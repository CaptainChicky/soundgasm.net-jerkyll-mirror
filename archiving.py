import os
import random
import requests
import re
from bs4 import BeautifulSoup

YAML_FILE = "_data/audio_data.yml"

# replacements for playcount
replacements = ["﷽", "𒐫", "𒈙", "ඞ", "꧅", ".̵̴̶̸̶̵̵̵̷̵̷̵̴̵̶̶̸̸̶̷̸̸̧̧̡̧̨̧̨̧̨̨̡̡̨̡̢̢̧̢̢̢̨̨̢̧̨̡̨̢̢̢̨̢̧̢̡̡̢̧̨̡̢̡̢̢̡̧̧̨̡̧̨̢̧̢̡̨̡̢̢̢̢̡̛̛̛̛̛̛̛̛̛̛̛̛̛͉̦̱͔̯̫̝͖̼̺̞͇̠͔̝͕̦̟̭̖͚̼̤͎̺̱̲͎͖̻͇̥̜͎̭̥̣̲̘͔̝̮͓̮̹͍͎̼͙͎̲̗̩̲̘͍̩̜͉̣̥͔̙̮̰̤̼͓̳̗̻̣̜̳͕̥̮̟̜͖͚̝̺͇͚̜̞͎̫̳͕͖͙̭͖̼͇̦̳͕̤̩̞̺͚̤̫͎̪̘͔̰̖̠͇̹̣̗̻̭̼͕̬̤͔̞̣̥̲̤̪̖̗̱̤̲͕̯͕̻͕̲̺͖͚̫̤͍̼̤͙̙͖͓̮̪͎̤̫͇͉̼̦̦̖̫͕͎̜̠̙͉͙͇͇̟̞̺̺̗̯̲͎͙̼̬̰͉̙͉̼̘͎̭̻͉̪͇̞̝̟̘͍͇͓̬̭̗͚̥̬͚͖͍̫̼͇̖̩̭̗̘͔̫̪̣̻͍̗̩̝̖͎͙̻̱̹̪̺̩̗̻̤̬̠͙̭̜̤̦̖͎͎͈̰̲͇͈̖̮̪͉̹̦͖̠̟̩͉̝̟̩͕̠̹̥̬̲͚̝͕͙̻͓̟͉͙̠̦̦̻̘̪̪̟̦̹̫̗̘̱̳͈͚̱͓̲̩̪̗̞͇͕̗̲̟̮̱̯͇͙̰͎̲̦̺͚̳̤͕̦̦͔̟̳̠̯̪̲̫̖̯̖̪̖̘͈̩͚̟͖̗̫͙̙̜͚̟̣̳̝̟̬̠͓̤͖̫̱͍͍͖̞̹̥̠̤̭̥̱̭̲̺͇͕̯̫̩̗̫̬̲̘̯̮̼̰͕͕͇͎̪̞̱͙̩̺͍͕̮͙̞̰̫̩͕̺͈̘͕͕̝̞̟̳͈͉͚̥͉̺̠̦̬̙͔̩͖̱̺̣̜̲̙͖̖͓͖̞̘̼̰̘̲̠̗͔̦̲̭̬͖̯̠̤̹̺͍͈̙̲̼͇̲͚͚͖̘̭̤͖͖̰̣͕͖͉͚̠̙̩̣͙̖̰̹̣̪͕̠̬̱̠̰͖̣̲̟͚̪̤̥̻̜͇̠̼͇̩̯̟̮̜̘̼̞͚̠͎̙̦̞̹̤̦̹͈̭̼̤̫͎̙̟̝̦͈̯̜̬͍͕̩͍͍̱͎͙̟̞̰͈̲̯͇̲̹̟̫̙͖̦͎̞͉̬͔͕̬͕͉̲͉̣̰̠̮͇͍̟̯͎͓͓͚̬̐̀͋́̿̃̉̈́̍͒̈́̆̋͊́̐͑̀̆̎̌͒͛̔̀̾̓̿͂͆̊̽̑̾̌͋̌̂͆̎͌͂̑͐̒͒̇͆̂͗̒̊̂̅̔͛̅͑͛́̑͗͋́̄̎̔́̈́̏͒͒̋̑͊̎̀̂̀̃̆̈́̍́͑̄̆̏̈̾͒̃̋́̈́͒̐̿̓̄̂̀́̍̐̀͌̑̌̈̆̆̐͐̈̄͆̋̉̃̿́́̃̀͊͗̍̏̾̈̏͂́̐͊̽̏̔̊̈́̿̒̎̓͂̃͗͒͐͐̀͗̊͌̈́́͂̅͛̾̑͑̆͋̈͒̏̇̀̈́̏̀̆̓͑̅͒̏̂̒́̒͊̈́͌͛͂̾̆̈́͑̌̈͆̂̈́͑̔͒͐̅͂̃͒͛͒̀͋͆̉̆̈̈́͋̅̿͒̿̀́͂̈́͗̈́͆̄̀̅̄͋͒̋̏̓̔̂̈́̔͒̋͋͒̾ͣ̀̐͒͊̀̋̄̒̓̍͂̐̾͗̍̂̾̋̾̃̇̑̌͗͐͗͗̋̄̽̀̈͌͗̀͊̍̋̐̔̏͗̉̈͐̏̊͂̃͌͌̍͗͋̒̍̋̎̽̈́̌̽̾̈̾͋̑͆͐̆̀́̄̐͒͗̇̓̂̔͆̂̎̾̽̾̄̈́͊͊̔̍̈́̍̂̈́͗͆̃̏́͒͑̃̂̿̈̈́̀̔̌̓̅̀͛̃̋͆̑̈͌̀̿̌̍͛̒̈́̎̍̉̒̒͑̄̏̉͑͊̈́̓̿̅͆͒́̌͑́͒̂̒̃̀́̓̊̊͊̇̈́͊̏̄̒̔̊̿́͋̓̈́̇̽̍̾͋̈́̐̍̽͛̀̈́̓̿̏̉̌̎͐̍̔͂̈́̀̀͊̂̆̈̋̇̍̉̐̑̈̇̆̾̾̈́̔̽̒͊͋̇̓̍̈́́̈́̅̊̀̽̔̀̍̽̎͊̀̈́̿̀͊͗̃̑͌̈́̌̍̏̂̓̍̊́͗̊͊͑̊̃͒̄͂̊͆̌̀̆̓̃̓̓͌̄͊̃́̐́͛̎̋̕̕͘͘͘͘̕̕̕̕͘̚̚̕͘̕͘̚̚̕̚̚͘͘̚̚̚̕̕̚̚̕̚̕̕͘̚̕͜͜͜͜͜͜͜͜͜͜͜͜͜͜͜͜͝͝͝͠͝͠͠͝͠͝͝͝͝͝͠͠͝͠͝͠͠͠͝͝͠͝͝͝͝͝͝͠͠͝ͅͅͅͅͅͅͅͅͅͅͅͅͅͅ,", ".̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒", "௵", "𒅌"]

