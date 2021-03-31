import requests
from fake_headers import Headers
from bs4 import BeautifulSoup


def get_soup(url):
	"""" Retrieve html and return a bs4 object """
	response = requests.get(url, headers=Headers().generate())
	soup = BeautifulSoup(response.text, "html.parser")
	if "Error 403" in soup.title.text:
		del soup
		raise Exception("Error 403: Captcha? https://www.1001tracklists.com/")
	else:
		return soup


def get_json(url):
	""" Retrieve JSON from url """
	return requests.get(url, headers=Headers().generate()).json()