import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv("venv/.env")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://example.com"

scope = "user-library-read,playlist-modify-private,user-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI, scope=scope))
user_id = sp.current_user()["id"]

date = input("What date would you like to travel to? (YYYY-MM-DD): ")
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}")
response.raise_for_status()
website = response.text
soup = BeautifulSoup(website, "html.parser")
chart = soup.find(name="div", class_="chart-results-list")
top_artist = chart.find(class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet")
song_artists = chart.find_all(class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")
song_titles = chart.select(selector="li h3")

songs = []
artists = [top_artist.get_text().strip()]
track_ids = []

for item in song_artists:
    artists.append(item.get_text().strip())

for item in song_titles:
    songs.append(item.get_text().strip())

for song in songs:
    track = song
    artist = artists[songs.index(track)]
    results = sp.search(q=f"track: {track}, artist: {artist}", type="track", limit=4)
    # artist_id = results["tracks"]["items"][0]["artists"]
    try:
        track_id = results["tracks"]["items"][0]["id"]
        track_ids.append(track_id)
    except ValueError:
        pass

playlist_id = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=track_ids)

