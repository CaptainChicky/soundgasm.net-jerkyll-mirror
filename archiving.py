#!/usr/bin/env python3
"""
Requirements:
  pip install requests beautifulsoup4
  yt-dlp on PATH (for whyp.it)
"""
import os
import random
import requests
import re
import subprocess
import json
import shutil
from bs4 import BeautifulSoup

YAML_FILE = "_data/audio_data.yml"

# replacements for playcount
replacements = ["'﷽'", "'𒐫'", "'𒈙'", "'ඞ'", "'꧅'", "'.̵̴̶̸̶̵̵̵̷̵̷̵̴̵̶̶̸̸̶̷̸̸̧̧̡̧̨̧̨̧̨̨̡̡̨̡̢̢̧̢̢̢̨̨̢̧̨̡̨̢̢̢̨̢̧̢̡̡̢̧̨̡̢̡̢̢̡̧̧̨̡̧̨̢̧̢̡̨̡̢̢̢̢̡̛̛̛̛̛̛̛̛̛̛̛̛̛͉̦̱͔̯̫̝͖̼̺̞͇̠͔̝͕̦̟̭̖͚̼̤͎̺̱̲͎͖̻͇̥̜͎̭̥̣̲̘͔̝̮͓̮̹͍͎̼͙͎̲̗̩̲̘͍̩̜͉̣̥͔̙̮̰̤̼͓̳̗̻̣̜̳͕̥̮̟̜͖͚̝̺͇͚̜̞͎̫̳͕͖͙̭͖̼͇̦̳͕̤̩̞̺͚̤̫͎̪̘͔̰̖̠͇̹̣̗̻̭̼͕̬̤͔̞̣̥̲̤̪̖̗̱̤̲͕̯͕̻͕̲̺͖͚̫̤͍̼̤͙̙͖͓̮̪͎̤̫͇͉̼̦̦̖̫͕͎̜̠̙͉͙͇͇̟̞̺̺̗̯̲͎͙̼̬̰͉̙͉̼̘͎̭̻͉̪͇̞̝̟̘͍͇͓̬̭̗͚̥̬͚͖͍̫̼͇̖̩̭̗̘͔̫̪̣̻͍̗̩̝̖͎͙̻̱̹̪̺̩̗̻̤̬̠͙̭̜̤̦̖͎͎͈̰̲͇͈̖̮̪͉̹̦͖̠̟̩͉̝̟̩͕̠̹̥̬̲͚̝͕͙̻͓̟͉͙̠̦̦̻̘̪̪̟̦̹̫̗̘̱̳͈͚̱͓̲̩̪̗̞͇͕̗̲̟̮̱̯͇͙̰͎̲̦̺͚̳̤͕̦̦͔̟̳̠̯̪̲̫̖̯̖̪̖̘͈̩͚̟͖̗̫͙̙̜͚̟̣̳̝̟̬̠͓̤͖̫̱͍͍͖̞̹̥̠̤̭̥̱̭̲̺͇͕̯̫̩̗̫̬̲̘̯̮̼̰͕͕͇͎̪̞̱͙̩̺͍͕̮͙̞̰̫̩͕̺͈̘͕͕̝̞̟̳͈͉͚̥͉̺̠̦̬̙͔̩͖̱̺̣̜̲̙͖̖͓͖̞̘̼̰̘̲̠̗͔̦̲̭̬͖̯̠̤̹̺͍͈̙̲̼͇̲͚͚͖̘̭̤͖͖̰̣͕͖͉͚̠̙̩̣͙̖̰̹̣̪͕̠̬̱̠̰͖̣̲̟͚̪̤̥̻̜͇̠̼͇̩̯̟̮̜̘̼̞͚̠͎̙̦̞̹̤̦̹͈̭̼̤̫͎̙̟̝̦͈̯̜̬͍͕̩͍͍̱͎͙̟̞̰͈̲̯͇̲̹̟̫̙͖̦͎̞͉̬͔͕̬͕͉̲͉̣̰̠̮͇͍̟̯͎͓͓͚̬̐̀͋́̿̃̉̈́̍͒̈́̆̋͊́̐͑̀̆̎̌͒͛̔̀̾̓̿͂͆̊̽̑̾̌͋̌̂͆̎͌͂̑͐̒͒̇͆̂͗̒̊̂̅̔͛̅͑͛́̑͗͋́̄̎̔́̈́̏͒͒̋̑͊̎̀̂̀̃̆̈́̍́͑̄̆̏̈̾͒̃̋́̈́͒̐̿̓̄̂̀́̍̐̀͌̑̌̈̆̆̐͐̈̄͆̋̉̃̿́́̃̀͊͗̍̏̾̈̏͂́̐͊̽̏̔̊̈́̿̒̎̓͂̃͗͒͐͐̀͗̊͌̈́́͂̅͛̾̑͑̆͋̈͒̏̇̀̈́̏̀̆̓͑̅͒̏̂̒́̒͊̈́͌͛͂̾̆̈́͑̌̈͆̂̈́͑̔͒͐̅͂̃͒͛͒̀͋͆̉̆̈̈́͋̅̿͒̿̀́͂̈́͗̈́͆̄̀̅̄͋͒̋̏̓̔̂̈́̔͒̋͋͒̾ͣ̀̐͒͊̀̋̄̒̓̍͂̐̾͗̍̂̾̋̾̃̇̑̌͗͐͗͗̋̄̽̀̈͌͗̀͊̍̋̐̔̏͗̉̈͐̏̊͂̃͌͌̍͗͋̒̍̋̎̽̈́̌̽̾̈̾͋̑͆͐̆̀́̄̐͒͗̇̓̂̔͆̂̎̾̽̾̄̈́͊͊̔̍̈́̍̂̈́͗͆̃̏́͒͑̃̂̿̈̈́̀̔̌̓̅̀͛̃̋͆̑̈͌̀̿̌̍͛̒̈́̎̍̉̒̒͑̄̏̉͑͊̈́̓̿̅͆͒́̌͑́͒̂̒̃̀́̓̊̊͊̇̈́͊̏̄̒̔̊̿́͋̓̈́̇̽̍̾͋̈́̐̍̽͛̀̈́̓̿̏̉̌̎͐̍̔͂̈́̀̀͊̂̆̈̋̇̍̉̐̑̈̇̆̾̾̈́̔̽̒͊͋̇̓̍̈́́̈́̅̊̀̽̔̀̍̽̎͊̀̈́̿̀͊͗̃̑͌̈́̌̍̏̂̓̍̊́͗̊͊͑̊̃͒̄͂̊͆̌̀̆̓̃̓̓͌̄͊̃́̐́͛̎̋̕̕͘͘͘͘̕̕̕̕͘̚̚̕͘̕͘̚̚̕̚̚͘͘̚̚̚̕̕̚̚̕̚̕̕͘̚̕͜͜͜͜͜͜͜͜͜͜͜͜͜͜͜͜͝͝͝͠͝͠͠͝͠͝͝͝͝͝͠͠͝͠͝͠͠͠͝͝͠͝͝͝͝͝͝͠͠͝ͅͅͅͅͅͅͅͅͅͅͅͅͅͅ,'", "'.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒̾̓̈́̇̇̋.̷̨̡̡̢̢̡̡̢̡̜̦̤̗̟̫͖͙͚̗̤͇̹̟̦͕͓̱̤̻̠̯͇̯͓̩͈͕̣̙̙͕̻̣̟̲̘͕͇̙͇̘͔̜͓̳̳̙̠̖̭̦͚̘̙͖͕̘̮̼̝̺͔͚̖̝̫͈̝͍̥͕͚̪͔̘̠͖̘̠̣͚̹͙̙͔̇̆̿̐̓͊̏̎̐͗̾́̀̔̋̈́̎́̿̐̐̆̐͂̉́͋̆̃͒̑̉͒̑̽͗́́̾̊̌̊͑̒'", "'௵'", "'𒅌'"]

