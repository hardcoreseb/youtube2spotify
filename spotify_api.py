import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

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

    print(access_token)
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
        return results
    except Exception as e:
        print("Error creating playlist:", e)
        return None

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
                                                       scope="playlist-modify-private")
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