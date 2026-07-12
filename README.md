## Overview

This is a badly copied over soundgasm.net mirror, with simulation of loading times/views/form submissions compared to the actual site. However it should work for local safekeeping or whatever. When building locally, change `baseurl: ''` in `_config.yml` to your custom baseurl, typically its just empty.

You can look over all the html files in the root and `/u/`, `/passwordreset/`, as they are all just custom coded templates that I copied over and modified. In particular, `index.html` on the root is changed to display all users.

`/assets/` contains all the website css/images/js whatever, ideally don't change that. 

`/media/` contains your actual audio files, which I've changed from what the actual site does (a database of `some-hash.m4a`) to `/username/some-hash.m4a` to be more organized. Yes, there are audios in there already from me testing this lmao 👀<sup>☣☣</sup>

`/_layouts/` contains the user profile layout, as well as the audio entry layouts. In these templates, note that `{{ "[link]" | relative_url }}` does the same thing as using `{{ site.baseurl }}`.

`/_data/` contains a `audio_data.yml` file (which already has entries corresponding to the stuff I was testing in `/media/`) which lists out all the actually important data in organization of
```yaml
users:
  [username]:
    - title: [title]
      description: [description]
      playcount: [playcount]
      audio: [audio]
```
which is used to dynamically generate user and audio pages by the two ruby scripts in `/_plugins/`. I've commentated the audio page one, and the user one is similar so shouldn't be that hard to understand (plus its like half GPT generated lol). There's a `audio_data.yml.bak` backup file because I was trying to mass-add stuff with python scripts (which I was too lazy to remove since they might come in handy later).

If an audio's name or description is annoying (i.e. has characters that don't escape well or is too long/more than one line), you can simply do as follows:
```yaml
users:
  [username]:
    - title: |
        [title]
      description: |
        [description]
      playcount: [playcount]
      audio: [audio]
```

When you want to add an audio to the archive, simply update `audio_data.yml` with the neccesary data (and backup beforehand when using scripts as desired), and add the audio file to `/media/[user]/`. Audio titles should be unique, and if they aren't, simply add something to make it unique (e.g. `audio title` vs `audio titlee` *cough cough ivywilde moment*).

When audios are privated, you are unable to access the `playcount`, so I just put some random unicode character or whatever as a replacement in `audio_data.yml`. Some examples are below:
1. ﷽
2. 𒐫
3. 𒈙
4. ꧅

I should uh note that my live demo I have set up has uh... interestingly been indexed by google, which is not ideal lmao, so I have added noindex tags to all the html pages hopefully to prevent this from happenning in the future. Apparently subdomains are publicly announced lol Actual bruh moment

## Auto-archiving Audio

The old `archiving.py` got replaced with a whole package in `Utilities/` which does the same thing (scrape metadata + download audio + update `audio_data.yml`) but now supports soundgasm, whyp, audiochan, and hotaudio with separate handler modules. Still probably buggy tbh, always keep `audio_data.yml.bak` around before running. This makes the archiver universal (at least for the current sites I see being used on r/GWA). It's dependent on 3rd party tools (`yt-dlp`, `gallery-dl`, and `playwright`), and if they (`yt-dlp` and `gallery-dl` in particular) break, then the archiver will break too and I'll have to update the script, but man i sure hope not lmao i am too lazy 🥱🥱🥱

To run it, either do on the commandline
```bash
python -m Utilities.run
```
or run from VSC via `Ctrl+Shift+D`, select "Run Archiver", then click run. You can figure out how to run on another IDE if you use something different since I can't be assed to make support universal so womp womp ig? And bec I don't want to have a `__main__.py`, I've included the custom `.vscode/launch.json` so VSC knows what to do without a main (there's the normal "Python: Current File" you use on `/Utilities/index.py` and `/Utilities/review.py`, and the "Run Archiver" which you use on `/Utilities/run.py`). Normally IDE configs should be on the gitignore, but this is a personal project and I've deemed it helpful enough for anyone who runs VSC to have, so here it is. If you don't use VSC, just ignore/delete it.

Edit the `urls` list at the top of `/Utilities/run.py` with whatever you want to archive. It auto-detects which site each URL belongs to:
```python
urls = [
    "https://soundgasm.net/u/someone/some-audio",
    "https://whyp.it/tracks/12345/some-track",
    "https://audiochan.com/a/some-random-audio",
    "https://hotaudio.net/u/someone/some-audio",           # 2x speed by default
    ("https://hotaudio.net/u/someone/other-audio", 1.0),   # tuple to override speed
]
```

