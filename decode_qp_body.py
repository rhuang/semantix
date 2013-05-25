from bs4 import BeautifulSoup
import re
import quopri
import json
import os, errno
import sys
import requests
from address import AddressParser, Address

# set default encoding to utf to avoid conflicts with weird symbols
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")


INPUT_FILE = "cpk.txt"
OUTPUT_FILE = "out.txt"

#remove the file if exists
try:
    os.remove(OUTPUT_FILE)
except OSError:
    pass

# Open the file.
inputFile = open(INPUT_FILE, 'r')
# Read the file contents.
lines = inputFile.readlines()

def printLocations(soup):
    title = soup.title
    if title is not None:
        if "location" in str(title):
            print "found keyword location at " + str(title)
            r = re.compile(r'location', re.IGNORECASE)
        
            def locationCheck(tag):
                locationCheck = False
                for key in dict(tag.attrs):
                    if key.find("location") != -1:
                        locationCheck = True

                    if type(tag[key]) is unicode:
                        if str(tag[key]).find('location') != -1:
                            locationCheck = True
                    else:
                        if any('location' in s for s in tag[key]):
                            locationCheck = True
                return locationCheck

            locationTags = soup.find_all(locationCheck)

            if locationTags:
                print "____Location Tags_____\n"
                print len(locationTags)

                addressParser = AddressParser()

                list_of_addresses = []
                
#GETS ADDRESSES --------------------------------------------------------------------------------
                
                end = len(locationTags)
                for locationTag in locationTags:
                    locationSoup = BeautifulSoup(str(locationTag))
                    allText = locationSoup.find_all(text = True)

                    index = 0
                    for locationText in allText:

                        pattern = re.compile(r'\t+')
                        output = re.sub(pattern, '', locationText)
                                
                        address = "cannot find"
                        try:
                            
                            #print output
                            address = addressParser.parse_address(output).full_address()

                            # make all spaces into single space
                            output = re.sub(r'\s+', ' ', output)
                            "regex matches"
                            #print  re.findall(r"\D(\d[0-9]{3,})\D", " "+output+" ")
                            index += 1

                            siblingIndex = index+1
                            maxSiblingSearchDepth = 4
                            siblingSearchDepth = 0
                            #print "trying to go into while"
                            # try to go into just neighbours text
                            
                            #while(siblingIndex < len(AllText) and siblingSearchDepth < maxSiblingSearchDepth):
                            while(siblingSearchDepth < maxSiblingSearchDepth):
                                

                                siblingText = str(allText[siblingIndex])

                                if re.sub(r'\s+', '', siblingText) != re.sub(r'\s+', '', output):
                                    output += re.sub(r'\s+', ' ', siblingText)
                                # found 3> numbers in a row, hopefully its a postal code
                                if len(re.findall(r"\D(\d[0-9]{3,})\D", " " + siblingText + " ")) > 0:
                                    break;

                                
                                siblingIndex += 1
                                siblingSearchDepth += 1
                            

                            #print "appended values to address, and new address is" + ' '.join(output.split()) + "\n"

                            if address is not "cannot find":
                                if output not in list_of_addresses:
                                    list_of_addresses.append(output)

                            #print "parsed ok"
                            #print "___________________________________"
                        except:
                            #print "not ok"
                            #print  re.findall(r"\D(\d[0-9]{3,})\D", " "+output+" ")
                            #print "___________________________________"
                            pass
                           
                        
                        
                        
                    #pattern = re.compile(r'\t+')
                    #output = re.sub(pattern, '', str(locationTag))
                
# MAKES REQUESTS ---------------------------------------------------------------------------------
                #for item in list_of_addresses:
                 #   print item
                
                
                for address in list_of_addresses:
                    print "_________________"
                    print address
                

                '''
                for address in list_of_addresses:
                    address.replace(" ", "+")
                    print "______________________________________________________"
                    print "original address: " + address
                    request = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&sensor=true"
                    r = requests.get(request)
                    if r.json() is not None:
                        response = r.json()
                        if(response['status'] == "OK"):
                            results = response["results"]
                            for result in results:
                                print result["formatted_address"]
                        else:
                            print response['status']
                    print "_______________________________________________________"
                '''
                
for line in lines:
    # load the line and the value that we want.
    body = json.loads(line)['body']

    # Use the quopri module to decode the qp_encoded value of each page.
    decodedQP = quopri.decodestring(body)
    soup = BeautifulSoup(decodedQP)
    printLocations(soup)

    # Write decoded values to the output file.

    outFile = open(OUTPUT_FILE, 'a')
    outFile.write(decodedQP)
    outFile.write("\n")
    outFile.close()

