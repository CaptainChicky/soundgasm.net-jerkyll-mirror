import os
import re

# Function to extract .m4a filenames from HTML files


def extract_audio_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # Regular expression to find the m4a filename
        matches = re.findall(
            r'["\']\.\.\/\.\.\/\.\.\/media\.soundgasm\.net\/sounds\/([^"\']+\.m4a)', content)

        return matches


# Directory containing the HTML files
directory = './'  # Change this to the path of the directory if needed

# Open the output file to store results
with open('audios.txt', 'w', encoding='utf-8') as output_file:
    # Loop through all HTML files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            audio_files = extract_audio_from_html(file_path)

            # Write each HTML file's name and its found .m4a filenames to the output file
            for audio in audio_files:
                output_file.write(f"{filename}\n{audio}\n")

print("Processing complete. Results saved to audios.txt.")
