# Youtube2Spotify Converter
## Introduction
Youtube2Spotify is a simple playlist converter to convert your Youtube playlist into a spotify playlist. This app was used to get some practice in python and one of its GUI-tools; in this case [CustomTinker](https://github.com/tomschimansky/customtkinter).

## Installation
Clone the repo:
```
git clone https://github.com/hardcoreseb/youtube2spotify.git
```
Install all the dependencies:
```
pip install -r requirements.txt
```
Remember to use a virtual environment for this project. If you use VS Code you can use the Command Palette (`Ctrl+Shift+P`) to search for the **Python: Create Environment** command, and select it.

## Usage
To use the Converter to its full intent you will either have to create a .env-file in the root directory of this project or click on the **API-Keys**-button to insert your wanted values. Inside of the .env-file you will need to fill in the 5 values needed to run this app:
```.env
SPOTIFY_ID='abcd1234efgh5678ijkl9012mnop3456'
CLIENT_ID='abc123def456ghi789jkl012mno345pq'
CLIENT_SECRET='12ab34cd56ef78gh90ij12kl34mn56op'
REDIRECT_URI='http://localhost:8888/callback'
YOUTUBE_API_KEY='IzaSyA1b2C3d4EfGhIjKlMnOpQrStUvWxYzA'
```
Disclaimer: All of the listed ID's, Secrets and/or API-keys are fully made-up.
