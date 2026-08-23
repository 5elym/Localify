# README

Localify is a wrapper for yt-dlp that is specifically for downloading songs from YouTube and allowing them to be
seamlessly added to Spotify via its Local Files feature

## Features

- Simple command to download audio from a YouTube link without complicated CLI arguments.
- Cleans titles when possible to show just artist and song title.
- Adds metadata to mp3 files so that it is recognised in Spotify.
- Can be used to just simply download songs from YouTube.

## Dependencies

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) - Core engine that downloads the audio from YouTube.
- [`ffmpeg`](https://github.com/yt-dlp/yt-dlp#dependencies) - Dependency for yt-dlp that adds postprocessing to the downloaded audio.
- [`mutagen`](https://github.com/quodlibet/mutagen) - Used to add/modify metadata tags to the downloaded audio file.

## Commands

- `lcfy [LINK]` - Downloads and processes audio from LINK and saves it to default folder (must be set first).
- `lcfy [LINK] -s [FILEPATH]` - Downloads and processes audio from LINK and saves it to the specified folder in FILEPATH.
- `lcfy -d [FILEPATH]` - Sets the default folder specified in FILEPATH.
- `lcfy -f` - Prints the default FILEPATH that was saved.
- `lcfy -h` - Prints help dialogue.
