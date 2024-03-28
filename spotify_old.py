import requests
import json
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

spotify_id = "1139834868"
client_id = "ba32f9dbf1644ead9041791489e0425d"
client_secret = "4f106a2de01d4b32ae37dd08345b1fd9"
callback_uri = "http://localhost:8888/callback"


def get_bearer_token():
    url = 'https://accounts.spotify.com/api/token'
    payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    r = requests.post(url, data=payload, headers=headers)

    print(r.json()['access_token'])
    access_token = r.json()['access_token']

    return access_token

def create_playlist():
    access_token = get_bearer_token()
    url = f"https://api.spotify.com/v1/users/{spotify_id}/playlists"
    headers = {
        "Authorization":f"Bearer {access_token}",
        "Content-Type":"application/json"
        }
    payload = {
        "name":"Youtube2Spotify",
        "description":"Created by the Youtube2Spotify App.",
        "public":"false"
    }
    r = requests.post(url, data=payload, headers=headers)

    print(r.json())

def authenticate_spotify():
    # Open the browser to Spotify's authentication endpoint
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={callback_uri}&scope=playlist-modify-private&show_dialog=True"
    webbrowser.open(auth_url)

def test():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=callback_uri,
                                                   scope="playlist-modify-private",
                                                   show_dialog=True))
    
    authenticate_spotify()

    results = sp.user_playlist_create(
        user=spotify_id,
        name="Youtube2Spotify",
        public=False,
        description="Created by the YouTube2Spotify App."
    )

    print(results.json())
#WIP -> Find a way to make the spotify api call the backend (python) so it gets redirected correctly -> check Chat GPT
test()
