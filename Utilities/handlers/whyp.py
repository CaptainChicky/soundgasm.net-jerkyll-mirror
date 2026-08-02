"""
Whyp handler, uses yt-dlp for Cloudflare-protected audio downloads.

Requirements: yt-dlp on PATH  (pip install yt-dlp)
"""
import json
import os
import re
import shutil
import subprocess

from ..config import resolve_author, log_ok, log_warn, log_error
from ..registry import audio_metadata, register
from ..yaml_store import is_already_archived


def get_metadata_whyp(url):
    if shutil.which("yt-dlp") is None:
        log_error("yt-dlp not found on PATH.")
        print("  Install it:  pip install yt-dlp  (or grab the binary)")
        return

    # == Metadata via yt-dlp JSON dump =============================
    print("  Fetching metadata via yt-dlp...")
    result = subprocess.run(["yt-dlp", "-j", url], capture_output=True, text=True)
    if result.returncode != 0:
        log_error(f"yt-dlp metadata extraction failed:\n{result.stderr}")
        return

    info = json.loads(result.stdout)

    username = resolve_author(info.get("uploader", "unknown_whyp_user"))
    if username == "unknown_whyp_user":
        log_error(f"Username not found, falling back to 'unknown_whyp_user'")
    else:
        log_ok(f"Username: {username}")

    title = info.get("title", "No title found")
    if title == "No title found":
        log_warn(f"Title not found for {url}")
    else:
        log_ok(f"Title: {title}")

    description = info.get("description") or "No description found"
    if description == "No description found":
        log_warn(f"Description not found for {url}")
    else:
        log_ok(f"Description: {description[:80]}...")

    view_count = info.get("view_count")
    if view_count is not None:
        playcount = str(view_count)
        log_ok(f"Playcount: {playcount}")
    else:
        playcount = "No playcount found"
        log_warn(f"Playcount not found for {url}")

    # == Audio filename from CDN URL ===============================
    cdn_url = info.get("url", "")
    cdn_match = re.search(r'/([a-f0-9-]+\.\w+)\?', cdn_url)
    if cdn_match:
        audio_filename = cdn_match.group(1)
        log_ok(f"Audio filename: {audio_filename}")
    else:
        track_id = str(info.get("id", "unknown"))
        ext = info.get("ext", "mp3")
        audio_filename = f"{track_id}.{ext}"
        log_warn(f"Couldn't extract CDN hash, falling back to {audio_filename}")

    # == Download ==================================================
    if is_already_archived(username, audio_filename):
        log_ok(f"Already archived for {username}. Skipping download.")
        return

    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)
    output_path = os.path.join(media_dir, audio_filename)

    print(f"  Downloading audio to {media_dir}...")
    dl = subprocess.run(
        ["yt-dlp", "-o", output_path, url], capture_output=True, text=True,
    )
    if dl.returncode != 0:
        log_error(f"yt-dlp download failed:\n{dl.stderr}")
        return
    log_ok(f"Downloaded: {output_path}")

    audio_metadata.append([username, title, description, playcount, audio_filename])


register("whyp", "whyp.it", get_metadata_whyp)