# Initialize the global metadata array
audio_metadata = []


# Step 1: Check if the YAML file exists; if not, create it
if not os.path.exists(YAML_FILE):
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(YAML_FILE), exist_ok=True)
    
    with open(YAML_FILE, "w", encoding="utf-8") as file:
        file.write("users:")  # Initialize the YAML file
    print(f"Created {YAML_FILE} with initial content.")
else:
    print(f"{YAML_FILE} already exists.")


# Step 2: Extract username from the webpage and add to the array
def get_metadata(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #=======================================================================
    # Extract the raw username (keeping all HTML tags)
    username_tag = soup.find("div", style="margin:10px 0").find("a")
    if username_tag:
        username = username_tag.decode_contents()  # Keep raw content, no cleaning
        print(f"Extracted Raw Username: {username}")
    else:
        print("Username not found.")
        username = "No username found"

    # =======================================================================
    # Extract the raw title (keeping all HTML tags)
    title_tag = soup.find("div", class_="jp-title", attrs={"aria-label": "title"})
    title = title_tag.decode_contents() if title_tag else "No title found"
    print(f"Extracted Raw Title: {title}")

    # =======================================================================
    # Extract the raw description between <p style="white-space: pre-wrap;"> and <div class="jp-no-solution">
    description_pattern = r'<p style="white-space: pre-wrap;">(.*?)<div class="jp-no-solution">'
    description_match = re.search(description_pattern, response.text, re.DOTALL)

    if description_match:
        description = description_match.group(1)  # Extract the content matched by the regex
        description = description.replace("</p>\r\n      </div>\r\n      ", "")  # Clean up unwanted closing tags
        # description = description.replace("\n", "").replace("\r", "")  # Remove all newlines and carriage returns
        print(f"Extracted Raw Description: {description[:100]}...")  # Print the first 100 characters for preview
    else:
        description = "No description found"
        print("Description not found.")

    # =======================================================================
    # Extract the playcount
    # Get the base URL by removing the audio page's part
    base_url = "/".join(url.split("/")[:-1])
    print(f"Base URL: {base_url}")

    # Perform a request to the base URL (the user's page)
    base_response = requests.get(base_url)
    base_soup = BeautifulSoup(base_response.text, "html.parser")

    # Search for the <a> tag that matches the audio page URL
    audio_link_tag = base_soup.find("a", href=url)
    if audio_link_tag:
        # After finding the <a> tag, we search for the next <span class="playCount"> in the content
        playcount_span = audio_link_tag.find_next("span", class_="playCount")
        if playcount_span:
            # Extract the playcount number from "Play Count: [playcount]"
            playcount_text = playcount_span.text
            playcount_match = re.search(r"Play Count:\s*(\d+)", playcount_text)
            if playcount_match:
                playcount = playcount_match.group(1)
                print(f"Extracted Playcount: {playcount}")
            else:
                playcount = "No playcount found"
                print("Playcount not found.")
        else:
            playcount = "No playcount span found"
            print("No playcount span found.")
    else:
        playcount = "No audio link found"
        print("No matching audio link found on the base page.")

    # =======================================================================
    # Extract the audio file URL and download it
    audio_url_pattern = r'https://media.soundgasm.net/sounds/(.*?).m4a'
    audio_url_match = re.search(audio_url_pattern, response.text)

    if audio_url_match:
        audio_filename = audio_url_match.group(1) + ".m4a"  # Extract the audio file name
        print(f"Extracted Audio Filename: {audio_filename}")

        # Ensure the target directory exists for the username
        media_dir = f"./media/{username}"
        os.makedirs(media_dir, exist_ok=True)

        # Download the audio file
        audio_url = f"https://media.soundgasm.net/sounds/{audio_filename}"
        audio_response = requests.get(audio_url)

        # Save the audio file in the specified directory
        audio_path = os.path.join(media_dir, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        print(f"Downloaded audio file: {audio_path}")
        
    else:
        print("Audio file not found.")

    # Add the raw content to the global array
    audio_metadata.append([username, title, description, playcount, audio_filename])

    print(f"Current audio_metadata array: {audio_metadata}")



# Step 3: Save the metadata to the YAML file
def save_metadata_to_yaml():
    # Open the existing YAML file 
    with open(YAML_FILE, "r", encoding="utf-8") as file:
        yaml_content = file.read()

    # Start by checking if the user exists in the YAML content
    for entry in audio_metadata:
        username, title, description, playcount, audio_filename = entry

        # Fix indentation for the description
        description = "\n".join(["        " + line if line.strip() else "" for line in description.splitlines()])

        # Check if the user exists in the file
        if f"  {username}:" not in yaml_content:
            # If the user doesn't exist, create the user entry
            yaml_content += f"\n  {username}:\n"
        
        # Check if the audio title already exists for that user
        title_check = f"title: |\n        {title}"
        if title_check in yaml_content:
            print(f"Title '{title}' already exists for {username}. Skipping...")
            continue  # Skip if the title already exists

        # Create the new entry to be added for the user
        new_entry = f"    - title: |\n        {title}\n      description: |\n{description}\n      playcount: {playcount}\n      audio: '{audio_filename}'\n"
        
        # Insert the new entry at the top of the user's section
        user_section_start = yaml_content.find(f"  {username}:") + len(f"  {username}:\n")
        user_section_end = yaml_content.find("\n  ", user_section_start)  # Find the next user or end of file
        if user_section_end == -1:  # No other users, end of file
            user_section_end = len(yaml_content)

        # Add the new entry to the top of the user's section
        yaml_content = yaml_content[:user_section_start] + new_entry + yaml_content[user_section_start:]

    # Write the modified YAML content back to the file
    with open(YAML_FILE, "w", encoding="utf-8") as file:
        file.write(yaml_content)

    print(f"Metadata saved to {YAML_FILE}")


# Step 4: Post-process the playcount in the YAML file
def postprocess_playcount_in_yaml():
    # Read the content of the YAML file
    with open(YAML_FILE, "r", encoding="utf-8") as file:
        yaml_content = file.read()

    # Regex pattern to match the playcount lines
    playcount_pattern = r"(\s*playcount:\s*)([^\n]*)"

    # Function to replace non-numeric playcount with a random character
    def replace_non_numeric_playcount(match):
        playcount_value = match.group(2).strip()  # Extract the value of playcount
        if playcount_value.isdigit():
            return match.group(0)  # If the playcount is a number, leave it unchanged
        else:
            # Replace non-numeric playcount with a random character from the replacements list
            random_replacement = random.choice(replacements)
            return f"{match.group(1)}{random_replacement}"

    # Apply the replacement to all playcount occurrences in the YAML content
    modified_yaml_content = re.sub(playcount_pattern, replace_non_numeric_playcount, yaml_content)

    # Write the modified YAML content back to the file
    with open(YAML_FILE, "w", encoding="utf-8") as file:
        file.write(modified_yaml_content)

    print(f"Post-processing complete. Non-numeric playcounts replaced with random characters.")
    

# Example usage
url = "https://soundgasm.net/u/skitty/Bullying-You-with-Kisses-F4M"
get_metadata(url)
save_metadata_to_yaml()
postprocess_playcount_in_yaml()