# author name synonyms, maps alternate names to the canonical name
# anything downloaded under "skittykat" gets filed under "skitty", etc.
AUTHOR_SYNONYMS = {
    "skittykat": "skitty",
}

def resolve_author(username):
    return AUTHOR_SYNONYMS.get(username, username)

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


# Detect which site a URL belongs to
def detect_site(url):
    if "soundgasm.net" in url:
        return "soundgasm"
    elif "whyp.it" in url:
        return "whyp"
    # elif "hotaudio" in url:
    #     return "hotaudio"
    elif "audiochan" in url:
        return "audiochan"
    else:
        return None


# Step 2: Extract metadata from the webpage and add to the array
# Routes to the right handler based on the URL

HANDLERS = {}

def get_metadata(url):
    site = detect_site(url)
    if site is None:
        print(f"Unsupported site: {url}")
        return

    print(f"\n{'=' * 60}")
    print(f"[{site}] {url}")
    print(f"{'=' * 60}")

    handler = HANDLERS.get(site)
    if handler:
        handler(url)
    else:
        print(f"No handler implemented for site: {site}")


#=======================================================================
# Soundgasm handler (direct scraping + requests download)
#=======================================================================
def get_metadata_soundgasm(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #=======================================================================
    # Extract the raw username (keeping all HTML tags)
    username_tag = soup.find("div", style="margin:10px 0").find("a")
    if username_tag:
        username = username_tag.decode_contents()  # Keep raw content, no cleaning
        username = resolve_author(username)
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
        return

    # Add the raw content to the global array
    audio_metadata.append([username, title, description, playcount, audio_filename])

    print(f"Current audio_metadata array: {audio_metadata}")

HANDLERS["soundgasm"] = get_metadata_soundgasm


#=======================================================================
# Whyp handler (yt-dlp for cloudflare-protected sites)
# requires yt-dlp on PATH
#=======================================================================
def get_metadata_whyp(url):
    if shutil.which("yt-dlp") is None:
        print("ERROR: yt-dlp not found on PATH.")
        print("  Install it:  pip install yt-dlp  (or grab the binary)")
        return

    # =======================================================================
    # Get metadata via yt-dlp JSON dump (no download yet, -j is simulate only)
    print("Fetching metadata via yt-dlp...")
    meta_result = subprocess.run(
        ["yt-dlp", "-j", url],
        capture_output=True, text=True
    )

    if meta_result.returncode != 0:
        print(f"yt-dlp metadata extraction failed:\n{meta_result.stderr}")
        return

    info = json.loads(meta_result.stdout)

    username = info.get("uploader", "unknown_whyp_user")
    username = resolve_author(username)
    title = info.get("title", "No title found")
    description = info.get("description") or "No description found"

    # whyp doesn't expose play counts via yt-dlp, so this will usually miss
    view_count = info.get("view_count")
    playcount = str(view_count) if view_count is not None else "No playcount found"

    # =======================================================================
    # Extract the CDN hash filename from the url field, same style as soundgasm
    # e.g. "https://cdn.whyp.it/3c3b23bc-8f74-4cc1-8dae-0f1b4b32a354.mp3?token=..."
    #  -> "3c3b23bc-8f74-4cc1-8dae-0f1b4b32a354.mp3"
    cdn_url = info.get("url", "")
    cdn_match = re.search(r'/([a-f0-9-]+\.\w+)\?', cdn_url)
    if cdn_match:
        audio_filename = cdn_match.group(1)
    else:
        # fallback to track ID if CDN URL doesn't match expected pattern
        track_id = str(info.get("id", "unknown"))
        ext = info.get("ext", "mp3")
        audio_filename = f"{track_id}.{ext}"
        print(f"Warning: couldn't extract CDN hash, falling back to {audio_filename}")

    print(f"Extracted Username: {username}")
    print(f"Extracted Title: {title}")
    print(f"Extracted Description: {description[:100]}...")
    print(f"Extracted Playcount: {playcount}")
    print(f"Extracted Audio Filename: {audio_filename}")

    # =======================================================================
    # Download the audio file via yt-dlp
    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)

    output_path = os.path.join(media_dir, audio_filename)

    if os.path.exists(output_path):
        print(f"File already exists: {output_path}. Skipping download.")
    else:
        print(f"Downloading audio to {media_dir}...")
        dl_result = subprocess.run(
            ["yt-dlp", "-o", output_path, url],
            capture_output=True, text=True
        )

        if dl_result.returncode != 0:
            print(f"yt-dlp download failed:\n{dl_result.stderr}")
            return

        print(f"Downloaded audio file: {output_path}")

    # Add the raw content to the global array
    audio_metadata.append([username, title, description, playcount, audio_filename])

    print(f"Current audio_metadata array: {audio_metadata}")

