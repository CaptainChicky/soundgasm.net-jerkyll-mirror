"""List all downloaded audio files sorted by size (largest first)."""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "Utilities" else SCRIPT_DIR
MEDIA_DIR = os.path.join(REPO_ROOT, "media")

# Supported audio extensions (you can expand)
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".opus", ".ogg", ".aac", ".webm"}

audio_files = []

# Walk through all directories and files
for root, dirs, files in os.walk(MEDIA_DIR):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in AUDIO_EXTENSIONS:
            full_path = os.path.join(root, file)
            size_bytes = os.path.getsize(full_path)
            audio_files.append((full_path, size_bytes))

# Sort by file size descending
audio_files.sort(key=lambda x: x[1], reverse=True)

# Print all files with sizes in MB
print(f"Found {len(audio_files)} audio files:\n")
for path, size in audio_files:
    print(f"  {size / (1024*1024):>8.2f} MB  {os.path.relpath(path, REPO_ROOT)}")