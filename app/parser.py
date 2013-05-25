from bs4 import BeautifulSoup
import re
import quopri
import json
import os, errno
import sys
import requests
from address import AddressParser, Address

def parse():
    # Set default encoding to UTF to avoid conflicts with symbols.
    reload(sys)
    sys.setdefaultencoding('utf-8')

    INPUT_FILE = 'cpk.txt'
    OUTPUT_FILE = 'out.txt'

    # Open the file.
    inputFile = open(INPUT_FILE, 'r')
    # Read the file contents.
    lines = inputFile.readlines()

    def parseLocations(soup):
        title = soup.title
        formattedAddresses = []

        if title is not None:
            if 'location' in str(title):
                r = re.compile(r'location', re.IGNORECASE)
            
                '''
                Boolean comparator that takes in a tag from BeautifulSoup.find_all and returns 
                true if the tag or its children contain the word 'location'.
                '''
                def locationCheck(tag):
                    for key in dict(tag.attrs):
                        if key.find('location') != -1:
                            return True
                        if type(tag[key]) is unicode:
                            if str(tag[key]).find('location') != -1:
                                return True
                        else:
                            if any('location' in s for s in tag[key]):
                                return True
                    return False

                locationTags = soup.find_all(locationCheck)

                if locationTags:
                    addressParser = AddressParser()

                    addresses = []     
                    for locationTag in locationTags:
                        
                        #print str(locationTag.name)
                        if str(locationTag.name) != "script":
                            locationSoup = BeautifulSoup(str(locationTag))
                            # Extract the text value from all the tags.
                            allText = locationSoup.find_all(text = True)
                            index = 0
                            for text in allText:
                                pattern = re.compile(r'\t+')
                                #cleanText = re.sub(pattern, '', text)
                                cleanText = re.sub(r'\s+', ' ', text)   
                                if cleanText.find("{") == -1:
                                    address = None
                                    try:
                                        parsedAdress = addressParser.parse_address(cleanText).full_address()
                                        index += 1
                                        siblingIndex = index + 1
                                        maxSiblingSearchDepth = 4
                                        siblingSearchDepth = 0

                                        while (siblingSearchDepth < maxSiblingSearchDepth):
                                            siblingText = str(allText[siblingIndex])

                                            if re.sub(r'\s+', '', siblingText) != re.sub(r'\s+', '', cleanText):
                                                cleanText += re.sub(r'\s+', ' ', siblingText)   
                                            # Found 3 > numbers in a row, hopefully it's a postal code.
                                            if len(re.findall(r"\D(\d[0-9]{3,})\D", ' ' + siblingText + ' ')) > 0:
                                                break;

                                            siblingIndex += 1
                                            siblingSearchDepth += 1

                                        if cleanText not in addresses:
                                            #if len(addresses) == 0:
                                            addresses.append(cleanText)
                                    except:
                                        pass
                           
                    
                    for address in addresses:
                        address.replace(' ', '+')
                        #print '\nORIGINAL' + re.sub(r'\s+', ' ', address)
                        request = 'https://maps.googleapis.com/maps/api/place/textsearch/json?sensor=true&key=AIzaSyDZa2Ayyv1Nk0um0VJvSkM8qj_uzESBMIQ&query=' + address
                        # request = 'http://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&sensor=true'
                        
                        r = requests.get(request)
                        if r.json() is not None:
                            response = r.json()
                            if response['status'] == 'OK':
                                results = response['results']
                                #print '----------RESULTS----------'

                                for result in results:
                                    #print 'Address: ' + result['formatted_address']
                                    if len(results) == 1:
                                        formattedAddresses.append(result['formatted_address'])
                            #else:
                                #print response['status']
                    
        for address in formattedAddresses:
            print address
            
        return formattedAddresses
                        
                    
    for line in lines:
        # Load the line and the value 'body'.
        body = json.loads(line)['body']

        # Use the quopri module to decode the qp encoded value of each page.
        decodedQP = quopri.decodestring(body)
        soup = BeautifulSoup(decodedQP)
        locations = parseLocations(soup)
        if (len(locations) > 0):
            return json.dumps(locations)

parse()

