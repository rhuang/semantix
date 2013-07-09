from bs4 import BeautifulSoup
import quopri
import json
import os, errno
import settings

def parseData():

    INPUT_FILE = settings.CPK_DATA

    # Open the file.
    inputFile = open(INPUT_FILE, 'r')
    # Read the file contents.
    lines = inputFile.readlines()
    
    soups = [] 
    
    for line in lines:
        # Load the line and the value 'body'.
        body = json.loads(line)['body']
    
        # Use the quopri module to decode the qp encoded value of each page.
        decodedQP = quopri.decodestring(body)

        soups.append(BeautifulSoup(decodedQP))
    
    return soups

