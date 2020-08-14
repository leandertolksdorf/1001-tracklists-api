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
        """"Retrieve html and return a bs4-object."""
        response = requests.get(url, headers=Headers().generate())
        soup = BeautifulSoup(response.text, "html.parser")
        if "Error 403" in soup.title.text:
            del soup
            raise Exception("Error 403: Captcha? https://www.1001tracklists.com/")
        else:
            return soup
    
    def fetch(self):
        """Fetch title and tracks from 1001.tl"""
        if not self.soup:
            self.soup = self.get_soup(self.url)
        self.title = self.soup.title.text
        self.tracks = self.fetch_tracks()

    def fetch_tracks(self):
        """Fetches metadata, url, and external ids for all tracks.
        Result is saved as Track()-Objects to tracklist.tracks."""
        result = []

        # Find td objects
        table_cells = self.soup.find_all("td", {"id": re.compile('(?<=tlptr_)[0-9]+')})
        


        for cell in table_cells:
            # Find track title (Artist - Title)
            try:
                track_name = cell.find("meta", itemprop="name").get("content")
                print(track_name)
            except AttributeError:
                print(f"Couldn't find title.")
                continue
            # Get track url
            try:
                track_url = cell.find("meta", itemprop="url").get("content")
            except AttributeError:
                print(f"No url found for {track_name}")
                track_url = ""
            # Find span-object containing track id in "id" attribute.
            try:
                id_attr = cell.find("span", {"id": re.compile('(?<=tr_)[0-9]+')}).get("id")
                track_id = re.search("(?<=tr_)[0-9]+", id_attr).group(0)
            except AttributeError:
                track_id = 0

            new = Track(
                url = track_url,
                track_id = track_id,
                title = track_name
            )

            # Get external ids for new track.
            new.fetch_external_ids()
            #new.fetch_external_ids()
            result.append(new)
        return result

    def get_tracks(self):
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
        try:
            # Extract content of "onclick" attribute, which is a js-function.
            track_id_source = track_id_source.get("onclick")
            # Extract track id (after idItem-parameter) using regex.
            self.track_id = re.search("(?<=idItem:\\s).[0-9]+", track_id_source).group(0)
        except AttributeError:
            print(track_id_source)

        # Fetch external ids
        self.fetch_external_ids()

    def get_external(self, *services):
        """Returns external ids of passed streaming services.

        Arguments:

        services -- One or more streaming service names.
                    * for all.

        Services:

        spotify, video, apple, traxsource, soundcloud, beatport
        """
        if not services:
            return self.external_ids

        result = {}
        for service in services:
            try:
                result[service] = self.external_ids[service]
            except KeyError:
                print(f"ERROR: No id found for {service}")
        return result

    def fetch_external_ids(self):
        """Fetch external ids."""
        if not self.track_id:
            print("No track id")
            return


        result = {}
        URL = f"https://www.1001tracklists.com/ajax/get_medialink.php?idObject=5&idItem={self.track_id}&viewSource=1"
        
        # Request all medialinks from 1001tl-API.
        response = requests.get(URL).json()

        # Add external ids to external_ids.
        if response["success"]:
            data = response["data"]
            for elem in data:
                try: 
                    result[SOURCES[elem["source"]]] = elem["playerId"]
                except KeyError:
                    print("Source: ", elem["source"], "not defined.")
            self.external_ids = result

        else: 
            print("Request failed:", response)
