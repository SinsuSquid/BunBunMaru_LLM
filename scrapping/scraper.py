#!/usr/bin/env python3
"""
Touhou Wiki Harvester (東方Wiki 採集機)
Scrapes character lore, abilities, personalities, and factions from Touhou Wiki (touhou.fandom.com)
to build an exhaustive Gensokyo directory for the Bunbunmaru Newspaper.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import concurrent.futures
from datetime import datetime

API_BASE = "https://touhou.fandom.com/api.php"
USER_AGENT = "BunbunmaruPress/2.0 (Tengu Newspaper Bureau; https://github.com/SinsuSquid/BunBunMaru_LLM)"

def clean_wiki_text(text: str) -> str:
    """Strip MediaWiki markup, templates, and HTML tags."""
    # Strip ruby-ja
    text = re.sub(r'\{\{ruby-ja\|([^\|\}]+)\|[^\}]*\}\}', r'\1', text)
    # Strip links [[target|label]] -> label, [[target]] -> target
    text = re.sub(r'\[\[(?:[^\|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Strip bold/italic quotes
    text = re.sub(r"'''+|''+", '', text)
    # Clean multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_infobox(wikitext: str) -> dict:
    """Extract key fields from character infobox."""
    info = {}
    match = re.search(r'\{\{Infobox/Character[\s\|](.*?)\n\}\}', wikitext, re.DOTALL | re.IGNORECASE)
    if not match:
        return info

    box_content = match.group(1)
    for line in box_content.splitlines():
        if line.startswith('|') and '=' in line:
            k, v = line[1:].split('=', 1)
            info[k.strip().lower()] = clean_wiki_text(v)
    return info

def extract_lead_summary(wikitext: str) -> str:
    """Extract the first meaningful descriptive summary paragraph."""
    # Split past infobox if present
    parts = re.split(r'\{\{Infobox/Character.*?\n\}\}', wikitext, flags=re.DOTALL | re.IGNORECASE)
    content = parts[-1] if len(parts) > 1 else wikitext

    for p in content.split('\n\n'):
        cleaned = clean_wiki_text(p)
        # Avoid section headers, nav boxes, or trivial one-liners
        if len(cleaned) > 60 and not cleaned.startswith('==') and not cleaned.startswith('{{'):
            return cleaned[:300] + ("..." if len(cleaned) > 300 else "")
    return ""

def generate_aya_attitude(name: str, species: str, personality_snippet: str) -> str:
    """Infer character's typical reaction to Aya Shameimaru's paparazzi reporting."""
    low_name = name.lower()
    low_species = species.lower()

    if "reimu" in low_name:
        return "Hostile and aggressive. Threatens to exterminate Aya unless she donates 500 Mon to the offering box."
    if "marisa" in low_name:
        return "Playfully guarded. Brags about solving the incident first and asks if Aya caught her good side."
    if "cirno" in low_name:
        return "Boastful and confused. Claims she is the strongest (⑨) and threatens to freeze the camera."
    if "sakuya" in low_name:
        return "Coldly polite. Subtle knife-twirling warning that prying near Lady Remilia is strictly forbidden."
    if "flandre" in low_name:
        return "Cheerfully terrifying. Asks if she can squeeze Aya's camera until it goes 'boom'."
    if "rinnosuke" in low_name:
        return "Pedantic lecture mode. Explains Outside World technology with 100% incorrect confidence."
    if "nitori" in low_name:
        return "Transactional. Denies all design defects and demands advertising discounts for Kappa gadgets."
    if "sanae" in low_name:
        return "Eager for PR coverage to promote Moriya Shrine, slipping in geeky Outside World mecha references."
    if "yuyuko" in low_name:
        return "Carefree and hungry. Completely ignores the questions and asks if the evidence is edible."
    if "fairy" in low_species:
        return "Easily startled or prone to childish pranks, complaining about being disturbed."
    if "vampire" in low_species or "oni" in low_species:
        return "Arrogantly amused. Treats the interview like an imperial audience while mocking Tengu rumors."
    if "god" in low_species:
        return "Condescending or commercially demanding. Insists on more faith offerings before answering."
    return "Guarded or irritated. Demands to know who authorized this intrusive Tengu surveillance."

def fetch_character_data(title: str) -> dict:
    """Fetch and parse a single character page from Touhou Wiki."""
    quoted = urllib.parse.quote(title.replace(' ', '_'))
    url = f"{API_BASE}?action=parse&page={quoted}&prop=wikitext&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            wikitext = data.get('parse', {}).get('wikitext', {}).get('*', '')

            infobox = parse_infobox(wikitext)
            species = infobox.get('species', 'Unknown')
            abilities = infobox.get('abilities', 'Unknown')
            occupation = infobox.get('occupation', infobox.get('location', 'Gensokyo Resident'))
            summary = extract_lead_summary(wikitext)
            attitude = generate_aya_attitude(title, species, summary)

            role_parts = [p for p in [species, occupation] if p and p != 'Unknown']
            role_desc = " / ".join(role_parts) if role_parts else "Gensokyo Resident"

            return {
                "name": title,
                "role": role_desc,
                "abilities": abilities if abilities != 'Unknown' else "Mystical Spell Cards",
                "personality": summary if summary else "A resident of Gensokyo caught in Aya's camera sights.",
                "attitude_towards_aya": attitude
            }
    except Exception as e:
        return None

def scrape_all_characters(max_workers: int = 10, limit: int = 200) -> list:
    """Scrape full character directory from Touhou Wiki Category:Characters."""
    print("🔍 Fetching character roster from Touhou Wiki Category:Characters...")
    list_url = f"{API_BASE}?action=query&list=categorymembers&cmtitle=Category:Characters&cmlimit={limit}&format=json"
    req = urllib.request.Request(list_url, headers={'User-Agent': USER_AGENT})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        members = data.get('query', {}).get('categorymembers', [])

    titles = [
        m['title'] for m in members
        if not m['title'].startswith(('Category:', 'Template:', 'Portal:'))
        and m['title'] not in ('Character List', 'List of Characters')
    ]

    print(f"📋 Found {len(titles)} characters. Scraping lore and profiles concurrently...")
    characters = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_title = {executor.submit(fetch_character_data, t): t for t in titles}
        for future in concurrent.futures.as_completed(future_to_title):
            res = future.result()
            if res:
                characters.append(res)
                print(f"  ✓ Harvested: {res['name']}")

    # Sort alphabetically
    characters.sort(key=lambda x: x['name'])
    return characters

def get_canonical_advertisers() -> list:
    """Canonical commercial sponsors & local businesses across Gensokyo."""
    return [
        {
            "sponsor": "Kourindou (香霖堂)",
            "proprietor": "Rinnosuke Morichika",
            "business_focus": "Outside World Salvage & High-Priced Relics",
            "typical_offerings": "Mysterious glass bricks (smartphones), silver calculation slabs (laptops), plastic cylinders with black carbonated liquid (Pepsi), mechanical clocks.",
            "ad_tone": "Scholarly, enigmatic, exorbitant pricing, mentions that proprietor may be reading in the back if shop appears deserted."
        },
        {
            "sponsor": "Kappa Heavy Industries (河童重工)",
            "proprietor": "Nitori Kawashiro & Engineering Guild",
            "business_focus": "Aquatic Machinery, Hydro-Jets & Experimental Weaponry",
            "typical_offerings": "Amphibious jetpacks, camouflage cloaks, waterproof drill-arms, automatic cucumber peelers.",
            "ad_tone": "Aggressive startup tech pitch, boasts low explosion odds (e.g. 'only 38% detonation risk!'), offers free bonus gadgets."
        },
        {
            "sponsor": "Hakurei Shrine (博麗神社)",
            "proprietor": "Reimu Hakurei",
            "business_focus": "Religious Services, Amulets & Desperate Faith Campaigns",
            "typical_offerings": "Exorcisms (50% off if paid in advance), lucky purification rod bromides, sacred spring water (tap water), donation box upgrades.",
            "ad_tone": "Aggressive guilt-tripping, blames current incidents on lack of donations, promises divine retribution to non-donors."
        },
        {
            "sponsor": "Moriya Shrine Faith & Tech Co. (守矢神社)",
            "proprietor": "Kanako Yasaka & Sanae Kochiya",
            "business_focus": "Modernized Faith, Nuclear Power & Mountain Tourism",
            "typical_offerings": "Ropeway aerial cable car tickets, miracle-infused energy drinks, clean geothermal power subscriptions, modern prayer apps.",
            "ad_tone": "Corporate corporate-speak, aggressive business expansion, guarantees tangible miracles with every contract."
        },
        {
            "sponsor": "Eientei Pharmacy (永遠亭 薬局)",
            "proprietor": "Eirin Yagokoro & Reisen Udongein Inaba",
            "business_focus": "Lunar Medicine & Miraculous Elixirs",
            "typical_offerings": "Ultra-vitality stamina draughts, sleepless night study drops, rabbit-ear soothing lotion, unapproved memory-erasing balms.",
            "ad_tone": "Clinical yet slightly menacing, reminds customers that side effects may include spiritual distortion or lunar madness."
        },
        {
            "sponsor": "Scarlet Devil Mansion Catering & Salon (紅魔館)",
            "proprietor": "Remilia Scarlet & Sakuya Izayoi",
            "business_focus": "Aristocratic Hospitality & Vampire Banquets",
            "typical_offerings": "Crimson black tea sets, private ballroom reservations, fine silverware appraisals, daytime parasol fittings.",
            "ad_tone": "Extravagant gothic aristocracy, subtly reminds patrons that uninvited gate-crashers will be disciplined by the gatekeeper."
        },
        {
            "sponsor": "Voile Secret Library (大図書館)",
            "proprietor": "Patchouli Knowledge & Koakuma",
            "business_focus": "Forbidden Grimoires & Arcane Research Rental",
            "typical_offerings": "Elemental spellcard scrolls, ancient demonology volumes, silent study cubicles.",
            "ad_tone": "Quiet, intellectual, strictly enforces late fees paid in elemental mana, warns that book thieves will be incinerated."
        },
        {
            "sponsor": "Geidontei Izakaya (鯢呑亭)",
            "proprietor": "Miyoi Okunoda",
            "business_focus": "Human Village Pub & Memory-Dulling Drinks",
            "typical_offerings": "Fresh river fish platters, mysterious sake that erases embarrassing memories, midnight snacks.",
            "ad_tone": "Warm village tavern hospitality, casual gossip, guarantees you won't remember how much you spent."
        },
        {
            "sponsor": "Suzunaan Book Rental (鈴奈庵)",
            "proprietor": "Kosuzu Motoori",
            "business_focus": "Demon Books & Foreign Literature Rental",
            "typical_offerings": "Cursed grimoires, foreign manga, ancient scrolls, translation glasses rentals.",
            "ad_tone": "Enthusiastic bookworm pitch, reminds customers not to unleash ancient evil spirits in the reading room."
        },
        {
            "sponsor": "Kirisame Magic Shop (霧雨魔法店)",
            "proprietor": "Marisa Kirisame",
            "business_focus": "High-Explosive Potions & Scrap Salvage",
            "typical_offerings": "Mini-Hakkero blast repairs, enchanted mushroom powders, high-speed broom waxing, suspicious magical junk.",
            "ad_tone": "Energetic, tomboyish pitch, promises maximum firepower and disclaims all liability for accidental forest fires."
        },
        {
            "sponsor": "Sanzu River Ferry & Cruise Co. (三途の川 渡し船)",
            "proprietor": "Komachi Onozuka",
            "business_focus": "Afterlife River Transit & Scenic Cruises",
            "typical_offerings": "One-way soul passage, scenic boat tours, currency exchange for ancient copper coins.",
            "ad_tone": "Lazy, cheerful ferryman pitch, offers discounts if passengers row themselves while the ferryman naps."
        },
        {
            "sponsor": "Ancient City Onsen & Magma Spa (旧都温泉街)",
            "proprietor": "Yuugi Hoshiguma & Underworld Oni",
            "business_focus": "Boiling Geothermal Hot Springs & Oni Taverns",
            "typical_offerings": "Natural magma sulfur baths, 100-proof demon sake casks, bare-knuckle arm wrestling matches.",
            "ad_tone": "Boisterous, high-energy Oni hospitality, boasts that no human has survived more than 10 minutes in the master bath."
        },
        {
            "sponsor": "Palace of Earth Spirits Pet Services (地霊殿)",
            "proprietor": "Satori Komeiji & Rin Kaenbyou",
            "business_focus": "Mind-Reading Therapy & Underworld Cartage",
            "typical_offerings": "Psychic counseling (no speaking necessary), wheelbarrow heavy haulage, hellfire heating fuel.",
            "ad_tone": "Eerily calm, reminds clients that Satori already knows your problem before you arrive."
        },
        {
            "sponsor": "Myouren Temple Zen Retreat (命蓮寺)",
            "proprietor": "Byakuren Hijiri",
            "business_focus": "Youkai-Human Harmony & Buddhist Meditation",
            "typical_offerings": "Motorcycle-blessed sutra scrolls, daily vegetarian temple meals, anger management for vengeful spirits.",
            "ad_tone": "Warm, compassionate, holy aura, welcoming all species while gently lecturing troublesome hermits."
        },
        {
            "sponsor": "Hakugyokurou Ghost Banquet & Catering (白玉楼)",
            "proprietor": "Yuyuko Saigyouji & Youmu Konpaku",
            "business_focus": "Netherworld Feasts & Phantom Landscaping",
            "typical_offerings": "All-you-can-eat ghost banquets, Roukanken precision hedge trimming, cherry blossom viewing spots.",
            "ad_tone": "Dreamy, whimsical, food-obsessed, Youmu frantically adds a disclaimer that Lady Yuyuko ate half the supplies."
        },
        {
            "sponsor": "Misty Lake Ice & Leisure Park (霧の湖)",
            "proprietor": "Cirno & Lake Fairies",
            "business_focus": "Sub-Zero Recreational Activities & Frog Preservation",
            "typical_offerings": "Instant flash-frozen frog popsicles, ice skating lessons by the Strongest, giant catfish warning whistles.",
            "ad_tone": "Childish, loud, boastful, claims that freezing things is the ultimate solution to all life problems."
        },
        {
            "sponsor": "Bamboo Forest Guide & Rescue Service (迷いの竹林)",
            "proprietor": "Fujiwara no Mokou & Tewi Inaba",
            "business_focus": "Mist Navigation & Emergency Fire Rescues",
            "typical_offerings": "Anti-pitfall bamboo walking sticks, immortal flame emergency signal flares, lucky rabbit-foot charms.",
            "ad_tone": "Tough, no-nonsense mercenary guide pitch, warning travelers that pitfall traps are 100% Tewi's fault."
        },
        {
            "sponsor": "Keiga Family Security & Protection (勁牙組)",
            "proprietor": "Saki Kurokoma",
            "business_focus": "Pegasus Bodyguard Services & Muscle Enforcement",
            "typical_offerings": "Yakuza debt collection, aerial strike security escorts, hoof-to-face conflict resolution.",
            "ad_tone": "Rowdy outlaw swagger, values raw physical strength above all, promises total protection to loyal clients."
        },
        {
            "sponsor": "Garden of the Sun Florist & Honey (太陽の畑)",
            "proprietor": "Yuuka Kazami",
            "business_focus": "Botanical Splendor & Pure Flower Honey",
            "typical_offerings": "Giant sunflower bouquets, sweet floral nectar, parasol shade rentals.",
            "ad_tone": "Polite, smiling, terrifyingly menacing, casually mentions that trespassers who step on the flowers become fertilizer."
        },
        {
            "sponsor": "Shining Needle Miniature Haberdashery (輝針城)",
            "proprietor": "Shinmyoumaru Sukuna",
            "business_focus": "Inchling Needlework & Miracle Appraisals",
            "typical_offerings": "Micro-scale embroidery, sewing needle fencing blades, Miracle Mallet wishes (terms and conditions apply).",
            "ad_tone": "Feisty, miniature revolutionary zeal, promises to overthrow oversized tyranny one stitch at a time."
        },
        {
            "sponsor": "Higan Court Moral Counseling (彼岸 裁判所)",
            "proprietor": "Eiki Shiki, Yamaxanadu",
            "business_focus": "Post-Mortem Sin Audits & Karma Consultation",
            "typical_offerings": "Cleanslate karma confessions, Rod of Remorse behavioral therapy, mirror of truth soul scans.",
            "ad_tone": "Stern, uncompromising moral lecture, reminds Gensokyo citizens that Hell is very real and very thorough."
        }
    ]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, "gensokyo_directory.json")
    characters = scrape_all_characters(max_workers=10, limit=200)
    advertisers = get_canonical_advertisers()

    dossier = {
        "_meta": {
            "source": "https://touhou.fandom.com/wiki/Touhou_Wiki",
            "harvested_at": datetime.now().isoformat(),
            "character_count": len(characters),
            "sponsor_count": len(advertisers),
            "description": "Comprehensive Gensokyo Directory harvested from Touhou Wiki for Bunbunmaru Newspaper LLM grounding."
        },
        "interviewees": characters,
        "advertisers": advertisers
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dossier, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 HARVEST COMPLETE! Saved {len(characters)} characters and {len(advertisers)} commercial sponsors to {output_file}!")

if __name__ == "__main__":
    main()
