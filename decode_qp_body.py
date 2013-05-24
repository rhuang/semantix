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
                index = 0
                end = len(locationTags)
                for locationTag in locationTags:
                    locationSoup = BeautifulSoup(str(locationTag))
                    allText = locationSoup.find_all(text = True)
                    for locationText in allText:
                        pattern = re.compile(r'\t+')
                        #output = re.sub(pattern, '', locationText)
                        
                        
                        address = "cannot find"
                        try:
                            
                            #print "output: " + output
                            
                            #print " +++++++++++++++++++++++++++++++++++++++"
                        
                            address = addressParser.parse_address(output).full_address()
                            #address += " Califonia Pizza Kitchen"
                            
                            #print "address: " + address
                            '''if full_address is not None:
                                print "full_address: " + full_address
                            
                            
                            print "-----------------------------------------------"   
                            
                            house_number = addressParser.parse_address(output).house_number
                            if house_number is not None:
                                print "house_num: " + house_number
                            
                            
                            print "--------------------------------------------------"   
                            
                            street_prefix = addressParser.parse_address(output).street_prefix
                            if street_prefix is not None:
                                print "street_address: " + street_prefix
                            
                            print "--------------------------------------------------"   
                            
                            street = addressParser.parse_address(output).street
                            if street is not None:
                                print "street: " + street
                               
                            print "---------------------------------------"   
                               
                            street_suffix = addressParser.parse_address(output).street_suffix
                            if street_suffix is not None:
                                print "full_prefix: " + street_suffix
                                
                            print "---------------------------------"   
                                
                            apartment = addressParser.parse_address(output).apartment
                            if apartment is not None:
                                print "apt no: " + apartment
                                
                            print "------------------------------------------"   
                                
                            buiding = addressParser.parse_address(output).buiding
                            if buiding is not None:
                                print "building: " + buiding
                                
                            print "---------------------------------------"   
                                
                            city = addressParser.parse_address(output).city
                            if city is not None:
                                print "city: " + city
                            
                            print "-----------------------------------"   
                            
                            state = addressParser.parse_address(output).state
                            if state is not None:
                                print "state: " + state
                            
                            print "---------------------------------------"
                            
                            zip = addressParser.parse_address(output).zip
                            if zip is not None:
                                print "zip: " + zip
                            
                            print " +++++++++++++++++++++++++++++++++++++++++"
                            '''
                            ''' # get  previous
                            if(index-1>=0):
                                address = str(addressParser.parse_address(locationText[index-1])) + address

                            # get next
                            if(index+1<end):
                                address+= str(addressParser.parse_address(locationText[index+1]))
                            '''
                        except:
                            pass
                           
                        if address is not "cannot find":
                            if address not in list_of_addresses:
                                list_of_addresses.append(address)
                        index+=1
                        
                    pattern = re.compile(r'\t+')
                    output = re.sub(pattern, '', str(locationTag))
                
# MAKES REQUESTS ---------------------------------------------------------------------------------
                #for item in list_of_addresses:
                 #   print item
    
                
                for address in list_of_addresses:
                    address.replace(" ", "+")
                    #print "original address: " + address
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

