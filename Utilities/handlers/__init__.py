"""
Handler auto-registration.

Importing this package loads every handler module, which in turn
registers itself into registry.HANDLERS.  If a handler's optional
dependency is missing (e.g. Playwright for hotaudio), it's silently
skipped and a note is printed.
"""

# These always work (stdlib + requests/bs4 are required anyway)
from . import soundgasm  # noqa: F401
from . import whyp       # noqa: F401
from . import audiochan  # noqa: F401

# Hotaudio needs Playwright — skip gracefully if not installed
try:
    from . import hotaudio  # noqa: F401
    HAS_HOTAUDIO = True
except (ImportError, FileNotFoundError) as e:
    HAS_HOTAUDIO = False
    print(f"Note: hotaudio handler unavailable ({e})")
