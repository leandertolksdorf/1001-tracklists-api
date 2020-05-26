from app import db

class Tracklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), index=True, unique=True)
    title = db.Column(db.String(64), index=True, unique=True)
    tracks = db.relationship("Track")
    def __repr__(self):
        return f"<Tracklist {self.title}>"

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    spotify = db.Column(db.String(64), index=True, primary_key=True)