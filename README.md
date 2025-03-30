## Overview

This is a badly copied over soundgasm.net mirror, with simulation of loading times/views/form submissions compared to the actual site. However it should work for local safekeeping or whatever. When building locally, change `baseurl: '/soundgasm.net-jerkyll-mirror'` in `_config.yml` to your custom baseurl, typically its just empty.

You can look over all the html files in the root and `/u/`, `/passwordreset/`, as they are all just custom coded templates that I copied over and modified. In particular, `index.html` on the root is changed to display all users.

`/assets/` contains all the website css/images/js whatever, ideally don't change that.

`/media/` contains your actual audio files, which I've changed from what the actual site does (a database of `some-hash.m4a`) to `/username/some-hash.m4a` to be more organized. Yes, there are audios in there already from me testing this lmao 👀
<sup>☣☣</sup>

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

If an audio's name or description is annoying (i.e. has characters that don't escape well or is too long), you can simply do as follows:
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

When you want to add an audio to the archive, simply update `audio_data.yml` with the neccesary data (and backup beforehand when using scripts as desired), and add the audio file to `/media/[user]/`. 

When audios are privated, you are unable to access the `playcount`, so I just put some random unicode character or whatever as a replacement in `audio_data.yml`. Some examples are below:
1. ﷽
2. 𒐫
3. 𒈙
4. ⸻
5. ꧅

Should note that in `_config.yml` technically you really don't need to include
```yaml
collections:
  audio_entries:
    output: true
    permalink: "{{ site.baseurl }}/u/:path/:title.html"
```
since this is always overridden by the scripts in `/_plugins/`, but I kept it in anyways whatever.

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

### <sup>☣☣</sup>Note
I'm quite literally going to use this as my own archive btw so this repo might get bloated from `/media/` :3
![imagine not loading the image](https://private-user-images.githubusercontent.com/70708832/428362692-e006518f-f2eb-40c1-a2bf-2b5fd5fcc6c5.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDMyOTUzODIsIm5iZiI6MTc0MzI5NTA4MiwicGF0aCI6Ii83MDcwODgzMi80MjgzNjI2OTItZTAwNjUxOGYtZjJlYi00MGMxLWEyYmYtMmI1ZmQ1ZmNjNmM1LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMzAlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzMwVDAwMzgwMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTZkOTAxNDc4M2Q4ZDFhNzJkODU5MWQ2OWY5NGE4ZGM2ZDgzNjJiNWZlOWVlMTcxMmUzNmE5MzI4M2Q1MjFiZDAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rnQ08EiCEPzXTcYiKxh3nl_A7FlLSQpUgprFLp5Ae3c)
