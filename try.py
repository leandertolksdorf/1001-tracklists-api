from tracklists import *

url = "https://www.1001tracklists.com/tracklist/1fy61y0k/lane-8-fall-2021-mixtape-2021-09-15.html"
if __name__ == '__main__':
    print('This is a module')
    tl = Tracklist(url)
    tracks = tl.tracks
    tracks = tracks