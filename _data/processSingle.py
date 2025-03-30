import os
import re


# File paths
data_file = 'data.txt'
catalogue_file = 'audio_data.yml'


# Function to read and parse data.txt


def parse_data_file(data_file):
    entries = []
    with open(data_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            title = lines[i].strip()
            description = lines[i+1].strip()
            playcount_match = re.search(r'Play Count: (\d+)', lines[i+2])
            if playcount_match:
                playcount = playcount_match.group(1)
            else:
                playcount = '0'  # Default to 0 if no playcount is found

            # Append the extracted data to the entries list
            entries.append({
                'title': title,
                'description': description,
                'playcount': playcount,
                'audio': ''  # Leave audio blank
            })

            # Move to the next block of data (3 lines per entry)
            i += 3

    return entries

# Function to update audio_data.yml with the new entries


def update_catalogue(catalogue_file, user_name, entries):
    # Read existing catalogue file (if it exists)
    try:
        with open(catalogue_file, 'r', encoding='utf-8') as file:  # ✅ Apply UTF-8 encoding
            catalogue_data = file.read()
    except FileNotFoundError:
        catalogue_data = ''

    # Find the section for the user and append new entries
    user_pattern = re.compile(rf'{user_name}:(.*?)(?=\n\S|$)', re.DOTALL)
    match = user_pattern.search(catalogue_data)

    if match:
        # If user section exists, append to it
        user_section = match.group(0)
        user_section_end = match.end(0)
        new_entries_str = '\n'.join([f"    - title: '{entry['title']}'\n"
                                     f"      description: '{entry['description']}'\n"
                                     f"      playcount: {entry['playcount']}\n"
                                     f"      audio: '{entry['audio']}'\n" for entry in entries])
        updated_catalogue = catalogue_data[:user_section_end] + \
            '\n' + new_entries_str
    else:
        # If user section does not exist, create it
        new_entries_str = '\n'.join([f"    - title: '{entry['title']}'\n"
                                     f"      description: '{entry['description']}'\n"
                                     f"      playcount: {entry['playcount']}\n"
                                     f"      audio: '{entry['audio']}'\n" for entry in entries])
        updated_catalogue = catalogue_data + \
            f'\nusers:\n  {user_name}:\n' + new_entries_str

    # Write the updated data back to the catalogue file
    with open(catalogue_file, 'w', encoding='utf-8') as file:  # ✅ Write with UTF-8 encoding
        file.write(updated_catalogue)




# Parse data from data.txt
entries = parse_data_file(data_file)

# Update audio_data.yml for user IvyWilde
update_catalogue(catalogue_file, 'IvyWilde', entries)

print("Catalogue updated successfully!")
