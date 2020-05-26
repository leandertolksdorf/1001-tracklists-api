import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}
SOURCES = {
    "1": "beatport",
    "2": "apple",
    "4": "traxsource",
    "10": "soundcloud",
    "13": "video",
    "36": "spotify",
}
URL_FORMAT = "1001tracklists.com/tracklist/"

'''
To do
- wrong "id" -> get_track_ids()
'''

def main(url):

    if URL_FORMAT not in url:
        return {"Error": "Invalid URL"}

    # Get HTML and soupify
    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.text, "html.parser")

    # Write Metadata
    result = {
        "url": url,
        "title": soup.title.text,
        "stream": None,
        "tracks": get_tracks(soup)
    }

    # Get Track IDs
    #track_ids = get_track_ids(soup)

    # Get external IDs
    #result["tracks"] = [get_external_ids(track_id) for track_id in track_ids]

    return result


def get_track_ids(soup):
    print("[1001] Getting track IDs")
    #track_table = soup.find("table", class_="default full tl hover")
    track_values = soup.find_all("span", class_="trackValue")
    #track_names = soup.find_all("div", class_="tlToggleData")
    result = [int((track_values[i]['id'])[3:]) for i in range(len(track_values)) if (track_values[i]['id'][3:]).isdigit()]
    return result


def get_tracks(soup):
    # <meta itemprop="name" content="MOGUAI ft. Cheat Codes - Hold On (VIZE Remix)">
    print("[1001] Getting track containers")
    result = []
    track_table = soup.find_all("tr", class_="tlpItem")
    for track in track_table:
        info = track.find_all("td")[2]
        track_id = info.find("span", class_="trackValue").get("id")[3:]
        track_result = {
            "id": track_id,
            "external_ids": get_external_ids(track_id)
        }
        try:
            track_result["title"] = info.find("meta", itemprop="name").get("content")
        except:
            track_result["title"] = "Error"
        result.append(track_result)

    return result


def get_external_ids(track_id):
    print("[1001] Getting external IDs")
    response = requests.get("https://www.1001tracklists.com/ajax/get_medialink.php?&idObject=5&idItem={}".format(track_id)).json()

    result = {}
    if response["success"]:
        result = {"success": True}
        data = response["data"]
        for elem in data:
            try:
                result[SOURCES[elem["source"]]] = elem["playerId"]
            except KeyError:
                print("Source: ", elem["source"], " not defined")

        return result
    else:
        return False