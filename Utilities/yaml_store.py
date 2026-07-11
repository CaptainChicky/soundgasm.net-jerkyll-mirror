"""
YAML file persistence for the audio archiver.

Handles initializing the YAML file, writing new entries, and
post-processing playcounts with unicode replacements.
"""
import os
import re

from .config import YAML_FILE, PLAYCOUNT_REPLACEMENTS, random_playcount_replacement
from .registry import audio_metadata


# ── Initialization ────────────────────────────────────────────────────
def ensure_yaml_exists():
    """Create the YAML file with a bare 'users:' key if it doesn't exist."""
    if not os.path.exists(YAML_FILE):
        os.makedirs(os.path.dirname(YAML_FILE), exist_ok=True)
        with open(YAML_FILE, "w", encoding="utf-8") as f:
            f.write("users:")
        print(f"Created {YAML_FILE} with initial content.")
    else:
        print(f"{YAML_FILE} already exists.")


# ── Helpers ───────────────────────────────────────────────────────────
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


# ── Main save ─────────────────────────────────────────────────────────
def save_metadata_to_yaml():
    """Write every entry in audio_metadata into the YAML file."""
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        yaml_content = f.read()

    for username, title, description, playcount, audio_filename in audio_metadata:
        # Skip true duplicates (same file already on disk for this user)
        if audio_filename in _get_existing_user_audios(yaml_content, username):
            print(f"Audio '{audio_filename}' already exists for {username}. Skipping...")
            continue

        # Disambiguate duplicate titles within the same user
        existing_titles = _get_existing_user_titles(yaml_content, username)
        if title in existing_titles:
            original = title
            title = _modify_duplicate_title(title)
            print(f"Title '{original}' already exists for {username}. Modified to '{title}'")

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
            f"{description}\n"
            f"      playcount: {playcount}\n"
            f"      audio: '{audio_filename}'\n"
        )

        # Insert at the top of the user's section
        header = f"  {username}:\n"
        insert_pos = yaml_content.find(header) + len(header)
        yaml_content = yaml_content[:insert_pos] + new_entry + yaml_content[insert_pos:]

    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"Metadata saved to {YAML_FILE}")


# ── Post-processing ──────────────────────────────────────────────────
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

    print("Post-processing complete. Non-numeric playcounts replaced.")
