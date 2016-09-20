from bs4 import BeautifulSoup
import urllib2
import os

courts = { "hkcfa": "http://www.hklii.hk/eng/hk/cases/hkcfa/" }

for x in range(0, len(courts)):
	court_short = courts.keys()[x]
	court = courts.values()[x]
	if not os.path.exists(court_short):
		os.makedirs(court_short)

	court_soup = BeautifulSoup(urllib2.urlopen(court).read(), "html.parser")
	blockquote = court_soup.find_all('blockquote')[1]
	for year in blockquote.find_all('a'):
		year_attr = year.attrs['href']
		if not os.path.exists(os.path.join(court_short, year_attr)):
			os.makedirs(os.path.join(court_short, year_attr))

		court_year = court + year_attr
		court_year_soup = BeautifulSoup(urllib2.urlopen(court_year).read(), "html.parser")
		topics = court_year_soup.find_all('li')
		for topic in topics:
			data = urllib2.urlopen(court_year + topic.a.attrs['href']).read()
			page = open(os.path.join(court_short, year_attr, topic.a.attrs['href']), 'w')
			page.write(data)
