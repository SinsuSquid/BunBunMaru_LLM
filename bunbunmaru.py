#!/usr/bin/env python3
"""
Bunbunmaru Newspaper (文々。新聞) - Hot-Wire Reporting Pipeline
Snaps photos, runs unhinged LLM tabloid analysis, and prints authentic broadsheets.
"""

import sys
import os
import json
import ollama
from press import render_newspaper

def main():
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
    dir_path = "gensokyo_directory.json"
    if os.path.exists(dir_path):
        try:
            with open(dir_path, "r", encoding="utf-8") as f:
                dossier = json.load(f)
            prompt_content += (
                "\n\n[MANDATORY GENSOKYO DOSSIER]\n"
                "Ground your eyewitnesses and classified ads using this directory of characters and sponsors:\n"
                + json.dumps(dossier, ensure_ascii=False)
            )
            print("📖 Loaded Gensokyo personnel & sponsor directory.")
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
