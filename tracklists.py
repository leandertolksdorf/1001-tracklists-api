import requests
import re
from fake_headers import Headers
from bs4 import BeautifulSoup

SOURCES = {
    "1": "beatport",
    "2": "apple",
    "4": "traxsource",
    "10": "soundcloud",
    "13": "video",
    "36": "spotify",
}

class Tracklist:
    """An object representing a tracklist on 1001tracklists.com

    Keyword arguments:

    url -- The url of the tracklist page.

    Class variables:

    url

    title -- Title of the Tracklist
    
    tracks -- List of Track Objects

    Run tracklist_name.fetch() to get data.
    """
    
    def __init__(self, url=""):
        self.url = url
        if not url:
            with open("test.html") as f:
                self.soup = BeautifulSoup(f, "html.parser")
        else:
            self.url = url
        self.title = ""
        self.tracks = []
        self.soup = None

    def __repr__(self):
        url = f"<Tracklist> {self.url}\n"
        title = f"<Title> {self.title}\n"
        tracks = ""
        for track in self.tracks:
            tracks += f"    <Track> {track.title}\n"
        return url + title + tracks
    
    def get_soup(self, url):
        response = requests.get(url, headers=Headers().generate())
        return BeautifulSoup(response.text, "html.parser")
    
    def fetch(self):
        """Fetch title and tracks from 1001.tl"""

        if not self.soup:
            self.soup = self.get_soup(self.url)
        self.title = self.soup.title.text
        self.tracks = self.fetch_tracks()

    def get_track_ids(self):
        """Returns a list of ids for all tracks included in tracklist."""
        track_values = self.soup.find_all("span", class_="trackValue")
        result = [int((track_values[i]['id'])[3:]) for i in range(len(track_values)) if (track_values[i]['id'][3:]).isdigit()]
        return result

    def get_track_table(self):
        result = {}
        entries = self.soup.find_all("tr", class_="tlpItem")
        for entry in entries:
            print(entry.find_all("a"))
        print(entries[0].text)

    def fetch_tracks(self):
        """Fetches metadata, url, and external ids for all tracks.
        Result is saved as Track()-Objects to tracklist.tracks."""
        result = []
        track_table = self.soup.find_all("tr", class_="tlpItem")

        for track in track_table:
            links = track.find_all("a")
            for link in links:
                if "/track/" in link["href"]:
                    track_url = link["href"]
                    break;

            info = track.find_all("td")[2]
            track_id = info.find("span", class_="trackValue").get("id")[3:]
            title = info.find("meta", itemprop="name").get("content")

            new = Track(
                url = track_url,
                track_id = track_id,
                title = info.find("meta", itemprop="name").get("content")
            )
            new.fetch_external_ids()
            result.append(new)
            self.tracks = result
        return result

    def tracks(self):
        for track in self.tracks:
            print(track)
        return self.tracks

class Track(Tracklist):
    """An object representing a track on 1001tracklists.com

    Keyword arguments:

    url -- The url of the tracklist page.

    track_id -- Internal 1001.tl-track id

    title -- Title

    external_ids -- List of available streaming ids

    Run track_name.fetch() to get data.

    """
    
    def __init__(self, url="", track_id=0, title="", external_ids={}):
       
        self.url = url
        self.track_id = track_id
        self.title = title
        self.external_ids = external_ids
        self.soup = None
        

    def __repr__(self):
        title = f"<Title> {self.title}\n"
        track_id = f"<ID> {self.track_id}\n"
        external = f"<External> {[x for x in self.external_ids]}\n"
        url = f"<URL> {self.url}...\n"
        return url + title + track_id + external

    def fetch(self):
        """Fetch title, track_id and external ids."""

        if not self.soup:
            self.soup = self.get_soup(self.url)
        
        self.title = self.soup.find("h1", id="pageTitle").text.strip()

        # Extract track id from <li title="add media links for this track">-element.
        track_id_source = self.soup.find("li", title="add media links for this track")
        track_id_source = track_id_source.get("onclick")
        self.track_id = re.search("(?<=idItem:\\s).[0-9]+", track_id_source).group(0)

        # Fetch external ids
        self.fetch_external_ids()

    def get_external(self, *services):
        """Returns external ids of passed streaming services.

        Arguments:

        services -- One or more streaming service names.

        Services:

        spotify, video, apple, traxsource, soundcloud, beatport
        """
        result = {}
        for service in services:
            try:
                result[service] = self.external_ids[service]
            except KeyError:
                print(f"ERROR: No id found for {service}")
        return result

    def fetch_external_ids(self):
        """Fetch external ids."""
        result = {}
        URL = f"https://www.1001tracklists.com/ajax/get_medialink.php?idObject=5&idItem={self.track_id}&viewSource=1"
        
        response = requests.get(URL).json()
        if response["success"]:
            data = response["data"]
            for elem in data:
                try: 
                    result[SOURCES[elem["source"]]] = elem["playerId"]
                except KeyError:
                    print("Source: ", elem["source"], "not defined.")
            self.external_ids = result
            return result

        else: 
            print("Request failed:", response)