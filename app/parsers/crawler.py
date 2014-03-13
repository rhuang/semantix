import urllib
import urlparse
from bs4 import BeautifulSoup
import json
import re

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
		print "ERROR: crawler.pullJsonEncodedHtml called with non-string argument"
	
	if "http://" not in url:
		url = "http://" + url

	urls = [url]
	visited = [url]
	jsonData = []
	current_level = 0

	whiteSpaceRegex = '\\s'
	urlEncodingsRegex = '%([0-9]|[A-Z])([0-9]|[A-Z])'
	doubleStarRegex = '\*\*'

	while len(urls) > 0:
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
			jsonData.append({
				"body" : htmlText,
				"sequence_number" : current_level,
				"url" : urls[0]
			})

		urls.pop(0)
		current_level = current_level + 1
		htmlSoup = BeautifulSoup(htmlText)

		for tag in htmlSoup.findAll('a', href=True):
			tag['href'] = urlparse.urljoin(url, tag['href'])
			if url in tag['href'] and tag['href'] not in visited:
				urls.append(tag['href'])
				visited.append(tag['href'])

	jsonStrData = ''
	for data in jsonData:
		jsonStrData = jsonStrData + json.dumps(data) + '\n'
	
	return jsonStrData
