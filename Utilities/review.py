"""
Interactive review tool for the audio archive.

Reads audio_data.yml, shows each entry in order from the yaml,
and lets you keep/remove/play each one.  Removals are applied
to both the YAML and the media/ folder after confirmation.
"""
import os
import re
import shutil
import subprocess
import sys
import platform

# == Paths (resolve relative to repo root, not script location) ========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# If script is in Utilities/, go up one level to repo root
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "Utilities" else SCRIPT_DIR
YAML_FILE = os.path.join(REPO_ROOT, "_data", "audio_data.yml")
MEDIA_DIR = os.path.join(REPO_ROOT, "media")


# == Colors ============================================================
_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
_RED = "\033[1;31m" if _COLOR else ""
_YEL = "\033[1;33m" if _COLOR else ""
_GRN = "\033[1;32m" if _COLOR else ""
_CYN = "\033[1;36m" if _COLOR else ""
_DIM = "\033[2m"    if _COLOR else ""
_BLD = "\033[1m"    if _COLOR else ""
_RST = "\033[0m"    if _COLOR else ""


# == YAML parsing ======================================================
def parse_entries(yaml_path):
    """
    Parse audio_data.yml into a list of entry dicts.

    Each entry has: username, title, playcount, audio, filepath,
    filesize, start_line, end_line (exclusive, like a slice).
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    current_user = None

    # First pass: find every "    - title:" line and its parent user
    entry_starts = []
    for i, line in enumerate(lines):
        user_match = re.match(r"^  (\S+):\s*$", line)
        if user_match:
            current_user = user_match.group(1)
        if re.match(r"^    - title:", line):
            entry_starts.append((i, current_user))

    # Second pass: for each entry, find its end and extract fields
    for idx, (start, user) in enumerate(entry_starts):
        # End is either the next entry start or end of file
        if idx + 1 < len(entry_starts):
            end = entry_starts[idx + 1][0]
        else:
            end = len(lines)

        # But a user section boundary also ends the entry
        for j in range(start + 1, end):
            if re.match(r"^  \S+:\s*$", lines[j]):
                end = j
                break

        block = "".join(lines[start:end])

        # -- Title --
        title_block = re.search(
            r"title: \|\n(.*?)(?=\n\s+(?:description|playcount|audio):)",
            block, re.DOTALL,
        )
        if title_block:
            title = " ".join(title_block.group(1).split())
        else:
            m = re.match(r"    - title:\s*'([^']*)'", lines[start])
            if not m:
                m = re.match(r"    - title:\s*(.*)", lines[start])
            title = m.group(1).strip().strip("'\"") if m else "(no title)"

        # -- Playcount --
        pc = re.search(r"playcount:\s*(.*)", block)
        playcount = pc.group(1).strip() if pc else ""

        # -- Audio filename --
        au = re.search(r"audio:\s*'([^']*)'", block)
        audio = au.group(1) if au else ""

        # -- File on disk --
        filepath = os.path.join(MEDIA_DIR, user or "", audio) if audio else ""
        filesize = 0
        if filepath and os.path.exists(filepath):
            filesize = os.path.getsize(filepath)

        entries.append({
            "username":   user or "unknown",
            "title":      title,
            "playcount":  playcount,
            "audio":      audio,
            "filepath":   filepath,
            "filesize":   filesize,
            "start_line": start,
            "end_line":   end,
        })

    return entries, lines


# == Helpers ===========================================================
def fmt_size(b):
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / (1024 * 1024):.1f} MB"


def play_audio(filepath):
    if not os.path.exists(filepath):
        print(f"  {_RED}File not found: {filepath}{_RST}")
        return
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception as e:
        print(f"  {_RED}Could not open: {e}{_RST}")


# == Main ==============================================================
def main():
    if not os.path.exists(YAML_FILE):
        print(f"{_RED}YAML not found: {YAML_FILE}{_RST}")
        return

    entries, lines = parse_entries(YAML_FILE)
    if not entries:
        print("No entries found in YAML.")
        return

    # Present in YAML order (grouped by user, as authored)
    total_size = sum(e["filesize"] for e in entries)
    print(f"\n  {_BLD}{len(entries)} entries{_RST} · {_BLD}{fmt_size(total_size)}{_RST} total\n")
    print(f"  {_DIM}(k)eep  (r)emove  (s)kip  (p)lay  (q)uit{_RST}\n")

    to_remove = []
    last_choice = None
    last_user = None

    for idx, entry in enumerate(entries):
        # Show user header when switching to a new user
        if entry["username"] != last_user:
            last_user = entry["username"]
            print(f"  {_BLD}── {last_user} ──{_RST}\n")

        size_str = fmt_size(entry["filesize"]) if entry["filesize"] else "file missing"
        pc = entry["playcount"] or "?"
        title_display = entry["title"][:90] if entry["title"] else "(no title)"

        print(f"  {_CYN}[{idx + 1}/{len(entries)}]{_RST}  "
              f"{_BLD}{entry['username']}{_RST} — {title_display}")
        print(f"           {size_str} · playcount: {pc}")

        if not os.path.exists(entry["filepath"]):
            print(f"           {_YEL}⚠ audio file not on disk{_RST}")

        while True:
            try:
                choice = input(f"           {_DIM}>{_RST} ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "q"

            if choice == "k":
                print(f"           {_GRN}✓ kept{_RST}\n")
                break
            elif choice == "r":
                to_remove.append(entry)
                print(f"           {_RED}✗ marked for removal{_RST}\n")
                break
            elif choice == "s":
                print(f"           {_DIM}— skipped{_RST}\n")
                break
            elif choice == "p":
                play_audio(entry["filepath"])
            elif choice == "q":
                break
            else:
                print(f"           {_DIM}(k)eep  (r)emove  (s)kip  (p)lay  (q)uit{_RST}")

        if choice == "q":
            print(f"\n  Quit after reviewing {idx}/{len(entries)} entries.")
            break

    # == Summary =======================================================
    if not to_remove:
        print(f"\n  {_GRN}Nothing to remove. Archive unchanged.{_RST}")
        return

    remove_size = sum(e["filesize"] for e in to_remove)
    print(f"\n  {'─' * 50}")
    print(f"  {_RED}{len(to_remove)} entries marked for removal{_RST} "
          f"(~{fmt_size(remove_size)} freed)\n")
    for e in to_remove:
        print(f"    {_RED}✗{_RST} {e['username']} — {e['title'][:65]}")

    print()
    try:
        confirm = input(f"  {_BLD}Remove these from YAML and delete audio files? (yes/no): {_RST}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        confirm = "no"

    if confirm != "yes":
        print("  Aborted. Nothing changed.")
        return

    # == Backup ========================================================
    backup_path = YAML_FILE.replace(".yml", ".yml.bak")
    shutil.copy2(YAML_FILE, backup_path)
    print(f"  {_GRN}✓ Backed up to {os.path.relpath(backup_path, REPO_ROOT)}{_RST}")

    # == Remove from YAML (bottom-up to preserve line indices) =========
    remove_ranges = sorted(
        [(e["start_line"], e["end_line"]) for e in to_remove],
        key=lambda r: r[0],
        reverse=True,
    )
    for start, end in remove_ranges:
        del lines[start:end]

    # Clean up empty user sections (header with no entries after it)
    cleaned = []
    for i, line in enumerate(lines):
        if re.match(r"^  \S+:\s*$", line):
            # Look ahead: is the next non-blank line another header or EOF?
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and re.match(r"^    -", lines[j]):
                cleaned.append(line)  # has entries, keep it
            # else: empty section, skip it
        else:
            cleaned.append(line)

    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.writelines(cleaned)
    print(f"  {_GRN}✓ Updated {os.path.relpath(YAML_FILE, REPO_ROOT)}{_RST}")

    # == Delete audio files ============================================
    deleted = 0
    for entry in to_remove:
        fp = entry["filepath"]
        if os.path.exists(fp):
            os.remove(fp)
            deleted += 1

    print(f"  {_GRN}✓ Deleted {deleted} audio file(s){_RST}")
    print(f"\n  {_BLD}Done.{_RST} Removed {len(to_remove)} entries, "
          f"freed ~{fmt_size(remove_size)}.\n")


if __name__ == "__main__":
    main()