HANDLERS["whyp"] = get_metadata_whyp

#=======================================================================
# Audiochan handler (gallery-dl for download + metadata)
# requires gallery-dl on PATH
#=======================================================================
def get_metadata_audiochan(url):
    if shutil.which("gallery-dl") is None:
        print("ERROR: gallery-dl not found on PATH.")
        print("  Install it:  pip install gallery-dl  (or grab the binary)")
        return

    # =======================================================================
    # Get metadata via gallery-dl JSON dump (no download yet)
    print("Fetching metadata via gallery-dl...")
    meta_result = subprocess.run(
        ["gallery-dl", "-j", url],
        capture_output=True, text=True
    )

    if meta_result.returncode != 0:
        print(f"gallery-dl metadata extraction failed:\n{meta_result.stderr}")
        return

    # gallery-dl -j returns one big pretty-printed JSON array
    try:
        entries = json.loads(meta_result.stdout)
    except json.JSONDecodeError as e:
        print(f"Could not parse gallery-dl JSON output: {e}")
        print(f"Raw output:\n{meta_result.stdout[:500]}")
        return

    info = None
    for entry in entries:
        if not isinstance(entry, list) or len(entry) < 2:
            continue
        if entry[0] == 3 and len(entry) >= 3:
            info = entry[2]
            break
        elif entry[0] == 2 and info is None:
            info = entry[1]

    if info is None:
        print("Could not extract metadata from gallery-dl output.")
        print(f"Raw output:\n{meta_result.stdout[:500]}")
        return

    # =======================================================================
    # Extract metadata using exact audiochan field names
    user_obj = info.get("user") or {}
    username = user_obj.get("username") or user_obj.get("display_name") or "unknown_audiochan_user"
    username = resolve_author(username)

    title = info.get("title") or "No title found"

    # description is a list of strings on audiochan
    desc_raw = info.get("description")
    if isinstance(desc_raw, list):
        description = "\n".join(desc_raw)
    elif isinstance(desc_raw, str):
        description = desc_raw
    else:
        description = "No description found"

    # valid_listens is total all-time listens
    listen_count = info.get("valid_listens")
    playcount = str(listen_count) if listen_count is not None else "No playcount found"

    # slug is the unique track ID in the URL, extension comes from the type-3 entry
    slug = info.get("slug") or str(info.get("id", "unknown"))
    ext = info.get("extension") or "mp3"
    audio_filename = f"{slug}.{ext}"

    print(f"Extracted Username: {username}")
    print(f"Extracted Title: {title}")
    print(f"Extracted Description: {description[:100]}...")
    print(f"Extracted Playcount: {playcount}")
    print(f"Extracted Audio Filename: {audio_filename}")

    # =======================================================================
    # Download the audio file via gallery-dl
    media_dir = f"./media/{username}"
    os.makedirs(media_dir, exist_ok=True)

    output_path = os.path.join(media_dir, audio_filename)

    if os.path.exists(output_path):
        print(f"File already exists: {output_path}. Skipping download.")
    else:
        print(f"Downloading audio to {media_dir}...")
        dl_result = subprocess.run(
            [
                "gallery-dl",
                "-d", ".",
                "-o", f'directory=["media", "{username}"]',
                "-o", f'filename={slug}.{{extension}}',
                url,
            ],
            capture_output=True, text=True
        )

        if dl_result.returncode != 0:
            print(f"gallery-dl download failed:\n{dl_result.stderr}")
            return

        # if gallery-dl ignored our output overrides, hunt for the file
        if not os.path.exists(output_path):
            import glob
            # check gallery-dl's default tree
            default_dir = os.path.join(".", "gallery-dl", "audiochan", username)
            candidates = glob.glob(os.path.join(default_dir, "*"))
            if candidates:
                actual = max(candidates, key=os.path.getmtime)
                dest = os.path.join(media_dir, audio_filename)
                shutil.move(actual, dest)
                print(f"Moved {actual} -> {dest}")
            else:
                print(f"Warning: could not locate downloaded file.")
                print(f"gallery-dl stdout:\n{dl_result.stdout}")
                return

        print(f"Downloaded audio file: {output_path}")

    # Add the raw content to the global array
    audio_metadata.append([username, title, description, playcount, audio_filename])

    print(f"Current audio_metadata array: {audio_metadata}")

