from .scraper import *

import re

SOURCES = {
	"1": "beatport",
	"2": "apple",
	"4": "traxsource",
	"10": "soundcloud",
	"13": "video",
	"36": "spotify",
}

class Tracklist:
	""" An object representing a tracklist on 1001tracklists.com.

	Attributes
	----------
	url : str
		Link to tracklist page
	tracklist_id : str
		Internal 1001tracklists.com ID for the tracklist
	title : str
		Name of tracklist
	tracks : list[Track]
		List of tracks in tracklist
	date_recorded : str
		Date tracklist was recorded
	interaction_details : dict{str : int}
		Dictionary including measure of interactions with the tracklist (e.g. likes)
	num_tracks : int
		Number of tracks in tracklist
	num_tracks_IDed : int
		Number of tracks which have been IDed
	genres : list[str]
		List of genres associated with the tracklist
	DJs : list[str]
		List of DJs who made the tracklist
	sources : dict{str : str}
		Dictionary mapping the type of source to the source (e.g. {' Open Air / Festival 0': 'Tomorrowland'})
	track_nums : list[str]
		List of track numbers ("01" is first song, "02" is second song, "w/" if track played with previous)
	cues : list[str]
		List of cue times for tracks (e.g. "0:04" or "47:30" or "" if not available)
	"""
	
	""" To-do list included here to avoid showing up in help(Tracklist)
	TODO:
	make DJ class
	tracklist media links
	clean up sources?
	methods for genre_counts, artist_counts, etc.
	additional metadata from left pane
	"""
	
	def __init__(self, url, fetch=True):
		""" Initialize Tracklist. """
		self.url = url
		self.tracklist_id = self.url.split('tracklist/')[1].split('/')[0] # Get id from url
		if fetch:
			self.fetch()

	def fetch(self):
		""" Load Tracklist details from url. """
		soup = get_soup(self.url)
		left_pane = soup.find("div", id = "left")
		self.title = soup.title.text
		self.load_metadata(left_pane)
		
		# Load tracks into list
		self.tracks = []
		track_divs = soup.find_all('div', {'class': 'tlpItem'}) # Find div objects for tracks
		for track_div in track_divs:
			t = Track(track_div) # TODO Get external links?
			if track_div.find('i', {'title': 'mashup linked position'}): # Track part of mashup -> attach to previous entry in tracklist
				self.tracks[-1].add_subsong(t)
			else:
				self.tracks.append(t)

		# Load track numbers and cues (adapted from https://github.com/globalnomad/quickCUE/blob/master/quickCUE.py)
		self.track_nums = [span.text.strip() for span in soup.find_all('span', id=re.compile('_tracknumber_value'))]
		self.cues = [div.text.strip() for div in soup.find_all('div', class_='cueValueField')]

	def __repr__(self):
		return "Tracklist(" + self.tracklist_id + ")"

	def __str__(self):
		return self.title

	def load_metadata(self, left_pane):
		""" Load metadata on tracklist from left pane of page (DJ, source, date recorded, etc.). """ 
		try:
			self.date_recorded = left_pane.find("span", title = "tracklist recording date").parent.parent.select("td")[1].text
		except (AttributeError, IndexError):
			self.date_recorded = None
		
		self.interaction_details = {}
		for interaction_detail in left_pane.find_all("meta", itemprop = "interactionCount"):
			name, count = interaction_detail["content"].strip().split(":")
			self.interaction_details[name] = int(count)
		
		IDed = left_pane.text.split('IDed')[1].split('short')[0].strip().split(" / ")[0]
		total = left_pane.text.split('IDed')[1].split('short')[0].strip().split(" / ")[1].split(' ')[0]
		self.num_tracks = int(total)
		self.num_tracks_IDed = int(IDed) if IDed != 'all' else int(total)
		
		self.genres = left_pane.find("td", id = "tl_music_styles").text.split(", ") if left_pane.find("td", id = "tl_music_styles") else []
		
		try:
			tracklist_DJs_location = left_pane.find_all("table", class_ = "sideTop")
			tracklist_DJs_location = [person_place.find("a") for person_place in tracklist_DJs_location]
			
			tracklist_DJs = []
			tracklist_source = {}
			
			for person_place in tracklist_DJs_location:
				if re.search("\/dj\/", person_place.get("href")):
					tracklist_DJs.append(person_place.text)
				if re.search("\/source\/", person_place.get("href")):
					tracklist_source[person_place.parent.parent.parent.find("td").contents[0]] = person_place.text
			  
			self.DJs = tracklist_DJs
			
			# Tracklist sources include event name, location, radio show, etc.
			# Splits each by type of source and adds number in case tracklist is for multiple sources (e.g. two radio shows do a colab and both appear on 1001Tracklists page)
			self.sources = {}
			for source in tracklist_source:
				source_number = 0
				source_w_number = source + str(source_number)
				while source_w_number in self.sources:
					source_number += 1
					source_w_number = source + str(source_number)
				self.sources[source_w_number] = tracklist_source[source]
			
		except AttributeError: # Couldn't find tracklist sources (e.g. DJs, festival, radio show, etc.)
			pass


