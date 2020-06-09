# ♫ 1001-tracklists-api (inofficial)

This is an under-development unofficial API for 1001tracklists.com

## Summary

This project is aimed at enabling easy access to the 1001tracklists database via Python.

The scraping is done with [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

Everyone is welcome to contribute!

## Overview

### Classes
```python
class Tracklist:

    # Class variables:
    url
    title
    tracks # list of Track object.
    soup # bs4 object

    # Functions:
    def fetch():
        # Get bs4-object, fetch title and all tracks.
    
    def fetch_tracks():
        # Fetch every tracks' data:
        #   - Metadata
        #   - URL
        #   - External ids (i.e. Spotify)

class Track(Tracklist):

    # Class variables:
    url
    track_id
    title
    external_ids # {"spotify": spotify_id, ...}
    soup # bs4 object

    #Functions:
    def fetch():
        # Fetch title, track_id and all external ids.

    def fetch_external_ids():
        # self-explaining

    def get_external(*services):
        # Returns external ids of passed services if existent.
```

### Example

```python
tracklist = Tracklist(
    "https://www.1001tracklists.com/tracklist/15hjh27t/scott-mills-sean-paul-bbc-radio-1-2020-06-08.html"
    )

# Initial fetch
tracklist.fetch()

# Get a list of tracks
tracks = tracklist.get_tracks()

# Get spotify and apple id for the first track
tracks[0].get_external("spotify", "apple")
```
