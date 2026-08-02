"""
Soundgasm handler, direct scraping via requests + BeautifulSoup.

Requirements: pip install requests beautifulsoup4
"""
import os
import re
import requests
from bs4 import BeautifulSoup

from ..config import resolve_author, log_ok, log_warn, log_error
from ..registry import audio_metadata, register
from ..yaml_store import is_already_archived


def get_metadata_soundgasm(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # == Username (from URL: soundgasm.net/u/{username}/{slug}) ====
    username = resolve_author(url.split("/u/")[1].split("/")[0])
    log_ok(f"Username: {username}")

    # == Title =====================================================
    title_tag = soup.find("div", class_="jp-title", attrs={"aria-label": "title"})
    if title_tag:
        title = title_tag.decode_contents()
        log_ok(f"Title: {title}")
    else:
        title = "No title found"
        log_warn(f"Title not found for {url}")

    # == Description ===============================================
    desc_match = re.search(
        r'<p style="white-space: pre-wrap;">(.*?)<div class="jp-no-solution">',
        response.text, re.DOTALL,
    )
    if desc_match:
        description = desc_match.group(1)
        description = description.replace("</p>\r\n      </div>\r\n      ", "")
        log_ok(f"Description: {description[:80]}...")
    else:
        description = "No description found"
        log_warn(f"Description not found for {url}")

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

    if playcount == "No playcount found":
        log_warn(f"Playcount not found for {url}")
    else:
        log_ok(f"Playcount: {playcount}")

    # == Audio file ================================================
    audio_match = re.search(
        r'https://media\.soundgasm\.net/sounds/(.*?\.m4a)', response.text,
    )
    if not audio_match:
        log_error(f"Audio file not found for {url}")
        return

    audio_filename = audio_match.group(1)
    log_ok(f"Audio filename: {audio_filename}")

    if is_already_archived(username, audio_filename):
        log_ok(f"Already archived for {username}. Skipping download.")
        return

    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)

    audio_url = f"https://media.soundgasm.net/sounds/{audio_filename}"
    audio_path = os.path.join(media_dir, audio_filename)
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)
    log_ok(f"Downloaded: {audio_path}")

    audio_metadata.append([username, title, description, playcount, audio_filename])


register("soundgasm", "soundgasm.net", get_metadata_soundgasm)