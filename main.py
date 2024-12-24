import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
import subprocess
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from PIL import ImageTk, Image
from io import BytesIO

# Spotify API Setup
SPOTIFY_CLIENT_ID = 'CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'SECRET'
SPOTIFY_REDIRECT_URI = 'URI'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private"
))

# YouTube API Setup
YOUTUBE_API_KEY = 'YOUTUBE_API_KEY'
youtube = build('youtube', 'v3', developerKey='YOUTUBE API ID')

# Function to search for a song on Spotify
def search_spotify(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        album_art_url = track['album']['images'][0]['url']  # Get highest res image
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'duration_ms': track['duration_ms'] // 1000,
            'album_art': album_art_url
        }
    return None

# Function to search YouTube for the song
def search_youtube(song_name, artist):
    query = f"{song_name} {artist} official audio"
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        return f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
    return None

# Function to download audio using yt-dlp
def download_audio(youtube_url, spotify_data, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    command = [
        'yt-dlp',
        '-x', '--audio-format', 'mp3',
        '--embed-thumbnail', # Embed thumbnail in metadata (if available)
        '--output', f"{output_path}/%(title)s.%(ext)s",
        youtube_url
    ]
    subprocess.run(command)
    if spotify_data and spotify_data.get('album_art'):
        try:
            response = requests.get(spotify_data['album_art'])
            response.raise_for_status() # Raise an exception for bad status codes
            image = Image.open(BytesIO(response.content))
            image.save(f"{output_path}/{spotify_data['name']}.jpg")  # Save as jpg
        except requests.exceptions.RequestException as e:
            print(f"Error downloading album art: {e}")

# Function to fetch user's playlists
def get_user_playlists():
    playlists = sp.current_user_playlists()
    return {item['name']: item['id'] for item in playlists['items']}

# Function to process tracks from a playlist
def process_playlist(playlist_id):
    tracks = sp.playlist_tracks(playlist_id)['items'] 
    for item in tracks:
        track = item['track']
        artist_name = track['artists'][0]['name']
        song_name = track['name']

        spotify_data = search_spotify(song_name, artist_name)
        if spotify_data:
            youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])
            if youtube_url:
                download_audio(youtube_url, spotify_data)

class SpotifyDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spotify to MP3 Downloader")
        self.setGeometry(100, 100, 500, 300)

        self.layout = QVBoxLayout()

        # Fetch Playlists Section
        self.playlist_label = QLabel("Spotify Playlists:")
        self.layout.addWidget(self.playlist_label)

        self.playlist_combo = QComboBox(self)
        self.playlist_combo.addItem("Fetching playlists...")
        self.layout.addWidget(self.playlist_combo)

        self.fetch_button = QPushButton("Fetch Playlists", self)
        self.fetch_button.clicked.connect(self.fetch_playlists)
        self.layout.addWidget(self.fetch_button)

        self.download_playlist_button = QPushButton("Download Playlist", self)
        self.download_playlist_button.clicked.connect(self.download_playlist)
        self.layout.addWidget(self.download_playlist_button)

        # Individual Song Download Section
        self.song_label = QLabel("Download Individual Song:")
        self.layout.addWidget(self.song_label)

        self.song_name_label = QLabel("Song Name:")
        self.layout.addWidget(self.song_name_label)

        self.song_name_input = QLineEdit(self)
        self.layout.addWidget(self.song_name_input)

        self.artist_name_label = QLabel("Artist Name:")
        self.layout.addWidget(self.artist_name_label)

        self.artist_name_input = QLineEdit(self)
        self.layout.addWidget(self.artist_name_input)

        self.individual_download_button = QPushButton("Download Song", self)
        self.individual_download_button.clicked.connect(self.download_individual_song)
        self.layout.addWidget(self.individual_download_button)

        self.setLayout(self.layout)

        self.user_playlists = {}

    def fetch_playlists(self):
        playlists = get_user_playlists()
        self.playlist_combo.clear()
        self.playlist_combo.addItem("Select a playlist")
        for name in playlists.keys():
            self.playlist_combo.addItem(name)
        self.user_playlists = playlists

    def download_playlist(self):
        selected_playlist = self.playlist_combo.currentText()
        if selected_playlist == "Select a playlist":
            self.show_message("Error", "Please select a playlist.")
            return

        playlist_id = self.user_playlists[selected_playlist]
        process_playlist(playlist_id)
        self.show_message("Success", "Playlist processed and downloads complete!")

    def download_individual_song(self):
        song_name = self.song_name_input.text()
        artist_name = self.artist_name_input.text()
        if not song_name or not artist_name:
            self.show_message("Error", "Please enter both song name and artist name.")
            return
        spotify_data = search_spotify(song_name, artist_name)
        if spotify_data:
            youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])
            if youtube_url:
                download_audio(youtube_url, spotify_data)
                self.show_message("Success", "Download complete!")
            else:
                self.show_message("Error", "Song not found on YouTube.")
        else:
            self.show_message("Error", "Song not found on Spotify.")

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpotifyDownloaderApp()
    window.show()
    sys.exit(app.exec_())
