"""
Handler registry and URL dispatcher.

Shared state (audio_metadata, handlers) lives here so every handler
can append results without circular imports.
"""

# == Shared mutable state ==============================================
audio_metadata = []   # [[username, title, description, playcount, filename], ...]
_HANDLERS = {}        # {"soundgasm": handler_fn, ...}
_URL_PATTERNS = {}    # {"soundgasm": "soundgasm.net", ...}


# == Registration ======================================================
def register(site_key, url_fragment, handler_fn):
    """
    Register a handler for a site.  Called once per handler module at
    import time.  Adding a new site = one new file with one register()
    call, nothing else to touch.
    """
    _HANDLERS[site_key] = handler_fn
    _URL_PATTERNS[site_key] = url_fragment


def detect_site(url):
    """Return a site key string, or None if the URL isn't recognised."""
    for site_key, fragment in _URL_PATTERNS.items():
        if fragment in url:
            return site_key
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

    handler = _HANDLERS.get(site)
    if handler is None:
        print(f"No handler registered for site: {site}")
        return

    handler(url, **kwargs)
