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

I spent some time writing (50% GPT again lmao) `archiving.py`, which automatically updates `audio_data.yml` with metadata and saves the audio, given a soundgasm link. It may be buggy, use with care. Always use the backup file `audio_data.yml.bak` before running the script. 

How it works:
We first check if the yaml file (audio_data.yml) exists, creating it if necessary. We then fetch the username, title, description, playcount, and audio file link. We download the audio file and stores it in a designated directory for the user. The metadata (username, title, description, playcount, and filename) is added to an array and subsequently saved into the yaml file. The playcount is post-processed to replace non-numeric values with random characters from our random unicode list, and then we write the yaml file back to the disk

For reference, here are unicode chars you can use for the replacements array: https://www.reddit.com/r/Unicode/comments/5qa7e7/widestlongest_unicode_characters_list/

## Building

Locally, (assuming you have Jerkyll and bundler installed, if not, do that) you can just run 
```
bundle install
```
when setting it up for the first time.

Then, you can build and serve the website locally via
```cmd
bundle exec jekyll build
bundle exec jekyll serve
```

When installing Jerkyll, don't make the mistake of not using Chocolatey.

If you want to host on a domain do your own shennaingans set up CNAME/server whatever but since its static you can just stick with github pages, its free lmao.

Have fun ig :3

## Space Considerations

As you know, media files can become large. Eventually if you are actually serving this online like I am, it may be worthwhile to convert the audio files into a more efficient encoding like opus from what they are now (mainly 128kbps aac and 192kbps mp3). I've testd aac with opus and 128kbps → 128kbps still decreases file size lol. You can check the largest media files with `index.py` which will output a list of audio ranked by file size in the `/media/` folder.

Since lossy → lossy conversion is... lossy<sup><small>[citation needed]</small></sup>, do be careful with the bitrates. I would recommend for ~128kbps aac files to be converted into 112-128kbps opus files, and ~192kbps mp3s to be converted into 128kbps opus files. This minimizes generation loss, and likely maintains a wide transparency margin. If the audio has lower bitrate than my aforementioned specifications, it would not be worthwhile to convert them into opus due to high generation loss.

I further recommend only converting files larger than 20-30MB to opus format, as for smaller files it is not worth it tbh. I say this but tbh I'm not gonna do this for now as I'll like to maintain original audio quality as much as possible and my site compilation runner vm still has enough space lmao so whatever

<sup><sub>I wish soundgasm served FLAC files ngl smh</sub></sup>

### <sup>☣☣</sup>Note

Note I'm quite literally going to use this as my own archive btw so this repo might get bloated from `/media/` :3

Might be worth using sparse checkout to avoid everything in `/media/` for quicker cloning. Unless you want to see what I've archived ;)

![imagine not loading the image](https://github.com/user-attachments/assets/e006518f-f2eb-40c1-a2bf-2b5fd5fcc6c5)
