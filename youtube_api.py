import os
import re
import json

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

youtube_api_key = os.environ.get("YOUTUBE_API_KEY")

def validate_youtube_link(link):
    youtube_link_pattern = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
    return bool(re.match(youtube_link_pattern, link))

def extraxt_playlist_id(link):
    playlist_id = None
    print(youtube_api_key)

    if "list=" in link:
        playlist_id = link.split("list=")[1].split("&")[0]
    return playlist_id

def retrieve_playlist_elements(playlist_id):
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=youtube_api_key
    )

    playlist_items = []
    next_page_token = None
    item_id = 1

    while True:
        request = youtube.playlistItems().list(
            part="id, snippet",
            playlistId=playlist_id,
            fields="items(kind, snippet(publishedAt, title)), pageInfo(totalResults), nextPageToken",
            maxResults=50,
            pageToken=next_page_token if next_page_token else None
        )

        response = request.execute()
        items = response.get("items", [])
        for item in items:
            snippet = item["snippet"]
            snippet["id"] = item_id
            playlist_items.append(snippet)
            item_id += 1

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    create_file_with_playlist_items(playlist_items)

def create_file_with_playlist_items(items):
    with open("./output/playlistitems.json", "w") as f:
        json.dump(items, f, indent=4)