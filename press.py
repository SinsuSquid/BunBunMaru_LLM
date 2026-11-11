"""
Bunbunmaru Printing Press (文々。新聞 印刷所)
Renders structured tabloid JSON into authentic Touhou 'Bohemian Archive in Japanese Red' broadsheet pages.
"""

import os
import sys
import json
import base64
import subprocess
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>文々。新聞 — {headline}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700;800;900&family=Zen+Old+Mincho:wght@700;900&family=Yuji+Boku&display=swap" rel="stylesheet">
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
    font-family: 'Shippori Mincho', 'Yu Mincho', 'Hiragino Mincho ProN', serif;
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
    min-height: 1450px;
    background-color: #f6f0e2;
    background-image: 
      radial-gradient(#e5dbcb 1px, transparent 1px),
      linear-gradient(to right, rgba(0,0,0,0.02) 1px, transparent 1px);
    background-size: 20px 20px, 4px 4px;
    border: 3px solid #3c342d;
    padding: 30px 35px 25px 35px;
    position: relative;
    overflow: hidden;
  }}

  /* Aged paper edge vignette */
  .newspaper::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    box-shadow: inset 0 0 60px rgba(120, 85, 45, 0.18);
  }}

  /* Top Masthead */
  .masthead {{
    border-bottom: 4px double #2c2520;
    padding-bottom: 12px;
    margin-bottom: 16px;
    display: grid;
    grid-template-columns: 200px 1fr 220px;
    align-items: center;
    gap: 15px;
  }}

  .masthead-meta-left {{
    font-size: 13px;
    line-height: 1.6;
    border-right: 1px solid #7c6f64;
    padding-right: 12px;
    color: #3f3630;
  }}

  .masthead-meta-left .issue-tag {{
    display: inline-block;
    background-color: #b5221d;
    color: #fff;
    font-weight: 800;
    padding: 2px 7px;
    font-size: 12px;
    letter-spacing: 2px;
    margin-bottom: 4px;
  }}

  .masthead-center {{
    text-align: center;
  }}

  .masthead-title {{
    font-family: 'Zen Old Mincho', 'Yuji Boku', serif;
    font-size: 64px;
    font-weight: 900;
    letter-spacing: 12px;
    color: #1a1512;
    text-shadow: 1px 1px 0 rgba(0,0,0,0.2);
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }}

  .tengu-seal {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    border: 3px solid #b5221d;
    color: #b5221d;
    font-family: 'Zen Old Mincho', serif;
    font-size: 26px;
    font-weight: 900;
    line-height: 1;
    border-radius: 4px;
    transform: rotate(-6deg);
    box-shadow: 0 0 0 1px rgba(181, 34, 29, 0.4);
    letter-spacing: 0;
  }}

  .masthead-subtitle {{
    font-size: 13px;
    letter-spacing: 6px;
    font-weight: 700;
    margin-top: 6px;
    color: #5a4e44;
  }}

  .masthead-meta-right {{
    font-size: 13px;
    line-height: 1.6;
    border-left: 1px solid #7c6f64;
    padding-left: 14px;
    color: #3f3630;
    text-align: right;
  }}

  .masthead-bar {{
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #3c342d;
    border-bottom: 2px solid #3c342d;
    padding: 4px 6px;
    font-size: 12px;
    font-weight: 700;
    color: #4a3e35;
    margin-bottom: 18px;
    letter-spacing: 1px;
  }}

  /* Headline Banner */
  .headline-section {{
    border-bottom: 3px solid #221c18;
    padding-bottom: 14px;
    margin-bottom: 16px;
  }}

  .subdeck-tag {{
    display: inline-block;
    color: #b5221d;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 4px;
  }}

  .main-headline {{
    font-family: 'Zen Old Mincho', serif;
    font-size: 38px;
    font-weight: 900;
    line-height: 1.25;
    color: #14100d;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
  }}

  .subdeck-text {{
    font-size: 19px;
    font-weight: 700;
    line-height: 1.4;
    color: #473930;
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
    padding-bottom: 18px;
    margin-bottom: 18px;
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
    box-shadow: 2px 3px 8px rgba(0,0,0,0.2);
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
    font-size: 12.5px;
    line-height: 1.55;
    color: #3b312a;
    background-color: #ede4d2;
    padding: 8px 10px;
    border-left: 3px solid #2c2520;
  }}

  .photo-credit {{
    font-weight: 800;
    color: #b5221d;
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
    padding: 12px 14px;
    font-size: 15px;
    line-height: 1.7;
    font-weight: 700;
    color: #1e1814;
    margin-bottom: 14px;
  }}

  .body-text {{
    column-count: 2;
    column-gap: 18px;
    column-rule: 1px dashed #aa9d8e;
    font-size: 13.5px;
    line-height: 1.85;
    text-align: justify;
    color: #26201b;
  }}

  .body-text p {{
    margin-bottom: 10px;
    text-indent: 1em;
  }}

  .body-text p:first-of-type::first-letter {{
    font-size: 26px;
    float: left;
    line-height: 1;
    font-weight: 900;
    color: #b5221d;
    padding-right: 5px;
    padding-top: 2px;
  }}

  /* Flash Bulletins Ticker */
  .bulletin-box {{
    margin-top: 14px;
    background-color: #2c2520;
    color: #f6f0e2;
    padding: 10px 14px;
    border-radius: 2px;
  }}

  .bulletin-header {{
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 900;
    color: #f1b347;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .bulletin-list {{
    list-style: none;
    font-size: 12px;
    line-height: 1.6;
  }}

  .bulletin-list li {{
    margin-bottom: 4px;
    padding-left: 14px;
    position: relative;
  }}

  .bulletin-list li::before {{
    content: "◆";
    position: absolute;
    left: 0;
    color: #b5221d;
    font-size: 10px;
  }}

  /* Lower Half: Interview Corner */
  .interview-section {{
    border: 2px solid #2c2520;
    background-color: #eee6d4;
    padding: 14px 18px;
    margin-bottom: 18px;
    position: relative;
  }}

  .interview-badge {{
    position: absolute;
    top: -12px;
    left: 20px;
    background-color: #2c2520;
    color: #f6f0e2;
    font-size: 12px;
    font-weight: 800;
    padding: 2px 12px;
    letter-spacing: 2px;
  }}

  .interview-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 4px;
  }}

  .quote-card {{
    background-color: #faf6ed;
    border: 1px solid #c9bda9;
    padding: 10px 12px;
    font-size: 13px;
    line-height: 1.65;
  }}

  .quote-speaker {{
    font-weight: 800;
    color: #b5221d;
    border-bottom: 1px solid #d8cdba;
    padding-bottom: 4px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }}

  .quote-speaker-role {{
    font-size: 11px;
    color: #6c5f54;
    font-weight: normal;
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
    font-size: 11px;
    line-height: 1.45;
    color: #42372f;
  }}

  .ad-title {{
    font-weight: 900;
    color: #1a1512;
    border-bottom: 1px dotted #887867;
    padding-bottom: 2px;
    margin-bottom: 4px;
    letter-spacing: 1px;
  }}

  /* Printing Footer */
  .newspaper-footer {{
    margin-top: 14px;
    padding-top: 8px;
    border-top: 1px solid #5a4e44;
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #6c5f54;
  }}
