#!/usr/bin/env python3
"""
Audio archiver (CLI entrypoint)

Usage:
    python -m Utilities.run
    or just run directly from VSC for instance

Requirements:
    pip install requests beautifulsoup4 (for soundgasm and other sites)
    yt-dlp on PATH               (for whyp, could've used gallery-dl but yt-dlp is cleaner)
    gallery-dl on PATH           (for audiochan)
    pip install playwright       (for hotaudio)
    playwright install chromium  (for hotaudio)
"""
import importlib

from .yaml_store import ensure_yaml_exists, save_metadata_to_yaml, postprocess_playcount_in_yaml
from .registry import get_metadata

# == Load handlers (each module's register() call fires on import) =====
for _mod in ("soundgasm", "whyp", "audiochan"):
    importlib.import_module(f".handlers.{_mod}", __package__)

_HAS_HOTAUDIO = False
try:
    importlib.import_module(".handlers.hotaudio", __package__)
    _HAS_HOTAUDIO = True
except (ImportError, FileNotFoundError) as e:
    from .config import log_warn
    log_warn(f"hotaudio handler unavailable ({e})")


# == URL list ==========================================================
# Plain strings use default settings.
# Tuples of (url, speed) override the playback speed for hotaudio.
#   speed only affects hotaudio; other handlers ignore it.

urls = [
    # soundgasm:
    # "https://soundgasm.net/u/IvyWilde/The-Teachers-Pet",

    # whyp:
    # "https://whyp.it/tracks/349458/f4m-skitty-wants-to-play-with-her-fav-toy-you-lubey-handjob-gentle-needy",

    # audiochan:
    # "https://audiochan.com/a/nCj5FelUwcXTJOMrFL",

    # hotaudio (plain -> default speed from HOTAUDIO_SPEED env or 2x):
    # "https://hotaudio.net/u/Financial-Dig4285/Mommy-is-going-to-ride-you-You-have-to-be-quiet",

    # hotaudio with explicit speed override:
    # ("https://hotaudio.net/u/SweetnEvil86/Your-Former-Teacher-Rewards-You-For-Being-a-Good-Boy", 1.0),

    "https://hotaudio.net/u/Financial-Dig4285/Blowjob-gift-card-from-your-friends-girlfriend"
]


# == Main ==============================================================
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