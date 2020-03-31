import requests
import re
import ast
import urllib.request
import time
from bs4 import BeautifulSoup


class Scraper:

    def __init__(self, url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}):
        self.url = url
        self.title = ""
        self.headers = headers
        self.track_ids = []
        self.soup = BeautifulSoup()

    def parse_html(self):
        response = requests.get(self.url, headers=self.headers)
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_track_ids(self):
        """Returns all track_id's from a 1001.tl/tracklist-url."""

        print("Getting track-ids.")

        # response = requests.get(self.url, headers=self.headers)
        # soup = BeautifulSoup(response.text, "html.parser")
        # print(type(soup))
        track_values = self.soup.find_all("span", class_="trackValue")

        result = [int((track_values[i]['id'])[3:]) for i in range(
            len(track_values)) if (track_values[i]['id'][3:]).isdigit()]
        self.track_ids = result
        return result

    def get_title(self):
        "Returns the title of a tracklist."
        self.title = self.soup.title
        return self.title

    # def get_a_tags(self):
    #     """Returns a list of all <a>-tags scraped from url."""
    #     response = requests.get(self.url, self.headers)
    #     soup = BeautifulSoup(response.text, "html.parser")
    #     result = soup.findAll('a')

    #     self.a_tags = result
    #     return result

    # def get_track_urls(self):
    #     """Returns a list of 1001.tl/track-urls from a list of <a>-tags."""
    #     prefix = "https://www.1001tracklists.com"
    #     result = [prefix + (a_tags[i]['href']) for i in range(len(a_tags)) if 'href="/track/' in str(a_tags[i])]
    #     self.track_urls = result
    #     return result
