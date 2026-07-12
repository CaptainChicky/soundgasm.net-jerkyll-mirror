import os

MEDIA_DIR = "media"

# Supported audio extensions (you can expand)
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".opus", ".ogg", ".aac"}

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
print("All audio files with sizes:")
for path, size in audio_files:
    print(f"{path} -> {size / (1024*1024):.2f} MB")