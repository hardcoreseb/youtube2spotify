import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

import time
import json

spotify_id = "1139834868"
client_id = "ba32f9dbf1644ead9041791489e0425d"
client_secret = "4f106a2de01d4b32ae37dd08345b1fd9"
access_token = None
callback_received = False

def get_bearer_token():
    url = 'https://accounts.spotify.com/api/token'
    payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, data=payload, headers=headers)
    access_token = r.json().get('access_token')

    print("Bearer Token", access_token)
    return access_token

def refresh_token():
    global access_token
    access_token = get_bearer_token()
    print(access_token)
    threading.Timer(3600, refresh_token).start()  # Refresh token every hour

def authenticate_spotify():
    # Define the HTTP server URL
    callback_uri = "http://localhost:8888/callback"

    # Open the browser to Spotify's authentication endpoint
    auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={callback_uri}&scope=playlist-modify-private&show_dialog=True"
    webbrowser.open(auth_url)

def create_playlist():
    global access_token
    global callback_received
    access_token = None
    print("ACCESTOKEN TEST:", access_token)
    if access_token is None:
        authenticate_spotify()
        callback_received = False
        while not callback_received:
            time.sleep(1)
    
    sp = spotipy.Spotify(auth=access_token)

    # Create a playlist
    try:
        results = sp.user_playlist_create(
            user=spotify_id,
            name="Youtube2Spotify",
            public=False,
            description="Created by the YouTube2Spotify App."
        )
        print("Playlist created successfully:", results)
        print("Spotify ID for the playlist", results["id"])
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

def search_spotify(title, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    params = {
        'q': title,
        'type': 'track'
    }
    
    url = 'https://api.spotify.com/v1/search'
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('tracks') and data['tracks'].get('items'):
            # Get the Spotify URI of the first track
            spotify_uri = data['tracks']['items'][0]['uri']
            return spotify_uri
        else:
            print(f"No tracks found for title: {title}")
            return None
    else:
        print(f"Failed to search for title: {title}, Status Code: {response.status_code}")
        return None
    
def search_titles_in_spotify(titles):
    spotify_uris = {}
    bearer_token = get_bearer_token()
    for title in titles:
        spotify_uri = search_spotify(title, bearer_token)
        if spotify_uri:
            spotify_uris[title] = spotify_uri
    return spotify_uris

def add_tracks_to_playlist(spotify_uris_dict, playlist_id):
    access_token = get_bearer_token()
    # Extract the URIs from the dictionary
    spotify_uris = list(spotify_uris_dict.values())
    
    # Spotify API endpoint to add tracks to a playlist
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Batch tracks in groups of 100 due to API limits (Spotify allows max 100 tracks per request)
    batch_size = 100
    for i in range(0, len(spotify_uris), batch_size):
        # Prepare data to send to the API
        data = {
            'uris': spotify_uris[i:i + batch_size]  # Slice the URIs into batches
        }
        
        # Make the POST request to add tracks
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Batch {i//batch_size + 1} added successfully!")
        else:
            print(f"Failed to add batch {i//batch_size + 1}: {response.status_code}, {response.text}")


def run_http_server():
    class SpotifyAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            global access_token, callback_received
        
            if self.path.startswith("/callback"):
                # Extract the authorization code from the callback URI
                authorization_code = self.path.split("=")[1]

                # Exchange the authorization code for an access token
                sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=client_id,
                                                       client_secret=client_secret,
                                                       redirect_uri="http://localhost:8888/callback",
                                                       scope="playlist-modify-public playlist-modify-private")
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
    refresh_token_thread = threading.Thread(target=refresh_token)
    refresh_token_thread.daemon = True  # Daemonize the thread
    refresh_token_thread.start()

    # Start the HTTP server for handling Spotify authentication
    server_thread = threading.Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()


    # Attempt to create the playlist
    create_playlist()

    run_http_server()