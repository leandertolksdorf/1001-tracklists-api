import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "geheim"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PLAYLIST_DESC = "Created with blabla"

    with open("config.json") as json_file:
        config = json.load(json_file)
        SPOTIFY_CLIENT_ID = config["id"]
        SPOTIFY_CLIENT_SECRET = config["secret"]
        SPOTIFY_AUTHORIZATION = config["authorization"]
    SPOTIFY_CALLBACK_URI = "http:///127.0.0.1:8766/auth/callback"
    