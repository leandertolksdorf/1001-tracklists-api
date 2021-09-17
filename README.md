# ♫ 1001-tracklists-api (unofficial)

An unofficial API to create Python objects with data from 1001tracklists.com.

## Summary

This project is aimed at enabling easy access to the 1001tracklists database via Python.

The scraping is done with [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).

## Usage

Tracklists can be loaded into `Tracklist` objects using:
```python
from tracklists import *
tl = Tracklist(url)
tracks = tl.tracks # A list of Track objects
```

To explore the data available for each object, you may wish to use:
```python
vars(x) # To see all the attributes
help(x) # For more complete documentation
```

## Contributing

Everyone is welcome to contribute!

Tasks which can be worked on are included in the files with TODO tags. In addition, this is the general to-do list:

- [ ] Captcha handling
    - When captcha occurs, pause scraping and redirect to solving page.
    - or: Proxy rotation
- [ ] JSON export
