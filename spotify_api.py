import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

spotify_id = os.getenv('SPOTIFY_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')

access_token = None
sp_oauth = None
callback_received = False

def authenticate_spotify():
    global sp_oauth
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-modify-public playlist-modify-private"
    )

    # Open the browser to Spotify's authentication endpoint
    auth_url = sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)

    while not callback_received:
        time.sleep(1)

    return spotipy.Spotify(auth_manager=sp_oauth)


def create_playlist(sp):
    # Create a playlist
    try:
        results = sp.user_playlist_create(
            user=spotify_id,
            name="Youtube2Spotify",
            public=False,
            description="Created by the YouTube2Spotify App."
        )
        print("Playlist created successfully:", results)
        return results
    except Exception as e:
        print("Error creating playlist:", e)
        return None


def filter_for_title():
    titles = []
    with open("output/playlistitems.json", "r") as f:
        data = json.load(f)  # Load the entire JSON data
        for item in data:
            title = item.get("title")
            if title:
                titles.append(title)
    
    print("Extracted titles:", titles)
    return titles


def search_spotify(sp, title):
    results = sp.search(q=title, type='track')
    if results['tracks']['items']:
        spotify_uri = results['tracks']['items'][0]['uri']
        return spotify_uri
    else:
        print(f"No tracks found for title: {title}")
        return None
    

def search_titles_in_spotify(sp, titles):
    spotify_uris = {}
    for title in titles:
        spotify_uri = search_spotify(sp, title)
        if spotify_uri:
            spotify_uris[title] = spotify_uri
    return spotify_uris


def add_tracks_to_playlist(sp, spotify_uris_dict, playlist_id):
    spotify_uris = list(spotify_uris_dict.values())
    
    # Batch tracks in groups of 100 due to API limits
    batch_size = 100
    for i in range(0, len(spotify_uris), batch_size):
        try:
            sp.playlist_add_items(playlist_id, spotify_uris[i:i + batch_size])
            print(f"Batch {i//batch_size + 1} added successfully!")
        except Exception as e:
            print(f"Failed to add batch {i//batch_size + 1}: {e}")


def run_http_server():
    class SpotifyAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            global access_token, callback_received, sp_oauth

            if self.path.startswith("/callback"):
                # Extract the authorization code from the callback URI
                authorization_code = self.path.split("=")[1]

                # Exchange the authorization code for an access token
                token_info = sp_oauth.get_access_token(authorization_code)

                # Update the global access token
                access_token = token_info["access_token"]
                callback_received = True

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body>Authorization successful. You can now close this window.</body></html>')

    server_address = ('', 8888)
    httpd = HTTPServer(server_address, SpotifyAuthHandler)
    print("Starting HTTP server...")
    httpd.serve_forever()


if __name__ == "__main__":
    # Start the HTTP server for handling Spotify authentication
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()

    # Authenticate Spotify user and get access token
    authenticate_spotify()

    # Wait for callback to be received
    while not callback_received:
        time.sleep(1)

    # Create a playlist
    playlist_id = create_playlist()

    # Search titles
    titles = filter_for_title()
    spotify_uris = search_titles_in_spotify(titles)

    # Add tracks
    add_tracks_to_playlist(spotify_uris, playlist_id)

    run_http_server()