from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, HiddenField
from wtforms.validators import DataRequired

class InputForm(FlaskForm):
    url = StringField("1001.tl-URL:",validators=[DataRequired()])
    #platform = RadioField("Platform",   choices=[("spotify", "Spotify"), ("apple", "Apple Music")])
    spotify = SubmitField("Spotify")
    applemusic = SubmitField("Apple Music")

class ResultForm(FlaskForm):
    title = HiddenField()
    track = HiddenField()
    submit = SubmitField("Make Playlist")