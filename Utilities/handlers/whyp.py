"""
Whyp handler — uses yt-dlp for Cloudflare-protected audio downloads.

Requirements: yt-dlp on PATH  (pip install yt-dlp)
"""
import json
import os
import re
import shutil
import subprocess

from ..config import resolve_author
from ..registry import audio_metadata, HANDLERS


def get_metadata_whyp(url, **_kwargs):
    if shutil.which("yt-dlp") is None:
        print("ERROR: yt-dlp not found on PATH.")
        print("  Install it:  pip install yt-dlp  (or grab the binary)")
        return

    # ── Metadata via yt-dlp JSON dump ─────────────────────────────
    print("Fetching metadata via yt-dlp...")
    result = subprocess.run(["yt-dlp", "-j", url], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp metadata extraction failed:\n{result.stderr}")
        return

    info = json.loads(result.stdout)

    username = resolve_author(info.get("uploader", "unknown_whyp_user"))
    title = info.get("title", "No title found")
    description = info.get("description") or "No description found"

    view_count = info.get("view_count")
    playcount = str(view_count) if view_count is not None else "No playcount found"

    # ── Audio filename from CDN URL ───────────────────────────────
    cdn_url = info.get("url", "")
    cdn_match = re.search(r'/([a-f0-9-]+\.\w+)\?', cdn_url)
    if cdn_match:
        audio_filename = cdn_match.group(1)
    else:
        track_id = str(info.get("id", "unknown"))
        ext = info.get("ext", "mp3")
        audio_filename = f"{track_id}.{ext}"
        print(f"Warning: couldn't extract CDN hash, falling back to {audio_filename}")

    print(f"Extracted Username: {username}")
    print(f"Extracted Title: {title}")
    print(f"Extracted Description: {description[:100]}...")
    print(f"Extracted Playcount: {playcount}")
    print(f"Extracted Audio Filename: {audio_filename}")

    # ── Download ──────────────────────────────────────────────────
    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)
    output_path = os.path.join(media_dir, audio_filename)

    if os.path.exists(output_path):
        print(f"File already exists: {output_path}. Skipping download.")
    else:
        print(f"Downloading audio to {media_dir}...")
        dl = subprocess.run(
            ["yt-dlp", "-o", output_path, url], capture_output=True, text=True,
        )
        if dl.returncode != 0:
            print(f"yt-dlp download failed:\n{dl.stderr}")
            return
        print(f"Downloaded audio file: {output_path}")

    audio_metadata.append([username, title, description, playcount, audio_filename])


HANDLERS["whyp"] = get_metadata_whyp
