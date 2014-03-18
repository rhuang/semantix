import urllib
import urlparse
from bs4 import BeautifulSoup
import json
import re

import time

'''
This function opens a network object denoted by a URL and vists links 
within associated html. Any links identified will only further be explored
if the top level domain matches the original url argument. 

All extracted html from the links will be returned as a json encoded string
of the form:

json = [
	{
		"data" : "<str>",
		"sequence_number" : <integer>,
		"url" : <str>
	},
	...
]

@param url - a website url.

The url must be astirng will be modified to contain a preceeding "http://"
if it does not already contain it. There is no attempt to make a secure
connection.

Please make sure to do url validation in the calling function as this function
does not make any attempt to validate the url argument.
'''
def pullJsonEncodedHtml(url):
	if not isinstance(url, str):
		print "WARNING: crawler.pullJsonEncodedHtml called with non-string argument"
	
	if "http://" not in url:
		url = "http://" + url

	urls = [url]
	visited = set([url])
	jsonData = []
	current_level = 0

	whiteSpaceRegex = '\\s'
	urlEncodingsRegex = '%([0-9]|[A-Z])([0-9]|[A-Z])'
	doubleStarRegex = '\*\*'

	start_time = time.time()

	MAX_CRAWLING_TIME = 300 # seconds

	while ((time.time() - start_time) < MAX_CRAWLING_TIME) and len(urls) > 0:
		htmlText = ""
		
		try:
			htmlText = urllib.urlopen(urls[0]).read()
		except:
			print "ERROR: crawler.pullJsonEncodedHtml cannot open url argument " + urls[0]

		if htmlText is not "":
			htmlText = re.sub(whiteSpaceRegex, ' ', htmlText)
			htmlText = re.sub(urlEncodingsRegex, ' ', htmlText)
			htmlText = re.sub(doubleStarRegex, '', htmlText)
			htmlText = unicode(htmlText, errors='ignore')
			print "Crawled URL : " + str(urls[0])
			jsonData.append({
				"body" : htmlText,
				"sequence_number" : current_level,
				"url" : urls[0]
			})

		urls.pop(0)
		current_level = current_level + 1
		htmlSoup = BeautifulSoup(htmlText)

		if (time.time() - start_time) < MAX_CRAWLING_TIME:
			for tag in htmlSoup.findAll('a', href=True):
				tag['href'] = urlparse.urljoin(url, tag['href']).split("#")[0]
				if url in tag['href'] and tag['href'] not in visited:
					urls.append(tag['href'])
					visited.add(tag['href'])
		else:
			print "Passed timer, finishing up"

	jsonStrData = ''
	for data in jsonData:
		jsonStrData = jsonStrData + json.dumps(data) + '\n'
	
	print "Completed Crawling"
	return jsonStrData