There are several requirements needed to actually run the thing (if you couldn't tell already) since I'm using 3rd party tools and python libraries ofc. By default, we need
```bash
pip install requests beautifulsoup4
```
Each handler then has its own dependencies, and if something's missing, that handler just gets skipped and everything else still works. They are as follows, 
- **soundgasm**: just requests + bs4, nothing extra
- **whyp**: needs `yt-dlp` on PATH
- **audiochan**: needs `gallery-dl` on PATH
- **hotaudio**: `pip install playwright` then `playwright install chromium`

Hotaudio opens an actual browser window and plays the audio in real-time to capture it (it hooks into the browser's MediaSource API to intercept decrypted chunks as the site encrypts everything so you can't just download the file directly aka the site dev's a goofy person who tried to make a trivially bypassable JS "DRM" lolmao). A 20min track at 2x speed takes ~10min to download. *Don't minimize the Chrome window* or it throttles playback, but you can alt-tab away from it.

Note that because hotaudio might have some detection for bots or whatever, I'm using a persistent Chrome profile for playwright at `~/.hotaudio_profile` (this is basically `%USERPROFILE%/.hotaudio_profile`) so the site sees a consistent browser fingerprint across runs. You can delete it to start fresh if anything gets weird, but the main thing to note is that this file is created **OUTSIDE OF THE ACTUAL REPO ITSELF**, so beware of this. What I know for sure tho is that hotaudio detects abnormal behavior speedwise (i tested this) and will effectively ip ban people, so ngl don't try to run this above 2x speed lmao (plus there's audio artifacts anyways if you go above 2x).

Overall though, this entire thing works the same way as the old script but split into pieces:

1. Check for `_data/audio_data.yml`, creates it if missing
2. For each URL, detects the site, scrapes metadata (username, title, description, playcount), downloads the audio to `./media/{username}/`
3. Writes everything to the YAML, but skips files that already exist for a user, disambiguates duplicate titles by repeating the last character (*cough cough ivywilde moment*)
4. Post-processes playcounts by replacing any non-numeric ones with random unicode characters from the replacements list (﷽, 𒐫, ඞ, zalgo text, etc)

Console output is color-coded so you can actually spot problems when batch-archiving 20 URLs at once. Green ✓ for stuff that worked, yellow ⚠ for missing fields (no playcount, no description, etc), red ✗ for actual errors. This console logging mechanism is AI generated if you couldn't tell from the untypable unicode already 🥀

For reference, here are unicode chars you can use for the replacements array: https://www.reddit.com/r/Unicode/comments/5qa7e7/widestlongest_unicode_characters_list/

## Building

Locally, (assuming you have Jerkyll and bundler installed, if not, do that) you can just run 
```bash
bundle install
```
when setting it up for the first time.

Then, you can build and serve the website locally via
```bash
bundle exec jekyll build
bundle exec jekyll serve
```

When installing Jerkyll, don't make the mistake of not using Chocolatey.

If you want to host on a domain do your own shennaingans set up CNAME/server whatever but since its static you can just stick with github pages, its free lmao.

Have fun ig :3

## Space Considerations

As you know, media files can become large. Eventually if you are actually serving this online like I am, it may be worthwhile to convert the audio files into a more efficient encoding like opus from what they are now (mainly 128kbps aac and 192kbps mp3). I've testd aac with opus and 128kbps → 128kbps still decreases file size lol. You can check the largest media files with `/Utilities/index.py` which will output a list of audio ranked by file size in the `/media/` folder.

Since lossy → lossy conversion is... lossy<sup><small>[citation needed]</small></sup>, do be careful with the bitrates. I would recommend for ~128kbps aac files to be converted into 112-128kbps opus files, and ~192kbps mp3s to be converted into 128kbps opus files. This minimizes generation loss, and likely maintains a wide transparency margin. If the audio has lower bitrate than my aforementioned specifications, it would not be worthwhile to convert them into opus due to high generation loss. You should definetely compare the two audios side by side to see it's transparent or not. If you dont hear any difference, then might as well convert right? :)

I further recommend only converting files larger than 20-30MB to opus format, as for smaller files it is not worth it tbh. I say this but tbh I'm not gonna do this for now as I'll like to maintain original audio quality as much as possible and my site compilation runner vm still has enough space lmao so whatever

<sup><sub>I wish soundgasm served FLAC files ngl smh</sub></sup>

**ALSO**, it is quite important that you **archive only the audios that you actually <u>use</u>/want to keep**. While having a datahoarding mindset is good for preservation, sometimes it is important to question the necessity of archiving only for the purpose of archiving (and not actually using). I've structured this site as an archive that serves personal use with expectation that you actually play the audios you archive, so it would serve you well to use it for such!!!, and not just one-off audios that you will never play again. I have an additional script in `/Utilities/review.py` helps you do this. Ofc, this is a personal opinion so make of it as you will but please do keep it in mind :)

### <sup>☣☣</sup>Note

Note I'm quite literally going to use this as my own archive btw so this repo might get bloated from `/media/` :3

Might be worth using sparse checkout to avoid everything in `/media/` for quicker cloning. Unless you want to see what I've archived ;)

![imagine not loading the image](https://github.com/user-attachments/assets/e006518f-f2eb-40c1-a2bf-2b5fd5fcc6c5)
