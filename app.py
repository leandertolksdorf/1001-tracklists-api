from flask import Flask, session, jsonify, render_template, redirect, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import sys
import api
import json
import os
import spotify
from forms import InputForm, ResultForm

print (sys.version)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

config_file = json.load(open('config.json'))
CLIENT_ID = config_file['id']
CLIENT_SECRET = config_file['secret']
CALLBACK_URI = config_file['callback_uri']

@app.route('/', methods=["GET","POST"])
@app.route('/index', methods=["GET","POST"])
def index():
    form = InputForm()
    if 'spotify_code' in request.cookies:
        spotify_code = request.cookies.get('spotify_code')
    else:
        spotify_code = False
    return render_template("index.html", title="Home", form=form, spotify_code=spotify_code)

@app.route('/api/<path:url>', methods=['GET'])
def get_response(url):
    return jsonify(api.main(url))

@app.route('/go', methods=["GET", "POST"])
def go():
    session.clear()
    response = make_response(redirect(f"http://accounts.spotify.com/de/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={CALLBACK_URI}&scope=user-read-email%20playlist-read-private%20user-follow-read%20user-library-read%20user-top-read%20playlist-modify-private%20playlist-modify-public&state=34fFs29kd09"))
    response.set_cookie("url", request.args.get("url"))
    return response

@app.route('/auth/callback')
def callback():
    auth_code = request.args['code']
    print("Code:", auth_code)
    access_token = spotify.get_access_token(auth_code)
    response = make_response(result())
    response.set_cookie("spotify_code", auth_code)
    response.set_cookie('spotify_token', access_token)
    return response



@app.route('/result/', methods=["GET","POST"])
def result():
    url = request.cookies.get("url")
    results = api.main(url)
    title = results["title"]
    tracks = [track["external_ids"]["spotify"] for track in results["tracks"] if track["external_ids"] and "spotify" in track["external_ids"]]
    form = ResultForm()
    return render_template("result.html", results=results["tracks"], tracks=tracks, title=title, form=form)


@app.route('/create-playlist/')
def create_playlist():
    """auth_code = request.cookies.get("spotify_code")
    data = {
        #"response_type": "code",
        "grant_type":"authorization_code",
        "code": auth_code,
        "redirect_uri": CALLBACK_URI,
        #"client_id": CLIENT_ID,
        #"client_secret": CLIENT_SECRET
    }
    headers = {
        "Authorization": "Basic YzA2OGJkZDVjNzJhNDNhN2FjYjdmYTIzOTgzNTM5NGQ6YWM3YjA2NGQzNjgwNGUyZGE5NjkzYzI0M2NhMjAxNjM="
    }"""
    user_id = spotify.get_user_id(request.cookies.get("spotify_token"))
    access_token = request.cookies.get("spotify_token")
    title = request.args.get("title")
    tracks = request.args.getlist("track")

    playlist_id = spotify.create_playlist(access_token, user_id, tracks, title)

    return render_template("done.html", playlist_id=playlist_id)

@app.route("/imprint")
def imprint():
    return "Imprint"

if __name__ == '__main__':
    app.run()
