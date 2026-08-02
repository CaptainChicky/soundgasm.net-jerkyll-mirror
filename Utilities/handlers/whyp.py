"""
Whyp handler — tries yt-dlp first, falls back to gallery-dl.

Requirements (at least one):
    yt-dlp on PATH      (pip install yt-dlp)
    gallery-dl on PATH   (pip install gallery-dl)
"""
import glob
import json
import os
import re
import shutil
import subprocess

from ..config import resolve_author, log_ok, log_warn, log_error
from ..registry import audio_metadata, register
from ..yaml_store import is_already_archived


# == Backend: yt-dlp ===================================================
def _ytdlp_metadata(url):
    """Try yt-dlp JSON dump.  Returns parsed info dict or None."""
    if shutil.which("yt-dlp") is None:
        return None
    print("  Trying yt-dlp...")
    result = subprocess.run(["yt-dlp", "-j", url],
                            capture_output=True, text=True)
    if result.returncode != 0:
        stderr_last = result.stderr.strip().splitlines(
        )[-1] if result.stderr.strip() else "unknown error"
        log_warn(f"yt-dlp failed: {stderr_last}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        log_warn("yt-dlp returned invalid JSON")
        return None


def _ytdlp_parse(info):
    """Normalize yt-dlp metadata into (username, title, desc, playcount, filename)."""
    username = info.get("uploader", "unknown_whyp_user")
    title = info.get("title", "No title found")
    description = info.get("description") or "No description found"

    view_count = info.get("view_count")
    playcount = str(
        view_count) if view_count is not None else "No playcount found"

    cdn_url = info.get("url", "")
    cdn_match = re.search(r'/([a-f0-9-]+\.\w+)\?', cdn_url)
    if cdn_match:
        audio_filename = cdn_match.group(1)
    else:
        track_id = str(info.get("id", "unknown"))
        ext = info.get("ext", "mp3")
        audio_filename = f"{track_id}.{ext}"

    return username, title, description, playcount, audio_filename


def _ytdlp_download(url, output_path):
    """Download via yt-dlp.  Returns True on success."""
    dl = subprocess.run(
        ["yt-dlp", "-o", output_path, url], capture_output=True, text=True,
    )
    if dl.returncode != 0:
        log_warn(f"yt-dlp download failed, trying gallery-dl...")
        return False
    return True


# == Backend: gallery-dl ===============================================
def _gallerydl_metadata(url):
    """Try gallery-dl JSON dump.  Returns parsed info dict or None."""
    if shutil.which("gallery-dl") is None:
        return None
    print("  Trying gallery-dl...")
    result = subprocess.run(
        ["gallery-dl", "-j", url], capture_output=True, text=True,
    )
    if result.returncode != 0:
        stderr_last = result.stderr.strip().splitlines(
        )[-1] if result.stderr.strip() else "unknown error"
        log_warn(f"gallery-dl failed: {stderr_last}")
        return None
    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError:
        log_warn("gallery-dl returned invalid JSON")
        return None

    # Type-3 preferred, type-2 fallback (same convention as audiochan)
    info = None
    for entry in entries:
        if not isinstance(entry, list) or len(entry) < 2:
            continue
        if entry[0] == 3 and len(entry) >= 3:
            info = entry[2]
            break
        elif entry[0] == 2 and info is None:
            info = entry[1]
    return info


def _gallerydl_parse(info):
    """Normalize gallery-dl metadata into (username, title, desc, playcount, filename)."""
    user_obj = info.get("user") or {}
    username = (user_obj.get("username")
                or user_obj.get("display_name")
                or info.get("uploader")
                or info.get("username")
                or "unknown_whyp_user")

    title = info.get("title") or "No title found"

    desc_raw = info.get("description")
    if isinstance(desc_raw, list):
        description = "\n".join(desc_raw)
    elif isinstance(desc_raw, str):
        description = desc_raw
    else:
        description = "No description found"

    listen_count = (info.get("valid_listens")
                    or info.get("view_count")
                    or info.get("listens"))
    playcount = str(
        listen_count) if listen_count is not None else "No playcount found"

    slug = info.get("filename") or info.get(
        "slug") or str(info.get("id", "unknown"))
    ext = info.get("extension") or "mp3"
    audio_filename = f"{slug}.{ext}"

    return username, title, description, playcount, audio_filename


def _gallerydl_download(url, username, audio_filename, output_path):
    """Download via gallery-dl.  Returns True on success."""
    slug = audio_filename.rsplit(".", 1)[0]
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
        log_error(f"gallery-dl download failed:\n{dl.stderr}")
        return False

    # Hunt for the file if gallery-dl ignored our output overrides
    if not os.path.exists(output_path):
        default_dir = os.path.join(".", "gallery-dl", "whyp", username)
        candidates = glob.glob(os.path.join(default_dir, "*"))
        if candidates:
            actual = max(candidates, key=os.path.getmtime)
            shutil.move(actual, output_path)
            log_ok(f"Moved {actual} -> {output_path}")
        else:
            log_error("Could not locate downloaded file.")
            print(f"  gallery-dl stdout:\n{dl.stdout}")
            return False

    return True


# == Main handler ======================================================
def get_metadata_whyp(url):
    # -- Metadata: try yt-dlp, fall back to gallery-dl -----------------
    backend = None
    info = _ytdlp_metadata(url)
    if info is not None:
        backend = "ytdlp"
        username, title, description, playcount, audio_filename = _ytdlp_parse(
            info)
    else:
        info = _gallerydl_metadata(url)
        if info is not None:
            backend = "gallerydl"
            username, title, description, playcount, audio_filename = _gallerydl_parse(
                info)
        else:
            log_error(
                "Both yt-dlp and gallery-dl failed. Cannot process this URL.")
            return

    username = resolve_author(username)

    # -- Log fields ----------------------------------------------------
    if username == "unknown_whyp_user":
        log_error("Username not found, falling back to 'unknown_whyp_user'")
    else:
        log_ok(f"Username: {username}")

    log_ok(f"Title: {title}") if title != "No title found" else log_warn(
        f"Title not found for {url}")
    log_ok(f"Description: {description[:80]}...") if description != "No description found" else log_warn(
        f"Description not found for {url}")
    log_ok(f"Playcount: {playcount}") if playcount != "No playcount found" else log_warn(
        f"Playcount not found for {url}")
    log_ok(f"Audio filename: {audio_filename}")
    log_ok(f"Backend: {backend}")

    # -- Archive check -------------------------------------------------
    if is_already_archived(username, audio_filename):
        log_ok(f"Already archived for {username}. Skipping download.")
        return

    # -- Download: use whichever backend worked, fall back if needed ----
    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)
    output_path = os.path.join(media_dir, audio_filename)

    print(f"  Downloading audio to {media_dir}...")

    ok = False
    if backend == "ytdlp":
        ok = _ytdlp_download(url, output_path)
    if not ok:
        ok = _gallerydl_download(url, username, audio_filename, output_path)
    if not ok:
        log_error("All download methods failed.")
        return

    log_ok(f"Downloaded: {output_path}")
    audio_metadata.append(
        [username, title, description, playcount, audio_filename])


register("whyp", "whyp.it", get_metadata_whyp)