"""
YAML file persistence for the audio archiver.

Handles initializing the YAML file, writing new entries, and
post-processing playcounts with unicode replacements.
"""
import os
import re

from .config import (
    YAML_FILE, PLAYCOUNT_REPLACEMENTS, random_playcount_replacement,
    log_ok, log_warn,
)
from .registry import audio_metadata


# == Initialization ====================================================
def ensure_yaml_exists():
    """Create the YAML file with a bare 'users:' key if it doesn't exist."""
    if not os.path.exists(YAML_FILE):
        os.makedirs(os.path.dirname(YAML_FILE), exist_ok=True)
        with open(YAML_FILE, "w", encoding="utf-8") as f:
            f.write("users:")
        log_ok(f"Created {YAML_FILE} with initial content.")
    else:
        print(f"  {YAML_FILE} already exists.")


# == Helpers ===========================================================
def _get_existing_user_audios(yaml_content, username):
    """Extract all audio filenames for a specific user from YAML content."""
    pattern = rf"  {re.escape(username)}:.*?(?=\n  \w+:|\Z)"
    section = re.search(pattern, yaml_content, re.DOTALL)
    if not section:
        return []
    return re.findall(r"audio: '([^']+)'", section.group(0))


def _get_existing_user_titles(yaml_content, username):
    """Extract all titles for a specific user from YAML content."""
    pattern = rf"  {re.escape(username)}:.*?(?=\n  \w+:|\Z)"
    section = re.search(pattern, yaml_content, re.DOTALL)
    if not section:
        return []

    text = section.group(0)
    titles = []

    # pipe-style multi-line titles
    for m in re.finditer(
        r"title: \|\n\s+(.+?)(?=\n\s+description:)", text, re.DOTALL
    ):
        titles.append(m.group(1).strip())

    # inline quoted titles
    for m in re.finditer(r"title: '([^']+)'", text):
        titles.append(m.group(1))

    return titles


def _modify_duplicate_title(title):
    """Append the last character once more to disambiguate a duplicate title."""
    stripped = title.rstrip()
    if stripped:
        return stripped + stripped[-1]
    return title


# == Pre-download duplicate check ======================================
def is_already_archived(username, audio_filename):
    """
    Check BEFORE downloading whether this audio is already archived.

    Looks in three places:
      1. In-memory queue  (already scraped this run but not yet written)
      2. YAML on disk     (written by a previous run)
      3. Media folder     (file on disk even if YAML entry is missing)

    Handlers should call this after resolving the filename but before
    downloading the file.  Returns True when the download can be skipped.
    """
    # 0. Force redownload when applicable
    from .config import FORCE_REDOWNLOAD
    if FORCE_REDOWNLOAD:
        return False
    
    # 1. Already queued this run
    for entry in audio_metadata:
        if entry[0] == username and entry[4] == audio_filename:
            return True

    # 2. Recorded in YAML from a previous run
    if os.path.exists(YAML_FILE):
        with open(YAML_FILE, "r", encoding="utf-8") as f:
            yaml_content = f.read()
        if audio_filename in _get_existing_user_audios(yaml_content, username):
            return True

    # 3. File sitting on disk (belt-and-suspenders)
    media_path = os.path.join("media", username, audio_filename)
    if os.path.exists(media_path):
        return True

    return False


def _remove_audio_entry(yaml_content, audio_filename):
    """Remove a single entry block (title through audio line) from YAML content."""
    marker = f"audio: '{audio_filename}'"
    idx = yaml_content.find(marker)
    if idx == -1:
        return yaml_content
    start = yaml_content.rfind("    - title:", 0, idx)
    if start == -1:
        return yaml_content
    end = yaml_content.find("\n", idx)
    if end == -1:
        end = len(yaml_content)
    else:
        end += 1
    return yaml_content[:start] + yaml_content[end:]


# == Main save =========================================================
def save_metadata_to_yaml():
    """Write every entry in audio_metadata into the YAML file."""
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    for username, title, description, playcount, audio_filename in audio_metadata:
        # Skip true duplicates (same file already on disk for this user)
        if audio_filename in _get_existing_user_audios(yaml_content, username):
            from .config import FORCE_REDOWNLOAD
            if not FORCE_REDOWNLOAD:
                log_warn(f"Audio '{audio_filename}' already exists for {username}. Skipping...")
                continue
            yaml_content = _remove_audio_entry(yaml_content, audio_filename)

        # Disambiguate duplicate titles within the same user
        existing_titles = _get_existing_user_titles(yaml_content, username)
        if title in existing_titles:
            original = title
            title = _modify_duplicate_title(title)
            log_warn(f"Title '{original}' already exists for {username}. Modified to '{title}'")

        # Indent description lines for YAML block-scalar format
        description = "\n".join(
            "        " + line if line.strip() else ""
            for line in description.splitlines()
        )

        # Ensure user section exists
        if f"  {username}:" not in yaml_content:
            yaml_content += f"\n  {username}:\n"

        new_entry = (
            f"    - title: |\n"
            f"        {title}\n"
            f"      description: |\n"
            f"{description}\n" # The indentation already happened above
            f"      playcount: {playcount}\n"
            f"      audio: '{audio_filename}'\n"
        )

        # Insert at the top of the user's section
        header = f"  {username}:\n"
        insert_pos = yaml_content.find(header) + len(header)
        yaml_content = yaml_content[:insert_pos] + new_entry + yaml_content[insert_pos:]

    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    log_ok(f"Metadata saved to {YAML_FILE}")


# == Post-processing ==================================================
def postprocess_playcount_in_yaml():
    """Replace non-numeric playcounts with random unicode characters."""
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    def _replace(match):
        value = match.group(2).strip()
        if value.isdigit() or value in PLAYCOUNT_REPLACEMENTS:
            return match.group(0)
        return f"{match.group(1)}{random_playcount_replacement()}"

    yaml_content = re.sub(r"(\s*playcount:\s*)([^\n]*)", _replace, yaml_content)

    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    log_ok("Post-processing complete. Non-numeric playcounts replaced.")
