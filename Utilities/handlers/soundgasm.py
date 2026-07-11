"""
Soundgasm handler, direct scraping via requests + BeautifulSoup.

Requirements: pip install requests beautifulsoup4
"""
import os
import re
import requests
from bs4 import BeautifulSoup

from ..config import resolve_author
from ..registry import audio_metadata, register


def get_metadata_soundgasm(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # == Username (from URL: soundgasm.net/u/{username}/{slug}) ====
    username = resolve_author(url.split("/u/")[1].split("/")[0])
    print(f"Extracted Username: {username}")

    # == Title =====================================================
    title_tag = soup.find("div", class_="jp-title", attrs={"aria-label": "title"})
    title = title_tag.decode_contents() if title_tag else "No title found"
    print(f"Extracted Raw Title: {title}")

    # == Description ===============================================
    desc_match = re.search(
        r'<p style="white-space: pre-wrap;">(.*?)<div class="jp-no-solution">',
        response.text, re.DOTALL,
    )
    if desc_match:
        description = desc_match.group(1)
        description = description.replace("</p>\r\n      </div>\r\n      ", "")
        print(f"Extracted Raw Description: {description[:100]}...")
    else:
        description = "No description found"
        print("Description not found.")

    # == Playcount (from the user's listing page) ==================
    base_url = "/".join(url.split("/")[:-1])
    base_response = requests.get(base_url)
    base_soup = BeautifulSoup(base_response.text, "html.parser")

    playcount = "No playcount found"
    audio_link_tag = base_soup.find("a", href=url)
    if audio_link_tag:
        span = audio_link_tag.find_next("span", class_="playCount")
        if span:
            m = re.search(r"Play Count:\s*(\d+)", span.text)
            if m:
                playcount = m.group(1)
    print(f"Extracted Playcount: {playcount}")

    # == Audio file ================================================
    audio_match = re.search(
        r'https://media\.soundgasm\.net/sounds/(.*?\.m4a)', response.text,
    )
    if not audio_match:
        print("Audio file not found.")
        return

    audio_filename = audio_match.group(1)
    print(f"Extracted Audio Filename: {audio_filename}")

    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)

    audio_url = f"https://media.soundgasm.net/sounds/{audio_filename}"
    audio_path = os.path.join(media_dir, audio_filename)
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)
    print(f"Downloaded audio file: {audio_path}")

    audio_metadata.append([username, title, description, playcount, audio_filename])


register("soundgasm", "soundgasm.net", get_metadata_soundgasm)