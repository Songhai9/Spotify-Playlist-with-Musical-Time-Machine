# Imports
from datetime import datetime
from http.client import responses
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests

# Getting Environment Value
load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Spotipy Authentication
scope = "playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    cache_path='token.txt',
    username='kana.maiga')
)
user_id = sp.current_user()['id']

# Getting the desired year for the user
while True:
    date_str = input("Which year do you want to travel to? Type the date in this format : YYYY-MM-DD: ")

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        break
    except ValueError:
        print('Invalid date format, please enter the date in YYYY-MM-DD format.')

# Scraping the webpage
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
URL = f'https://www.billboard.com/charts/hot-100/{date_str}'
response = requests.get(URL, headers=header)
chart_webpage = response.text
soup = BeautifulSoup(chart_webpage, 'html.parser')
song_titles = soup.find_all(name="h3",
                            class_="a-no-trucate", id="title-of-a-story")
songs = [song.getText().replace('\t', '').replace('\n', '') for song in song_titles]

# Creating the playlist
songs_uri = []
year = date_str.split('-')[0]
for song in songs:
    result = sp.search(q=f"track:{song}, year:{year}", type="track")

    try:
        uri = result['tracks']['items'][0]['uri']
        songs_uri.append(uri)
    except IndexError:
        print("Song doesn't exist, skipping to the next one")
playlist = sp.user_playlist_create(user=user_id,
                                   name=f'{date_str} Billboard 100',
                                   public=False)
playlist_id = playlist['id']

sp.playlist_add_items(playlist_id=playlist_id,
                      items=songs_uri)
