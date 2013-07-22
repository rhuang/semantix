from bs4 import BeautifulSoup
import quopri
import json
import os, errno
import collections

# Input         - 
# Description   - 
# Output        - 
# Load the line and the value 'body'.
 # Use the quopri module to decode the qp encoded value of each page.
def parseData(inputFile,getBizName=False):
    soups = []
    bizName = ""
    business = collections.namedtuple('Business', ['businessSoups', 'businessName'])
    with open(inputFile) as data:
        for line in data:

            seqVal = json.loads(line)['sequence_number']            
            body = json.loads(line)['body']
            decodedQP = quopri.decodestring(body)
            soup = BeautifulSoup(decodedQP)

            if getBizName == True and seqVal == 0:
                bizName = str(soup.title).replace("<title>","").replace("</title>","")

            soups.append(soup)

    if bizName is None:
        bizName = 'Not Found'

    if getBizName == True:
        return  business(soups,bizName)
        
    return soups
        