HANDLERS["audiochan"] = get_metadata_audiochan

# Helper function to extract existing audio filenames for a user from YAML
def get_existing_user_audios(yaml_content, username):
    """Extract all audio filenames for a specific user from YAML content"""
    audio_pattern = rf"  {re.escape(username)}:.*?(?=\n  \w+:|\Z)"
    user_section = re.search(audio_pattern, yaml_content, re.DOTALL)
    
    if not user_section:
        return []
    
    # Find all audio filenames in this user's section
    audio_files = re.findall(r"audio: '([^']+)'", user_section.group(0))
    return audio_files


# Helper function to extract existing titles for a user from YAML
def get_existing_user_titles(yaml_content, username):
    """Extract all titles for a specific user from YAML content"""
    audio_pattern = rf"  {re.escape(username)}:.*?(?=\n  \w+:|\Z)"
    user_section = re.search(audio_pattern, yaml_content, re.DOTALL)

    if not user_section:
        return []

    titles = []

    # Format 1: title: | (pipe format - multi-line)
    #           multi-line content
    title_pattern_pipe = r"title: \|\n\s+(.+?)(?=\n\s+description:)"
    for match in re.finditer(title_pattern_pipe, user_section.group(0), re.DOTALL):
        title = match.group(1).strip()
        titles.append(title)

    # Format 2: title: 'inline string' (single-line quoted format)
    title_pattern_inline = r"title: '([^']+)'"
    for match in re.finditer(title_pattern_inline, user_section.group(0)):
        title = match.group(1)
        titles.append(title)

    return titles


