import requests
import spotipy
import spotipy.util as util
import json
import os

AUTH_ENDPOINT = "https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={callback_uri}&scope=user-read-private%20user-read-email&state=34fFs29kd09"
PLAYLIST_ENDPOINT ="https://api.spotify.com/v1/users/{user_id}/playlists"

config_file = json.load(open('config.json'))
CLIENT_ID = config_file['id']
CLIENT_SECRET = config_file['secret']
CALLBACK_URI = config_file['callback_uri']
AUTHORIZAZION = config_file['authorization']
PLAYLIST_DESC = config_file['playlist_desc']

def get_access_token(code):
    print("[SPOTIFY] Getting access token")
    base_url = "https://accounts.spotify.com/api/token"
    data = {
        "redirect_uri": CALLBACK_URI,
        "code": code,
        "grant_type": "authorization_code"
    }
    headers = {
        "Authorization": "Basic YzA2OGJkZDVjNzJhNDNhN2FjYjdmYTIzOTgzNTM5NGQ6YWM3YjA2NGQzNjgwNGUyZGE5NjkzYzI0M2NhMjAxNjM=",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(base_url, headers=headers, data=data)
    auth_json = json.loads(r.text)
    print(auth_json)
    try:
        return auth_json["access_token"]
    except:
        return auth_json

def get_user_id(access_token):
    print("[SPOTIFY] Getting user ID")
    base_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(base_url, headers=headers)
    return response.json()["id"]

def create_playlist(access_token, user_id, tracks, title):
    print("[SPOTIFY] Creating playlist")
    # GENERATE NEW PLAYLIST
    base_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "name": title,
        "public": "true",
        "collaborative": "false",
        "description": PLAYLIST_DESC,
    }
    #print(json.dumps(data))
    playlist = requests.post(base_url, headers=headers, data=json.dumps(data))
    #print(playlist.text)
    playlist_id = playlist.json()["id"]

    # ADD TRACKS TO PLAYLIST

    base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    tracks = ["spotify:track:" + uri for uri in tracks]
    data = {"uris": tracks}
    #print(tracks)

    response = requests.post(base_url, headers=headers, data=json.dumps(data))

    #print(response.text)

    return playlist_id