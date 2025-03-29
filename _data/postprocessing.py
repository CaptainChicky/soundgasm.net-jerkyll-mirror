import re

# Function to normalize the title by removing non-alphabet characters and replacing spaces with dashes
def normalize_title(title):
    return re.sub(r'[^A-Za-z0-9 ]', '', title).replace(' ', '-')

# Function to read the audio.txt file and build a mapping between normalized titles and audio filenames
def read_audio_file(audio_file_path):
    audio_mapping = {}
    with open(audio_file_path, 'r') as audio_file:
        lines = audio_file.readlines()
        for i in range(0, len(lines), 2):  # Every two lines, first is title and second is audio filename
            title = lines[i].strip().replace('.html', '').replace('-', ' ')
            audio_filename = lines[i + 1].strip()
            normalized_title = normalize_title(title)
            audio_mapping[normalized_title] = audio_filename
    return audio_mapping

# Function to read catalogue.txt and update it with the audio file names
def update_catalogue_file(catalogue_file_path, audio_mapping):
    with open(catalogue_file_path, 'r') as catalogue_file:
        catalogue_lines = catalogue_file.readlines()

    # Processing catalogue file to add audio filename
    updated_lines = []
    inside_user_section = False
    for line in catalogue_lines:
        if line.startswith('users:'):
            inside_user_section = True
        elif inside_user_section and line.strip() == '':
            inside_user_section = False

        # Look for titles and add corresponding audio file if available
        if 'title:' in line:
            title = line.strip().split(":", 1)[1].strip().strip("'")
            normalized_title = normalize_title(title)
            audio_filename = audio_mapping.get(normalized_title, '')

            updated_lines.append(line)
        elif 'playcount:' in line:
            updated_lines.append(line)
            # Find the next line where we should add the audio filename
            updated_lines.append(f"      audio: '{audio_filename}'\n" if audio_filename else "      audio: ''\n")
        else:
            updated_lines.append(line)

    # Write the updated catalogue to the file
    with open(catalogue_file_path, 'w') as catalogue_file:
        catalogue_file.writelines(updated_lines)

# Paths to the files
catalogue_file_path = 'audio_data.yml'
audio_file_path = 'audios.txt'

# Step 1: Read the audio.txt file and create the audio mapping
audio_mapping = read_audio_file(audio_file_path)

# Step 2: Update the catalogue.txt file with the corresponding audio filenames
update_catalogue_file(catalogue_file_path, audio_mapping)

print(f"Catalogue file '{catalogue_file_path}' has been updated with audio files.")
