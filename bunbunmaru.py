#!/usr/bin/env python3
"""
Bunbunmaru Newspaper (文々。新聞) - Hot-Wire Reporting Pipeline
Snaps photos, runs unhinged LLM tabloid analysis, and prints authentic broadsheets.
"""

import sys
import os
import json
import ollama
from pressing import render_newspaper

def main():
    image_path = "assets/blahaj.jpg"
    if not os.path.exists(image_path) and os.path.exists("blahaj.jpg"):
        image_path = "blahaj.jpg"

    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            image_path = sys.argv[1]
        else:
            print(f"❌ Error: Image file '{sys.argv[1]}' not found!")
            sys.exit(1)

    print(f"📸 Scooping evidence from: {image_path}")
    print("🪶 Alerting Aya Shameimaru at the Bunbunmaru Printing Press...")

    # Load Gensokyo Directory Dossier if present
    prompt_content = "Break this story right now!"
    dir_path = "data/gensokyo_directory.json"
    if not os.path.exists(dir_path) and os.path.exists("gensokyo_directory.json"):
        dir_path = "gensokyo_directory.json"
    if os.path.exists(dir_path):
        try:
            import random
            with open(dir_path, "r", encoding="utf-8") as f:
                dossier = json.load(f)
            all_chars = dossier.get("interviewees", [])
            sponsors = dossier.get("advertisers", [])

            # Core iconic cast + diverse random rotation
            key_names = {
                "Reimu Hakurei", "Marisa Kirisame", "Cirno", "Sakuya Izayoi",
                "Remilia Scarlet", "Flandre Scarlet", "Nitori Kawashiro", "Sanae Kochiya",
                "Rinnosuke Morichika", "Yuyuko Saigyouji", "Youmu Konpaku", "Reisen Udongein Inaba"
            }
            featured = [c for c in all_chars if c["name"] in key_names]
            remaining = [c for c in all_chars if c["name"] not in key_names]
            if remaining:
                featured.extend(random.sample(remaining, min(8, len(remaining))))

            compact_dossier = {
                "featured_residents_for_interview": [
                    {
                        "name": c["name"],
                        "role": c.get("role", "Resident"),
                        "attitude_towards_aya": c.get("attitude_towards_aya", "Irritated by prying")
                    }
                    for c in featured
                ],
                "commercial_sponsors_for_ads": sponsors
            }
            prompt_content += (
                "\n\n[GENSOKYO DOSSIER]\n"
                "Ground your eyewitness quotes in the personalities above, and generate 3 classified ads for sponsors:\n"
                + json.dumps(compact_dossier, ensure_ascii=False)
            )
            print(f"📖 Loaded Gensokyo directory ({len(all_chars)} characters, {len(sponsors)} sponsors).")
        except Exception as e:
            print(f"⚠️ Could not load directory: {e}")

    response = ollama.chat(
        model="bunbunmaru",
        format="json",
        messages=[
            {
                "role": "user",
                "content": prompt_content,
                "images": [image_path],
            }
        ],
    )

    raw_content = response["message"]["content"]
    try:
        story_data = json.loads(raw_content)
    except json.JSONDecodeError:
        print("⚠️ Warning: Model did not return clean JSON. Attempting fallback parse...")
        print(raw_content)
        return

    print("\n" + "=" * 70)
    print(f"📢 HEADLINE: {story_data.get('headline')}")
    print(f"💥 SUBDECK:  {story_data.get('subdeck')}")
    print("=" * 70 + "\n")

    # Render authentic Bohemian Archive in Japanese Red broadsheet
    render_newspaper(story_data, image_path)
    print("\n🎉 The evening edition has finished printing! Read all about it, Gensokyo!")

if __name__ == "__main__":
    main()
