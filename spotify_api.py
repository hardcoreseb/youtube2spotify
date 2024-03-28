import requests
import json

spotify_id = "1139834868"
client_id = "ba32f9dbf1644ead9041791489e0425d"
client_secret = "4f106a2de01d4b32ae37dd08345b1fd9"


def get_bearer_token():
    url = 'https://accounts.spotify.com/api/token'
    payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    r = requests.post(url, data=payload, headers=headers)

    print(r.json()['access_token'])
    access_token = r.json()['access_token']

    return access_token

def create_playlist():
    url = f"https://api.spotify.com/v1/users/{spotify_id}/playlists"
    

get_bearer_token()