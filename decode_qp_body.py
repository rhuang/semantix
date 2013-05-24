from bs4 import BeautifulSoup
import re
import quopri
import json
import os, errno
import sys

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
                #print "\n"
                #print tag.attrs
                for key in dict(tag.attrs):
                    #print key, "corresponds to ", tag[key]
                    # look in keys for keyword location
                    if key.find("location") != -1:
                        locationCheck = True

                    #look in values for keyword location
                    # since values could be a list, iteration may be needed
                    #print "type of val is" + str(type(tag[key]))
                    if type(tag[key]) is unicode:
                        #print str(tag[key]) + "and"
                        if str(tag[key]).find("location") != -1:
                            locationCheck = True
                    else:
                        if any("location" in s for s in tag[key]):
                            locationCheck = True
                #print locationCheck
                return locationCheck

            locationTags = soup.find_all(locationCheck)

            if locationTags:
                print "____Location Tags_____\n"
                print len(locationTags)

                for locationTag in locationTags:
                    pattern = re.compile(r'\t+')
                    output = re.sub(pattern, '', str(locationTag))
                    print output
                    print "___________________________________________________________ "
                    print "\n"

            print "_____End Location tags____\n"


# Loop through each line in the file.
index = 0

for line in lines:
    line = lines[index]
    index += 1

    # load the line and the value that we want.
    body = json.loads(line).values()[0]

    # Use the quopri module to decode the qp_encoded value of each page.
    decodedQP = quopri.decodestring(body)
    soup = BeautifulSoup(decodedQP)
    printLocations(soup)

    # Write decoded values to the output file.

    outFile = open(OUTPUT_FILE, 'a')
    outFile.write(decodedQP)
    outFile.write("\n")
    outFile.close()