</style>
</head>
<body>

<div class="newspaper">

  <!-- Masthead -->
  <header class="masthead">
    <div class="masthead-meta-left">
      <span class="issue-tag">號外 / EXTRA</span><br>
      <strong>第百三十九季 (Season 139)</strong><br>
      妖怪の山 天狗総本山 報道局<br>
      天候: 局所的暴風雨注意報
    </div>
    <div class="masthead-center">
      <div class="masthead-title">
        <span>文々。新聞</span>
        <div class="tengu-seal">文</div>
      </div>
      <div class="masthead-subtitle">BUNBUNMARU SHINBUN — THE FASTEST SCOOP IN GENSOKYO</div>
    </div>
    <div class="masthead-right masthead-meta-right">
      <strong>主筆・写真: 射命丸 文</strong><br>
      定価: 百文 (交渉不可)<br>
      発行部数: 一千万部突破<br>
      真実より速さとセンセーション！
    </div>
  </header>

  <div class="masthead-bar">
    <span>【東方文花帖 號外緊急報道】</span>
    <span>GENSOKYO EMERGENCY BROADCAST SYSTEM</span>
    <span>記事捏造疑惑全面否定版</span>
  </div>

  <!-- Headlines -->
  <section class="headline-section">
    <span class="subdeck-tag">【特報・異変勃発！？】</span>
    <h1 class="main-headline">{headline}</h1>
    <div class="subdeck-text">{subdeck}</div>
  </section>

  <!-- Content Grid -->
  <div class="content-grid">
    <!-- Left Photo Column -->
    <div class="photo-column">
      <div class="photo-frame">
        <img src="{image_data_uri}" alt="現場決定的証拠写真">
      </div>
      <div class="photo-caption">
        <div class="photo-credit">▲ 撮影協力: 被害者各位 / 撮影: 射命丸 文</div>
        <strong>【現場証拠写真】</strong> 鴉天狗の超望遠魔眼レンズが捉えた決定的瞬間。外世界の未知なる遺物か、あるいは山奥で秘密裏に進む邪悪な禁呪実験の痕跡か。
      </div>
    </div>

    <!-- Right Article Column -->
    <div class="article-column">
      <div class="lead-box">
        {lead_paragraph}
      </div>

      <div class="body-text">
        <p>{body_paragraph}</p>
        <p>山麓の河童技術者集団はこの件について口を閉ざしており、博麗神社においては賽銭箱の重量不足に起因する神気低下の関与も噂されている。筆者が直ちに上空から追跡を試みたところ、奇妙な思念波が観測された。</p>
      </div>

      <div class="bulletin-box">
        <div class="bulletin-header">⚡ 文々。速報電波フラッシュ</div>
        <ul class="bulletin-list">
          {bulletins_html}
        </ul>
      </div>
    </div>
  </div>

  <!-- Interview Section -->
  <section class="interview-section">
    <div class="interview-badge">【関係者緊急直撃インタビュー】</div>
    <div class="interview-grid">
      {quotes_html}
    </div>
  </section>

  <!-- Bottom Classifieds -->
  <footer class="ads-section">
    <div class="ad-box">
      <div class="ad-title">◆ 香霖堂 (Kourindou) 新入荷</div>
      外世界より漂着した「ぎんいろの電子計算機(HP)」及び謎の炭酸飲料「ペプシ」。触ると冷たい。価格要応談。店主不在時は裏庭へ。
    </div>
    <div class="ad-box">
      <div class="ad-title">◆ 河童重工 水流ジェット推進器</div>
      玄武の沢にて大好評実験中！水陸両用・爆発確率わずか38%。今なら天狗除けの光学迷彩フードをもれなく進呈！
    </div>
    <div class="ad-box">
      <div class="ad-title">◆ 博麗神社 賽銭大募集中</div>
      最近の異変多発は皆様の信心不足が原因です。百文以上の喜捨で特製「安全祈願・お祓い棒ブロマイド」進呈中。
    </div>
  </footer>

  <div class="newspaper-footer">
    <span>発行所: 妖怪の山 文々。新聞社印刷工場</span>
    <span>※本紙に掲載された記事・写真の無断転載および抗議は風神少女の突風により一切受け付けません。</span>
    <span>文花帖 号外規格</span>
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
    """Render structured story JSON + image into authentic Bunbunmaru newspaper."""
    headline = json_data.get("headline", "GENSOKYO EMERGENCY SCOOP!")
    subdeck = json_data.get("subdeck", "Unverified Scandal Shakes the Human Village!")
    lead_paragraph = json_data.get("lead_paragraph", "")
    body_paragraph = json_data.get("body_paragraph", "")

    # Build quotes HTML
    quotes_list = json_data.get("eyewitness_quotes", [])
    quotes_html_parts = []
    for q in quotes_list:
        name = q.get("name", "通行人")
        quote = q.get("quote", "ノーコメントよ！")
        quotes_html_parts.append(f"""
        <div class="quote-card">
          <div class="quote-speaker">
            <span>{name}</span>
            <span class="quote-speaker-role">証言者</span>
          </div>
          <div class="quote-body">「{quote}」</div>
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

    # Use headless Chrome to take high-res screenshot and PDF if available
    if export_images:
        chrome_bin = "/usr/bin/google-chrome"
        if os.path.exists(chrome_bin):
            abs_html_path = os.path.abspath(output_html_path)
            abs_png_path = os.path.abspath(output_png_path)

            print("🖨️ Running Bunbunmaru Printing Press via Headless Chrome...")
            # Screenshot
            cmd_png = [
                chrome_bin,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1050,1480",
                f"--screenshot={abs_png_path}",
                f"file://{abs_html_path}",
            ]
            res_png = subprocess.run(cmd_png, capture_output=True, text=True)
            if res_png.returncode == 0 and os.path.exists(abs_png_path):
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
