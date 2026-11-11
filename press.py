"""
Bunbunmaru Printing Press (文々。新聞 印刷所)
Renders structured tabloid JSON into authentic Touhou 'Bohemian Archive in Japanese Red' broadsheet pages in English.
"""

import os
import sys
import json
import base64
import subprocess

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Bunbunmaru Newspaper — {headline}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;0,900;1,700&family=Cinzel:wght@700;900&family=Shippori+Mincho:wght@700;900&family=Zen+Old+Mincho:wght@900&display=swap" rel="stylesheet">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: #f6f0e2;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    font-family: 'Playfair Display', 'Georgia', serif;
    color: #1a1715;
    -webkit-print-color-adjust: exact;
  }}

  @page {{
    size: 1050px 1480px;
    margin: 0;
  }}

  /* The physical newspaper broadsheet sheet */
  .newspaper {{
    width: 1050px;
    background-color: #f6f0e2;
    background-image: 
      radial-gradient(#e5dbcb 1px, transparent 1px),
      linear-gradient(to right, rgba(0,0,0,0.02) 1px, transparent 1px);
    background-size: 20px 20px, 4px 4px;
    border: 3px solid #3c342d;
    padding: 28px 32px 22px 32px;
    position: relative;
    overflow: hidden;
  }}

  /* Aged paper edge vignette */
  .newspaper::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    box-shadow: inset 0 0 50px rgba(120, 85, 45, 0.16);
  }}

  /* Top Masthead */
  .masthead {{
    border-bottom: 4px double #2c2520;
    padding-bottom: 12px;
    margin-bottom: 14px;
    display: grid;
    grid-template-columns: 235px 1fr 235px;
    align-items: stretch;
    gap: 12px;
  }}

  .masthead-meta-left {{
    font-size: 11px;
    line-height: 1.55;
    border-right: 1px solid #7c6f64;
    padding-right: 12px;
    color: #3f3630;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  .masthead-meta-left .issue-tag {{
    display: inline-block;
    align-self: flex-start;
    background-color: #b5221d;
    color: #fff;
    font-weight: 900;
    padding: 2px 8px;
    font-size: 11px;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
  }}

  .masthead-center {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }}

  .masthead-title {{
    font-family: 'Zen Old Mincho', 'Shippori Mincho', serif;
    font-size: 58px;
    font-weight: 900;
    letter-spacing: 8px;
    color: #14100d;
    text-shadow: 1px 1px 0 rgba(0,0,0,0.25);
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-left: 8px;
  }}

  .tengu-seal {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border: 3px solid #b5221d;
    color: #b5221d;
    font-family: 'Zen Old Mincho', serif;
    font-size: 24px;
    font-weight: 900;
    line-height: 1;
    border-radius: 4px;
    transform: rotate(-6deg);
    box-shadow: 0 0 0 1px rgba(181, 34, 29, 0.4);
    letter-spacing: 0;
  }}

  .masthead-subtitle {{
    font-family: 'Cinzel', serif;
    font-size: 14px;
    letter-spacing: 4px;
    font-weight: 900;
    margin-top: 6px;
    color: #2c2520;
    text-transform: uppercase;
  }}

  .masthead-tagline {{
    font-family: 'Playfair Display', serif;
    font-size: 11px;
    letter-spacing: 2.5px;
    font-weight: 700;
    font-style: italic;
    margin-top: 2px;
    color: #655447;
    text-transform: uppercase;
  }}

  .masthead-meta-right {{
    font-size: 11px;
    line-height: 1.55;
    border-left: 1px solid #7c6f64;
    padding-left: 12px;
    color: #3f3630;
    text-align: right;
    letter-spacing: 0.5px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  .masthead-bar {{
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #3c342d;
    border-bottom: 2px solid #3c342d;
    padding: 4px 6px;
    font-family: 'Cinzel', serif;
    font-size: 11px;
    font-weight: 800;
    color: #4a3e35;
    margin-bottom: 16px;
    letter-spacing: 1px;
  }}

  /* Headline Banner */
  .headline-section {{
    border-bottom: 3px solid #221c18;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }}

  .subdeck-tag {{
    display: inline-block;
    color: #b5221d;
    font-family: 'Cinzel', serif;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 4px;
  }}

  .main-headline {{
    font-family: 'Playfair Display', serif;
    font-size: 34px;
    font-weight: 900;
    line-height: 1.2;
    color: #14100d;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}

  .subdeck-text {{
    font-size: 17.5px;
    font-weight: 700;
    line-height: 1.35;
    color: #3f3128;
    border-left: 4px solid #b5221d;
    padding-left: 12px;
    margin-top: 6px;
  }}

  /* Main Broadsheet Grid */
  .content-grid {{
    display: grid;
    grid-template-columns: 460px 1fr;
    gap: 22px;
    border-bottom: 2px solid #2c2520;
    padding-bottom: 16px;
    margin-bottom: 16px;
  }}

  /* Left: Photo Frame */
  .photo-column {{
    display: flex;
    flex-direction: column;
  }}

  .photo-frame {{
    border: 3px solid #2c2520;
    padding: 6px;
    background-color: #fff;
    box-shadow: 2px 3px 8px rgba(0,0,0,0.18);
  }}

  .photo-frame img {{
    width: 100%;
    height: 380px;
    object-fit: cover;
    display: block;
    filter: contrast(1.08) brightness(0.96) sepia(0.12);
    border: 1px solid #999;
  }}

  .photo-caption {{
    margin-top: 8px;
    font-size: 12px;
    line-height: 1.5;
    color: #3b312a;
    background-color: #ede4d2;
    padding: 8px 10px;
    border-left: 3px solid #2c2520;
  }}

  .photo-credit {{
    font-weight: 900;
    color: #b5221d;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
  }}

  /* Right: Multi-column Report */
  .article-column {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .lead-box {{
    background-color: rgba(181, 34, 29, 0.06);
    border: 1px solid #d8b8b6;
    border-left: 5px solid #b5221d;
    padding: 11px 13px;
    font-size: 14px;
    line-height: 1.6;
    font-weight: 700;
    color: #1e1814;
    margin-bottom: 12px;
  }}

  .body-text {{
    column-count: 2;
    column-gap: 16px;
    column-rule: 1px dashed #aa9d8e;
    font-size: 13px;
    line-height: 1.75;
    text-align: justify;
    color: #26201b;
  }}

  .body-text p {{
    margin-bottom: 8px;
    text-indent: 1.2em;
  }}

  .body-text p:first-of-type::first-letter {{
    font-size: 28px;
    float: left;
    line-height: 0.95;
    font-weight: 900;
    color: #b5221d;
    padding-right: 5px;
    padding-top: 2px;
    font-family: 'Playfair Display', serif;
  }}

  /* Flash Bulletins Ticker */
  .bulletin-box {{
    margin-top: 12px;
    background-color: #2c2520;
    color: #f6f0e2;
    padding: 9px 12px;
    border-radius: 2px;
  }}

  .bulletin-header {{
    font-family: 'Cinzel', serif;
    font-size: 11.5px;
    letter-spacing: 1.5px;
    font-weight: 900;
    color: #f1b347;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
  }}

  .bulletin-list {{
    list-style: none;
    font-size: 11.5px;
    line-height: 1.55;
  }}

  .bulletin-list li {{
    margin-bottom: 3px;
    padding-left: 14px;
    position: relative;
  }}

  .bulletin-list li::before {{
    content: "◆";
    position: absolute;
    left: 0;
    color: #b5221d;
    font-size: 9px;
  }}

  /* Lower Half: Interview Corner */
  .interview-section {{
    border: 2px solid #2c2520;
    background-color: #eee6d4;
    padding: 12px 16px;
    margin-bottom: 16px;
    position: relative;
  }}

  .interview-badge {{
    position: absolute;
    top: -11px;
    left: 20px;
    background-color: #2c2520;
    color: #f6f0e2;
    font-family: 'Cinzel', serif;
    font-size: 11px;
    font-weight: 900;
    padding: 2px 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }}

  .interview-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 4px;
  }}

  .quote-card {{
    background-color: #faf6ed;
    border: 1px solid #c9bda9;
    padding: 9px 12px;
    font-size: 12.5px;
    line-height: 1.55;
  }}

  .quote-speaker {{
    font-weight: 900;
    color: #b5221d;
    border-bottom: 1px solid #d8cdba;
    padding-bottom: 3px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
  }}

  .quote-speaker-role {{
    font-size: 10px;
    color: #6c5f54;
    font-weight: 700;
    text-transform: uppercase;
  }}

  .quote-body {{
    color: #2b231d;
    font-style: italic;
  }}

  /* Classified Ads at bottom */
  .ads-section {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    border-top: 2px solid #2c2520;
    padding-top: 10px;
  }}

  .ad-box {{
    border: 1px solid #9c8e7e;
    padding: 8px 10px;
    background-color: #ede4d1;
    font-size: 10.5px;
    line-height: 1.45;
    color: #42372f;
  }}

  .ad-title {{
    font-family: 'Cinzel', serif;
    font-weight: 900;
    color: #1a1512;
    border-bottom: 1px dotted #887867;
    padding-bottom: 2px;
    margin-bottom: 4px;
    letter-spacing: 1px;
    font-size: 11px;
  }}

  /* Printing Footer */
  .newspaper-footer {{
    margin-top: 12px;
    padding-top: 6px;
    border-top: 1px solid #5a4e44;
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: #6c5f54;
    letter-spacing: 0.5px;
  }}
</style>
</head>
<body>

<div class="newspaper">

  <!-- Masthead -->
  <header class="masthead">
    <div class="masthead-meta-left">
      <span class="issue-tag">SPECIAL EXTRA</span><br>
      <strong>SEASON 139 (GENSOKYO ERA)</strong><br>
      Youkai Mountain Bureau<br>
      Weather: Gale Advisory (Tengu Flight)
    </div>
    <div class="masthead-center">
      <div class="masthead-title">
        <span>文々。新聞</span>
        <div class="tengu-seal">文</div>
      </div>
      <div class="masthead-subtitle">BUNBUNMARU NEWSPAPER</div>
      <div class="masthead-tagline">FASTEST SCOOP IN GENSOKYO</div>
    </div>
    <div class="masthead-meta-right">
      <strong>Editor & Photo: Aya Shameimaru</strong><br>
      Price: 100 Mon (Non-negotiable)<br>
      Circulation: Over 10,000,000 Copies<br>
      Speed & Sensationalism Over Truth!
    </div>
  </header>

  <div class="masthead-bar">
    <span>【TOUHOU TABLOID EMERGENCY REPORT】</span>
    <span>GENSOKYO EMERGENCY BROADCAST WIRE</span>
    <span>ALL FABRICATION CLAIMS STRICTLY DENIED</span>
  </div>

  <!-- Headlines -->
  <section class="headline-section">
    <span class="subdeck-tag">【BREAKING: CATASTROPHIC INCIDENT DECLARED】</span>
    <h1 class="main-headline">{headline}</h1>
    <div class="subdeck-text">{subdeck}</div>
  </section>

  <!-- Content Grid -->
  <div class="content-grid">
    <!-- Left Photo Column -->
    <div class="photo-column">
      <div class="photo-frame">
        <img src="{image_data_uri}" alt="Decisive Crime Scene Evidence Photo">
      </div>
      <div class="photo-caption">
        <div class="photo-credit">▲ Shooting Cooperation: Unwitting Bystanders / Photo: Aya Shameimaru</div>
        <strong>[EXHIBIT A: CRIME SCENE EVIDENCE]</strong> Captured decisively through the Crow Tengu's ultra-telephoto clairvoyance lens. Is it a forbidden relic from the Outside World, or unmistakable traces of dark spellcard sorcery brewing in the mountains?
      </div>
    </div>

    <!-- Right Article Column -->
    <div class="article-column">
      <div class="lead-box">
        {lead_paragraph}
      </div>

      <div class="body-text">
        <p>{body_paragraph}</p>
        <p>The Kappa engineering collective at the foot of the mountain has strictly refused to comment on this development, while whispers around the Hakurei Shrine suggest an alarming drop in spiritual wards directly tied to chronic donation deficits. Crow scouts attempting high-altitude reconnaissance reported intense, chaotic psychic resonances echoing across the vicinity.</p>
      </div>

      <div class="bulletin-box">
        <div class="bulletin-header">⚡ Bunbunmaru Flash Rumor Wire</div>
        <ul class="bulletin-list">
          {bulletins_html}
        </ul>
      </div>
    </div>
  </div>

  <!-- Interview Section -->
  <section class="interview-section">
    <div class="interview-badge">【Emergency Eyewitness Ambush Interview】</div>
    <div class="interview-grid">
      {quotes_html}
    </div>
  </section>

  <!-- Bottom Classifieds -->
  <footer class="ads-section">
    <div class="ad-box">
      <div class="ad-title">◆ Kourindou Curiosities: New Arrival</div>
      Salvaged from the Outside World: A sleek 'Silver Calculating Machine (HP)' and a mysterious bottled elixir labeled 'Pepsi'. Cold to the touch. Inquire within; if shopkeeper is absent, wait out back.
    </div>
    <div class="ad-box">
      <div class="ad-title">◆ Kappa Heavy Industries: Hydro-Jets</div>
      Now undergoing explosive field trials at Genbu Ravine! Fully amphibious design with a detonation risk of only 38%! Every preorder includes a free Tengu-deflecting optical cloak hood!
    </div>
    <div class="ad-box">
      <div class="ad-title">◆ Hakurei Shrine: Urgent Faith Appeal</div>
      Recent escalations of bizarre incidents are directly caused by your lack of shrine donations! Offerings of 100 Mon or more receive an exclusive 'Purification Rod Blessing Bromide'!
    </div>
  </footer>

  <div class="newspaper-footer">
    <span>Published by: Youkai Mountain Bunbunmaru Printing Press</span>
    <span>* All rights reserved. Complaints, retractions, and slander lawsuits will be blown away by local gale gusts.</span>
    <span>Bohemian Archive Spec</span>
  </div>

</div>

</body>
</html>
"""

def image_to_base64_data_uri(image_path: str) -> str:
    """Convert local image into self-contained base64 data URI."""
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

def render_newspaper(
    json_data: dict,
    image_path: str,
    output_html_path: str = "bunbunmaru_newspaper.html",
    output_png_path: str = "bunbunmaru_newspaper.png",
    export_images: bool = True
):
    """Render structured story JSON + image into authentic Bunbunmaru newspaper in English."""
    headline = json_data.get("headline", "GENSOKYO EMERGENCY SCOOP!")
    subdeck = json_data.get("subdeck", "Unverified Scandal Shakes the Human Village!")
    lead_paragraph = json_data.get("lead_paragraph", "")
    body_paragraph = json_data.get("body_paragraph", "")

    # Build quotes HTML
    quotes_list = json_data.get("eyewitness_quotes", [])
    quotes_html_parts = []
    for q in quotes_list:
        name = q.get("name", "Bystander")
        quote = q.get("quote", "No comment! Get lost!")
        quotes_html_parts.append(f"""
        <div class="quote-card">
          <div class="quote-speaker">
            <span>{name}</span>
            <span class="quote-speaker-role">Eyewitness</span>
          </div>
          <div class="quote-body">"{quote}"</div>
        </div>
        """)
    quotes_html = "\n".join(quotes_html_parts)

    # Build bulletins HTML
    bulletins_list = json_data.get("bulletins", [])
    bulletins_html_parts = []
    for b in bulletins_list:
        bulletins_html_parts.append(f"<li>{b}</li>")
    bulletins_html = "\n".join(bulletins_html_parts)

    # Convert photo to Data URI for fully standalone HTML
    image_data_uri = image_to_base64_data_uri(image_path)

    # Populate HTML
    html_content = HTML_TEMPLATE.format(
        headline=headline,
        subdeck=subdeck,
        lead_paragraph=lead_paragraph,
        body_paragraph=body_paragraph,
        image_data_uri=image_data_uri,
        quotes_html=quotes_html,
        bulletins_html=bulletins_html,
    )

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Generated Newspaper HTML: {output_html_path}")

    # Use headless Chrome to take high-res screenshot
    if export_images:
        chrome_bin = "/usr/bin/google-chrome"
        if os.path.exists(chrome_bin):
            abs_html_path = os.path.abspath(output_html_path)
            abs_png_path = os.path.abspath(output_png_path)

            print("🖨️ Running Bunbunmaru Printing Press via Headless Chrome...")
            cmd_png = [
                chrome_bin,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1050,1600",
                f"--screenshot={abs_png_path}",
                f"file://{abs_html_path}",
            ]
            res_png = subprocess.run(cmd_png, capture_output=True, text=True)
            if res_png.returncode == 0 and os.path.exists(abs_png_path):
                # Auto-crop cleanly to the exact bottom border of the newspaper
                try:
                    from PIL import Image
                    import numpy as np
                    im = Image.open(abs_png_path)
                    arr = np.array(im)
                    # Find bottom border: dark row of 3px solid #3c342d border
                    for y in range(im.height - 1, 100, -1):
                        row = arr[y, 100:950, :3]
                        if (row < 80).all(axis=-1).mean() > 0.7:
                            cropped = im.crop((0, 0, 1050, y + 1))
                            cropped.save(abs_png_path)
                            print(f"📐 Cleanly aligned & cropped newspaper to: {cropped.size[0]}x{cropped.size[1]}px")
                            break
                except Exception as e:
                    pass
                print(f"📸 Exported Front-Page PNG: {abs_png_path}")
            else:
                print(f"⚠️ PNG export issue: {res_png.stderr}")

if __name__ == "__main__":
    # Test sample with our actual Blahaj run
    sample_json = {
        "headline": "BLUE HORROR OF GENSOYKO: THE OCEAN SHRINE HAS INVADED YOUR PRIVATE HOME!",
        "subdeck": "A MYSTERIOUS Y-SHIRT BEING REVEALS A FULL-BRED SHARK BEHEMOTH IN SILVER TECH GEAR!",
        "lead_paragraph": "Breaking news straight from the Hakai Domain! What started as a simple, routine work session has rapidly spiralled into a catastrophe of the highest order. Witnesses describe a figure wearing the sacred purple fabric adorned with mystical Y-character runes emerging from... well, emerging as the Great Blue Gengorobo spirit. They are actively engaging with silicon-based technology, and the local Pepsi supply has reportedly been tainted.",
        "body_paragraph": "The evidence of the shark spirit manifesting is undeniable. The shark plushie over the skull is no longer a mere garment but a cursed spiritual barrier channeling deep-sea mana directly into the laptop. The dark soda bottle placed adjacent to the HP unit is confirmed as an ancient vessel of Pessimistic Essence, necessary for casting spells of water destruction in the age of modern computing.",
        "eyewitness_quotes": [
            {
                "name": "Cirno (Self-Proclaimed Strongest)",
                "quote": "Well, it’s definitely shark-shaped! But I hate you guys being here in the house."
            },
            {
                "name": "Yuki Nana (Allegedly)",
                "quote": "My 'Y' symbol shirt is glowing too bright... what happened to my dignity? It looks like a real monster wearing me. Stop it. Just stop typing the spell, you idiot."
            }
        ],
        "bulletins": [
            "FLOOR SECRECTION CONFIRMED: The shark spirit is sinking the entire floor.",
            "Pepsi Max Incident: Witnesses claim it smells like the ocean when opened.",
            "The laptop is now singing in a language that sounds like a whale choking on glass."
        ]
    }

    image_path = "blahaj.jpg"
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        image_path = sys.argv[1]

    render_newspaper(sample_json, image_path)
