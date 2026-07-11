#!/usr/bin/env python3
"""
Audio archiver — CLI entry point.

Usage:
    python -m Utilities.run

Requirements:
    pip install requests beautifulsoup4
    yt-dlp on PATH            (for whyp)
    gallery-dl on PATH         (for audiochan)
    pip install playwright     (for hotaudio, optional)
    playwright install chromium
"""
import importlib

from .yaml_store import ensure_yaml_exists, save_metadata_to_yaml, postprocess_playcount_in_yaml
from .registry import get_metadata

# ── Load handlers (each module's register() call fires on import) ─────
for _mod in ("soundgasm", "whyp", "audiochan"):
    importlib.import_module(f".handlers.{_mod}", __package__)

_HAS_HOTAUDIO = False
try:
    importlib.import_module(".handlers.hotaudio", __package__)
    _HAS_HOTAUDIO = True
except (ImportError, FileNotFoundError) as e:
    print(f"Note: hotaudio handler unavailable ({e})")


# ── URL list ──────────────────────────────────────────────────────────
# Plain strings use default settings.
# Tuples of (url, speed) override the playback speed for hotaudio.
#   speed only affects hotaudio; other handlers ignore it.

urls = [
    # soundgasm:
    # "https://soundgasm.net/u/sinthyasanguine/some-audio-title",

    # whyp:
    # "https://whyp.it/tracks/349458/f4m-skitty-wants-to-play-with-her-fav-toy-you-lubey-handjob-gentle-needy",

    # audiochan:
    "https://audiochan.com/a/nCj5FelUwcXTJOMrFL",

    # hotaudio (plain → default speed from HOTAUDIO_SPEED env or 2x):
    # "https://hotaudio.net/u/Lurkydip/some-audio",

    # hotaudio with explicit speed override:
    # ("https://hotaudio.net/u/VoidScreamsBack/vampire-ceo", 1.0),
]


# ── Main ──────────────────────────────────────────────────────────────
def main():
    ensure_yaml_exists()

    for entry in urls:
        if isinstance(entry, tuple):
            url, speed = entry[0], entry[1]
            get_metadata(url, speed=speed)
        else:
            get_metadata(entry)

    save_metadata_to_yaml()
    postprocess_playcount_in_yaml()

    # Clean up Playwright if it was used
    if _HAS_HOTAUDIO:
        from .handlers.hotaudio import close_browser
        close_browser()


if __name__ == "__main__":
    main()