# Helper function to modify title by repeating last letter
def modify_duplicate_title(title):
    """Add one extra letter that repeats the last letter of the title"""
    if title and len(title) > 0:
        # Get the last character (could be HTML entity or regular character)
        # Strip to handle any trailing whitespace
        title_stripped = title.rstrip()
        if title_stripped:
            last_char = title_stripped[-1]
            return title_stripped + last_char
    return title


# Step 3: Save the metadata to the YAML file
def save_metadata_to_yaml():
    # Open the existing YAML file 
    with open(YAML_FILE, "r", encoding="utf-8") as file:
        yaml_content = file.read()

    # Process each entry in metadata
    for entry in audio_metadata:
        username, title, description, playcount, audio_filename = entry

        # Check if the audio file already exists for this user (true duplicate)
        existing_audios = get_existing_user_audios(yaml_content, username)
        
        if audio_filename in existing_audios:
            print(f"Audio '{audio_filename}' already exists for {username}. Skipping...")
            continue
        
        # Audio is unique, now check if title is duplicate within same user
        existing_titles = get_existing_user_titles(yaml_content, username)
        original_title = title
        
        if title in existing_titles:
            title = modify_duplicate_title(title)
            print(f"Title '{original_title}' already exists for {username}. Modified to '{title}'")

        # Fix indentation for the description
        description = "\n".join(["        " + line if line.strip() else "" for line in description.splitlines()])

        # Check if the user exists in the file
        if f"  {username}:" not in yaml_content:
            # If the user doesn't exist, create the user entry
            yaml_content += f"\n  {username}:\n"
        
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
        if playcount_value.isdigit() or playcount_value in replacements:
            return match.group(0)  # If the playcount is a number (or already got unicoded), leave it unchanged
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


urls = [
    # soundgasm example:
    # "https://soundgasm.net/u/sinthyasanguine/some-audio-title",
    # whyp example:
    # "https://whyp.it/tracks/349458/f4m-skitty-wants-to-play-with-her-fav-toy-you-lubey-handjob-gentle-needy",
    "https://audiochan.com/a/nCj5FelUwcXTJOMrFL"
]

for url in urls:
    get_metadata(url)

save_metadata_to_yaml()
postprocess_playcount_in_yaml()

# things of note:
# it is worth updating IvyWilde once in a while
# full archive of skittykat (including swf and ph) and behold-the-beauty
# partial archive, if at all, of notable audios of pillowasmr whatever it was called, and belle-in-the-woods
# it is worth archiving bumbledee audios from youtube with ffmpeg