"""
Hotaudio handler, uses Playwright to drive a real browser, inject MSE
hooks, and capture decrypted audio + metadata.

Requirements:
    pip install playwright
    playwright install chromium

The handler registers itself only if Playwright is importable, so the
rest of the pipeline still works without it.

Notes:
    - Uses a persistent browser profile (~/.hotaudio_profile) so the site
      sees a consistent fingerprint across runs.  Delete it to start fresh.
    - Plays at 2x by default.  Set HOTAUDIO_SPEED=1 env var if you want
      bit-perfect captures (2x is safe, >2x causes cipher drift).
    - hotaudio_inject.js must sit next to this file (same directory).
"""
import os
import re
from pathlib import Path

from ..config import resolve_author
from ..registry import audio_metadata, register

# == Constants =========================================================
INJECT_JS = (Path(__file__).parent / "hotaudio_inject.js").read_text()
PROFILE_DIR = os.path.expanduser("~/.hotaudio_profile")
PLAYBACK_SPEED = float(os.environ.get("HOTAUDIO_SPEED", "2"))

# == Lazy Playwright state =============================================
_pw = None
_browser = None


def _get_browser():
    """Launch (or reuse) a persistent Chromium context."""
    global _pw, _browser
    if _browser is not None:
        return _browser

    from playwright.sync_api import sync_playwright
    _pw = sync_playwright().start()

    _browser = _pw.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        ignore_default_args=["--enable-automation"],
        locale="en-US",
        viewport={"width": 1280, "height": 720},
    )

    _browser.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
    """)
    return _browser


def close_browser():
    """Call at the end of the script to cleanly shut down Playwright."""
    global _pw, _browser
    if _browser:
        _browser.close()
        _browser = None
    if _pw:
        _pw.stop()
        _pw = None


# == Main handler ======================================================
def get_metadata_hotaudio(url, speed=None):
    """
    Navigate to a hotaudio URL, hook MSE, play the audio at the
    requested speed, wait for it to finish, then extract metadata +
    decrypted audio bytes.

    Args:
        url:   hotaudio post URL (e.g. https://hotaudio.net/u/User/slug)
        speed: playback speed override (0.5-2.0).  None = HOTAUDIO_SPEED
               env var (default 2).  Stay <=2 to avoid cipher drift.
    """
    playback_speed = speed if speed is not None else PLAYBACK_SPEED
    playback_speed = max(0.5, min(playback_speed, 2.0))
    browser = _get_browser()
    page = browser.new_page()

    try:
        # == 1. Inject hooks before any page JS ====================
        page.add_init_script(INJECT_JS)

        # == 2. Navigate ===========================================
        print(f"Navigating to {url} ...")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(3000)

        # == 3. Scrape metadata from the DOM =======================
        metadata = page.evaluate("""() => {
            const pb = document.getElementById('postbody');
            if (!pb) return { error: 'no #postbody found' };

            const titleEl = pb.querySelector('span.text-2xl');
            const title = titleEl ? titleEl.textContent.trim() : 'No title found';

            const tagmDivs = pb.querySelectorAll('.tagm');
            let performer = null, scriptwriter = null, length = null;
            for (const div of tagmDivs) {
                const spans = div.querySelectorAll('span');
                const label = spans[0]?.textContent.trim().toLowerCase();
                if (label === 'by') {
                    const link = div.querySelector('a[href^="/u/"]');
                    performer = link ? link.textContent.trim() : null;
                } else if (label === 'script') {
                    const link = div.querySelector('a[href^="/u/"]');
                    scriptwriter = link ? link.textContent.trim() : null;
                } else if (label === 'length') {
                    length = spans[spans.length - 1]?.textContent.trim() || null;
                }
            }

            const proseEl = pb.querySelector('.prose.prose-ha');
            const description = proseEl ? proseEl.innerHTML.trim() : 'No description found';

            const tidEls = pb.querySelectorAll('span[data-tid]');
            const trackEntries = Array.from(tidEls).map(el => ({
                tid: el.getAttribute('data-tid'),
                text: el.textContent.trim(),
            }));

            const tagEls = pb.querySelectorAll('a.tag .tag');
            const tags = Array.from(tagEls).map(el => el.textContent.trim());

            return {
                title, description, length,
                performer: performer || 'unknown_hotaudio_user',
                scriptwriter, trackEntries, tags,
                pageUrl: location.href,
            };
        }""")

        if metadata.get("error"):
            print(f"  DOM scrape failed: {metadata['error']}")
            return

        # Fallback username from URL
        url_user_match = re.search(r'/u/([^/]+)/', url)
        username = metadata["performer"]
        if username == "unknown_hotaudio_user" and url_user_match:
            username = url_user_match.group(1)
        username = resolve_author(username)

        title = metadata["title"]
        description = metadata["description"]
        track_entries = metadata.get("trackEntries", [])
        tags = metadata.get("tags", [])
        length = metadata.get("length")
        playcount = "No playcount found"

        # Pick best track ID
        track_id = None
        for te in track_entries:
            if re.search(r'\.\w{2,4}$', te.get("text", "")):
                track_id = te["tid"]
                break
        if track_id is None and track_entries:
            track_id = track_entries[0]["tid"]

        print(f"  Username:     {username}")
        print(f"  Title:        {title}")
        if metadata.get("scriptwriter"):
            print(f"  Script by:    {metadata['scriptwriter']}")
        print(f"  Description:  {description[:80]}...")
        print(f"  Track IDs:    {track_entries}")
        print(f"  Tags:         {', '.join(tags)}")
        print(f"  Length:       {length}")

        # == 4. Start playback =====================================
        speed_map = {
            0.5: "0.5x", 0.75: "0.75x", 1.0: "1.0x",
            1.25: "1.25x", 1.5: "1.5x", 1.75: "1.75x", 2.0: "2.0x",
        }
        closest_speed = min(speed_map, key=lambda s: abs(s - playback_speed))
        target_label = speed_map[closest_speed]
        print(f"  Setting speed to {target_label} (requested {playback_speed}x)...")

        speed_set = page.evaluate("""(targetLabel) => {
            const options = document.querySelectorAll('.speed-option');
            for (const opt of options) {
                if (opt.textContent.trim() === targetLabel) {
                    opt.click();
                    return 'menu';
                }
            }
            const el = document.querySelector('audio') || document.querySelector('video');
            if (el) {
                el.playbackRate = parseFloat(targetLabel);
                return 'direct';
            }
            return 'none';
        }""", target_label)
        print(f"  Speed set via: {speed_set}")

        print("  Starting playback...")
        play_btn = page.query_selector("#player-playpause")
        if play_btn:
            play_btn.click()
            print("  Clicked #player-playpause")
        else:
            page.keyboard.press("k")
            print("  Pressed 'k' keyboard shortcut")

        page.wait_for_timeout(2000)

        # Verify playback started
        is_paused = page.evaluate("""() => {
            const btn = document.getElementById('player-playpause');
            return btn ? btn.classList.contains('paused') : true;
        }""")
        if is_paused:
            print("  Still paused — trying keyboard shortcut...")
            page.keyboard.press("k")
            page.wait_for_timeout(2000)

        # Verify chunks are flowing
        chunks_started = page.evaluate("() => window.__INTERCEPTOR.chunks.length > 0")
        if not chunks_started:
            print("  No chunks yet — trying direct audio.play()...")
            page.evaluate("""() => {
                const el = window.__INTERCEPTOR.playerEl
                         || document.querySelector('audio')
                         || document.querySelector('video');
                if (el) el.play().catch(() => {});
            }""")
            page.wait_for_timeout(3000)
            chunks_started = page.evaluate("() => window.__INTERCEPTOR.chunks.length > 0")
            if not chunks_started:
                print("  ERROR: Could not start playback. Hooks may have been blocked.")
                return

        print("  Playback confirmed — chunks flowing.")

        # == 5. Wait for playback to end ===========================
        wait_timeout_ms = 45 * 60 * 1000
        if length:
            try:
                total_sec = 0
                for unit, mult in [("h", 3600), ("m", 60), ("s", 1)]:
                    m = re.search(rf'(\d+)\s*{unit}', length)
                    if m:
                        total_sec += int(m.group(1)) * mult
                if total_sec > 0:
                    real_sec = (total_sec / closest_speed) + 60
                    wait_timeout_ms = int(real_sec * 1000)
                    print(f"  Computed timeout: {real_sec:.0f}s "
                          f"(track {total_sec}s at {closest_speed}x)")
            except Exception:
                pass

        print("  Waiting for playback to finish...")
        try:
            page.wait_for_function(
                "() => window.__INTERCEPTOR.done === true",
                timeout=wait_timeout_ms,
            )
        except Exception as e:
            progress = page.evaluate("""() => {
                const el = document.getElementById('player-progress-text');
                return el ? el.textContent.trim() : '';
            }""")
            chunk_count = page.evaluate("() => window.__INTERCEPTOR.chunks.length")

            if chunk_count == 0:
                print(f"  ERROR: Playback never started or hooks failed: {e}")
                return

            progress_match = re.match(r'([\d:]+)\s*/\s*([\d:]+)', progress)
            if progress_match and progress_match.group(1) == progress_match.group(2):
                print(f"  Progress bar shows complete ({progress}). Continuing.")
            else:
                print(f"  Warning: 'ended' event didn't fire (progress: {progress}), "
                      f"but we have {chunk_count} chunks. Continuing.")

        # == 6. Extract chunks =====================================
        print("  Extracting audio chunks...")
        audio_data = page.evaluate("""() => {
            const st = window.__INTERCEPTOR;
            const result = {
                mimeType: st.mimeType,
                chunkCount: st.chunks.length,
                totalBytes: st.chunks.reduce((s, c) => s + c.byteLength, 0),
                data: [],
            };
            if (result.totalBytes > 50 * 1024 * 1024) {
                result.tooLarge = true;
                return result;
            }
            for (const chunk of st.chunks) {
                for (let i = 0; i < chunk.byteLength; i++) {
                    result.data.push(chunk[i]);
                }
            }
            return result;
        }""")

        if audio_data.get("tooLarge"):
            print("  File >50MB — using in-browser download fallback...")
            audio_bytes = _download_via_browser(page)
            if audio_bytes is None:
                return
        else:
            audio_bytes = bytes(audio_data["data"])

        chunk_count = audio_data["chunkCount"]
        total_bytes = audio_data["totalBytes"]
        mime = audio_data["mimeType"]
        print(f"  Captured {chunk_count} chunks, {total_bytes} bytes, MIME: {mime}")

        # == 7. Save to disk =======================================
        ext = "m4a" if "mp4" in mime else "webm"
        slug_match = re.search(r'/u/[^/]+/([^/?#]+)', url)
        if slug_match:
            slug = slug_match.group(1)
        elif track_id:
            slug = track_id
        else:
            slug = "unknown"
        audio_filename = f"{slug}.{ext}"

        media_dir = f"./media/{username}"
        os.makedirs(media_dir, exist_ok=True)
        output_path = os.path.join(media_dir, audio_filename)

        if os.path.exists(output_path):
            print(f"  File already exists: {output_path}. Skipping write.")
        else:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"  Saved: {output_path}")

        # == 8. Append to shared metadata ==========================
        audio_metadata.append([username, title, description, playcount, audio_filename])
        print(f"  Done. audio_metadata now has {len(audio_metadata)} entries.")

    except Exception as e:
        print(f"  FATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        page.close()


def _download_via_browser(page):
    """Fallback for >50MB files: trigger an in-browser Blob download."""
    try:
        with page.expect_download(timeout=30_000) as dl_info:
            page.evaluate("""() => {
                const st = window.__INTERCEPTOR;
                const blob = new Blob(st.chunks, { type: st.mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'hotaudio_capture';
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(url);
            }""")
        download = dl_info.value
        with open(download.path(), "rb") as f:
            return f.read()
    except Exception as e:
        print(f"  Download fallback failed: {e}")
        return None


# == Auto-register =====================================================
# Only registers if Playwright is actually installed; otherwise the
# import is silently skipped by handlers/__init__.py.
register("hotaudio", "hotaudio", get_metadata_hotaudio)