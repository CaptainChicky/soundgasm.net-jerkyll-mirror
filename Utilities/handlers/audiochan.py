"""
Audiochan handler — uses gallery-dl for metadata extraction and downloads.

Requirements: gallery-dl on PATH  (pip install gallery-dl)
"""
import glob
import json
import os
import re
import shutil
import subprocess

from ..config import resolve_author
from ..registry import audio_metadata, register


def get_metadata_audiochan(url, **_kwargs):
    if shutil.which("gallery-dl") is None:
        print("ERROR: gallery-dl not found on PATH.")
        print("  Install it:  pip install gallery-dl  (or grab the binary)")
        return

    # ── Metadata via gallery-dl JSON dump ─────────────────────────
    print("Fetching metadata via gallery-dl...")
    result = subprocess.run(
        ["gallery-dl", "-j", url], capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"gallery-dl metadata extraction failed:\n{result.stderr}")
        return

    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Could not parse gallery-dl JSON output: {e}")
        print(f"Raw output:\n{result.stdout[:500]}")
        return

    # Find the best metadata entry (type-3 preferred, type-2 fallback)
    info = None
    for entry in entries:
        if not isinstance(entry, list) or len(entry) < 2:
            continue
        if entry[0] == 3 and len(entry) >= 3:
            info = entry[2]
            break
        elif entry[0] == 2 and info is None:
            info = entry[1]

    if info is None:
        print("Could not extract metadata from gallery-dl output.")
        print(f"Raw output:\n{result.stdout[:500]}")
        return

    # ── Parse fields ──────────────────────────────────────────────
    user_obj = info.get("user") or {}
    username = user_obj.get("username") or user_obj.get("display_name") or "unknown_audiochan_user"
    username = resolve_author(username)

    title = info.get("title") or "No title found"

    desc_raw = info.get("description")
    if isinstance(desc_raw, list):
        description = "\n".join(desc_raw)
    elif isinstance(desc_raw, str):
        description = desc_raw
    else:
        description = "No description found"

    listen_count = info.get("valid_listens")
    playcount = str(listen_count) if listen_count is not None else "No playcount found"

    slug = info.get("slug") or str(info.get("id", "unknown"))
    ext = info.get("extension") or "mp3"
    audio_filename = f"{slug}.{ext}"

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
            [
                "gallery-dl",
                "-d", ".",
                "-o", f'directory=["media", "{username}"]',
                "-o", f"filename={slug}.{{extension}}",
                url,
            ],
            capture_output=True, text=True,
        )
        if dl.returncode != 0:
            print(f"gallery-dl download failed:\n{dl.stderr}")
            return

        # Hunt for the file if gallery-dl ignored our output overrides
        if not os.path.exists(output_path):
            default_dir = os.path.join(".", "gallery-dl", "audiochan", username)
            candidates = glob.glob(os.path.join(default_dir, "*"))
            if candidates:
                actual = max(candidates, key=os.path.getmtime)
                shutil.move(actual, output_path)
                print(f"Moved {actual} -> {output_path}")
            else:
                print("Warning: could not locate downloaded file.")
                print(f"gallery-dl stdout:\n{dl.stdout}")
                return

        print(f"Downloaded audio file: {output_path}")

    audio_metadata.append([username, title, description, playcount, audio_filename])


register("audiochan", "audiochan", get_metadata_audiochan)
