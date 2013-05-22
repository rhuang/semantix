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

    # the title may have location
    title = soup.title

    if title is not None:
    	if "location" in str(title):
    		print "found keyword location at " + str(title)
	    	r = re.compile(r'location',re.IGNORECASE)
	    	locationAnchorTags = soup.find_all("a", text=r)
	    	locationSpanTags = soup.find_all("span", text=r)
	    	locationDivTags = soup.find_all("div", id=r)
	    	locationParaTags = soup.find_all("p", text=r)
	    	
	    	if locationAnchorTags:
	    		print "____Anchor tags_____\n"
	    		for locationAnchorTag in locationAnchorTags:
	    			print str(locationAnchorTag).strip()
	    			for descendant in locationAnchorTag.descendants:
	    				pattern = re.compile(r'\s+')
	    				output = re.sub(pattern, '', str(descendant))
	    				print output
	    		print "____End anchor tags_____\n"

	    	if locationSpanTags:
	    		for locationSpanTag in locationSpanTags:
	    			pattern = re.compile(r'\s+')
	    			output = re.sub(pattern, '', str(locationSpanTag))
	    			print output
	    			print "\n"

	    	if locationDivTags:
	    		print "____Div Tags_____\n"
	    		print len(locationAnchorTags)
	    		for locationDivTag in locationDivTags:
	    			pattern = re.compile(r'\t+')
	    			output = re.sub(pattern, '', str(locationDivTag))
	    			print output + "\n"
                    
	    			#for descendant in locationDivTag.descendants:
	    				#if descendant is not None:
	    				#	print " 	" + str(descendant)

	    		print "_____End Div tags____\n"

	    	if locationParaTags:
	    		for locationParaTag in locationParaTags:
	    			pattern = re.compile(r'\s+')
	    			#print str(locationParaTag).sub(pattern, '', str(locationParaTag))
	    			output = re.sub(pattern, '', str(locationParaTag))
	    			print output
	    		print "\n"

    # Write decoded values to the output file.

    outFile = open(OUTPUT_FILE, 'a')
    outFile.write(decodedQP)
    
    outFile.write("\n")
    outFile.close()