class Artist:
	""" An object representing an artist on 1001tracklists.com

	Attributes
	----------
	name : str
		Artist's name
	url : str
		Link to artist page on 1001tracklists.com, or None if no page exists
	artist_id : str
		Internal 1001tracklists.com ID for artist, or None if not available

	"""

	"""
	TODO
	handle subartists e.g. &, vs.
	fetch() method
	"""

	def __init__(self, span=None, name=None):
		""" Initialize from bs4.span containing artist name and link, or artist name if span not available """
		self.name = name if name else span.text
		self.url = span.a['href'] if span and span.find('a') else None
		self.artist_id = self.url.split('artist/')[1].split('/')[0] if self.url else None

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name


class Label:
	""" An object representing a label on 1001tracklists.com

	Attributes
	----------
	name : str
		Label name
	url : str
		Link to label page on 1001tracklists.com, or None if no page exists
	label_id : str
		Internal 1001tracklists.com ID for label, or None if not available
	"""

	"""
	TODO
	handle sublabels better
	fetch() method
	"""
	

	def __init__(self, td):
		""" Initialize from bs4.td containing label name and link """
		self.name = td.text
		self.url = td.a['href'] if td.find('a') else None
		self.label_id = self.url.split('label/')[1].split('/')[0] if self.url else None
		# If sublabel (e.g. "DHARMA (SPINNIN')") keeps full name ("DHARMA (SPINNIN')") and link to sublabel (DHARMA)

	def __str__(self):
		return self.name

	def __repr__(self):
		return "Label(" + (self.label_id if self.label_id else self.name) + ")"


class Track:
	"""An object representing a tracklist on 1001tracklists.com

	Attributes
	----------
	url : str
		Link to tracklist page
	track_id : str
		Internal 1001tracklists.com ID for the track
	full_title : str
		Full name of track (e.g. 'Tiësto & DallasK - Show Me')
	title : str
		Track title (e.g. 'Seven Nation Fun (Holl & Rush Mashup)')
	full_artist : str
		Full name of track artist, including any featured artists (e.g. 'Tiësto & Dzeko ft. Lena Leon')
	artist : Artist
		Artist who recorded track (not including any featured artists)
	genre : str
		Genre associated with the track or None if not listed
	duration : str
		The duration of the track in ISO 8601 date format or None if not listed
	labels : list[Label]
		Label that released track, multiple labels in case Track is a mashup
	subsongs : list[Track]
		If Track is a mashup, list of tracks it includes
	"""
	"""
	TODO
	----
	fetch()
	Remix information
	Parse featured artist(s)
	Handle reworks
	"""

	def __init__(self, soup, fetch=False):
		""" Initialize Track from bs4.div with itemprop="tracks". """

		# Get basic info
		self.full_title = soup.find('span', {'class': "trackValue"}).text.strip().replace('\xa0', ' ')
		self.full_artist, self.title = tuple(self.full_title.split(' - ', maxsplit=1))

		# Get info from metadata
		meta_data = {meta['itemprop']: meta['content'] for meta in soup.find_all('meta')} # keys: 'name', 'byArtist', 'publisher', 'duration', 'genre', 'url'
		self.genre = meta_data['genre'] if 'genre' in meta_data else None
		self.duration = meta_data['duration'] if 'duration' in meta_data else None
		self.url = meta_data['url'] if 'url' in meta_data else None


		#doesn't exist for some reason
		#track_id = soup.find('span', {'class': 'trackValue'})['id']
		#self.track_id = int(track_id[3:]) if 'pos' not in track_id else None
		
		# Get track artist
		try:
			artist_span = soup.find('span', {'title': 'open artist page'}).parent
			self.artist = Artist(span=artist_span)
		except: # No artist link available -> use artist name from metadata or self.full_artist
			self.artist = Artist(name=meta_data['byArtist'] if 'byArtist' in meta_data else self.full_artist)
		
		# Get label details (store in list because can have multiple labels)
		labels = soup.find_all('span', {'title': 'label'})
		self.labels = [Label(label) for label in labels] if labels else []

		# Prepare mashup details
		self.subsongs = [] # Will be populated if track is mashup

	def add_subsong(self, subsong):
		"""
		Add original tracks which were used in mashup.
		
		subsong : Track
			Original track used in mashup
		"""
		self.subsongs.append(subsong)

	def __str__(self):
		return self.title + ' by ' + str(self.artist)
	
	def __repr__(self):
		return 'Track(' + self.full_title + ')'
	
	def fetch(self):
		""" Fetch track details from track page. """
		if not self.track_id:
			return
		
		url = 'https://www.1001tracklists.com/track/' + str(self.track_id)
		soup = get_soup(url)
		# TODO get other information

	def fetch_external_ids(self):
		""" Fetch external link ids for track. """
		if not self.track_id:
			return

		# Request all medialinks from 1001tl-API
		url = f"https://www.1001tracklists.com/ajax/get_medialink.php?idObject=5&idItem={self.track_id}"
		response = get_json(url)

		# Add external ids to external_ids
		self.external_ids = {}
		if response["success"]:
			for elem in response["data"]:
				try: 
					self.external_ids[SOURCES[elem["source"]]] = elem["playerId"]
				except KeyError:
					print("Source: ", elem["source"], "not defined.")