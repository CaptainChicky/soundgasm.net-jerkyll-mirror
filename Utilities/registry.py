"""
Handler registry and URL dispatcher.

Shared state (audio_metadata, HANDLERS) lives here so every handler
can append results without circular imports.
"""

# == Shared mutable state ==============================================
audio_metadata = []   # [[username, title, description, playcount, filename], ...]
HANDLERS = {}         # {"soundgasm": fn, "whyp": fn, ...}

# == Site detection ====================================================
_SITE_RULES = [
    ("soundgasm.net", "soundgasm"),
    ("whyp.it",       "whyp"),
    ("hotaudio",      "hotaudio"),
    ("audiochan",     "audiochan"),
]


def detect_site(url):
    """Return a site key string, or None if the URL isn't recognised."""
    for fragment, site in _SITE_RULES:
        if fragment in url:
            return site
    return None


# == Dispatcher ========================================================
def get_metadata(url, **kwargs):
    """
    Route a URL to the correct handler.

    Extra kwargs (e.g. speed=1.5) are forwarded only to handlers that
    accept them (currently just hotaudio).
    """
    site = detect_site(url)
    if site is None:
        print(f"Unsupported site: {url}")
        return

    print(f"\n{'=' * 60}")
    print(f"[{site}] {url}")
    print(f"{'=' * 60}")

    handler = HANDLERS.get(site)
    if handler is None:
        print(f"No handler registered for site: {site}")
        return

    handler(url, **kwargs)
