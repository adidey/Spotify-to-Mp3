# Spotify to MP3 Converter

This program allows you to download songs from your Spotify playlist as MP3 files.  It leverages the `spotipy` library to interact with the Spotify API and other libraries for downloading and converting audio.

## Requirements

* **Python 3.7+:**  Ensure you have Python 3.7 or higher installed.
* **`spotipy`:** Install using `pip install spotipy`
* **`youtube-dl`:** Install using `pip install youtube-dl` (or `pip install yt-dlp` for a more actively maintained fork)
* **`ffmpeg`:** You'll need `ffmpeg` installed on your system.  Download it from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and make sure it's added to your system's PATH environment variable.

## Usage

1. **Authentication:** You'll need a Spotify account and create a Spotify developer application to obtain a client ID and client secret.  The program will guide you through the authentication process.
2. **Playlist Selection:** Choose the Spotify playlist you want to convert.
3. **Download:** The program will download the tracks from your selected playlist and convert them to MP3 files.

## Disclaimer
This program is for personal, non-commercial use only. Downloading copyrighted music without permission is illegal.  Use this tool responsibly and respect copyright laws.


