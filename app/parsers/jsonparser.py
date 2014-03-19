from bs4 import BeautifulSoup
import quopri
import json
import re
import os, errno
import os.path
import collections
from ..crawlers import crawler
import sys
from collections import  namedtuple
import time
import settings
from os import listdir
from ..naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier

MAX_JSON_PARSING_TIME = 15 # seconds

def getBusinessClassifier():
    businessfolders = []
    businessespath = os.path.join(settings.APP_DATA_TRAINING, "businesses")
    for businesslabel in listdir(businessespath):
        ignores = [".DS_Store"]
        if businesslabel not in ignores:
            businessfolders.append(os.path.join(businessespath, businesslabel))    
    return NaiveBayesClassifier(businessfolders, settings.APP_DATA_COMMON_WORDS)

'''
From a list of labels and their frequencies, retrieve the label with highest weight and the average
average probability of that label.
'''
def highestFrequency(labels):
    frequencies = {}
    # Go through labels and create a frequency map.
    for label in labels:
        if label[0] not in frequencies:
            frequencies[label[0]] = {'frequency': 1, 'probabilities': [label[1]]}
        else:
            frequencies[label[0]]['frequency'] += 1
            # Accumulate a list of probabilities.
            frequencies[label[0]]['probabilities'].append(label[1])

    # Calculate the average probability from the frequencies as well as the weight to get the 
    # highest weight. Weight is frequency * average probability.
    highestResult = {}

    for label in frequencies:
        frequency = frequencies[label]['frequency']

        # Calculate average probability.
        averageProbability = 0
        for probability in frequencies[label]['probabilities']:
            averageProbability += probability
        averageProbability /= frequency
        weight = averageProbability * frequency

        if not highestResult or weight > highestResult['weight']:
            highestResult = {'label': label, 'probability': averageProbability, \
                'weight': averageProbability * frequency}
    return highestResult


def populateSoupBusinessType(soup, nbc):

    soupText = ""
    scriptTags = re.compile(r"[{}\[\]\*>=]")
    if soup is not None:
        # clean up the text
        soupText = str(re.sub(r'\s+', ' ', soup.getText()))
        soupText = re.sub('[.!;+_]', '', soupText)
        soupText = soupText.strip()
        soupText = ' '.join(soupText.split())
    return nbc.classify(soupText)

def generateSoupData(data, nbc):
    
    soup_data = namedtuple("SoupData", ["soups", "name", "label"])
    labels = []
    soups = []
    start_time = time.time()
    businessName = ""
    for line in data:

        # stop parsing at MAX_JSON_PARSING_TIME
        if (time.time() - start_time) > MAX_JSON_PARSING_TIME:
            print "Passed json parser timer, finishing up"
            break
        try:     
            loadedJson = json.loads(line)
            seqVal = loadedJson["sequence_number"]  
            body = loadedJson["body"]
            
            decodedQP = quopri.decodestring(body)
            soup = BeautifulSoup(decodedQP)

            # populate business type
            labels.append(populateSoupBusinessType(soup,nbc))

            # get the title of the page from the body of the root page
            if seqVal == 0:
                businessName = str(soup.title).replace("<title>","").replace("</title>","")
            soups.append(soup)

        except :
            print "An error occured when attempting to parse some soup data "
    
    
    label = highestFrequency(labels)
    print "Extracting all HTML and getting biz name/type took " + str((time.time() - start_time))  + " seconds"

    soup_data.name = businessName
    soup_data.soups = soups
    soup_data.label = label

    return soup_data


# Input         - An input file that corresponds to a website
#               - for example cpk_com.txt
# Description   - Take in the input file and either get the cached version of the file or use the crawler and get its data
# Output        - A business type tuple that 
# Load the line and the value "body".
# Use the quopri module to decode the qp encoded value of each page.
def parseData(url):
    
    businessTuple = collections.namedtuple("Business", ["soups", "name", "type"])
    businessTypeTuple = namedtuple('Type', ['label', 'probability'])

    nbc = getBusinessClassifier()

    # Get a safe file path
    filePath = os.path.join(settings.APP_DATA_HTML, makeFileSafeURL(url))

    # Some files have a ".txt" appended to the end of it, cover that case
    if os.path.isfile(filePath + ".txt"):
        filePath = filePath + ".txt"

    # If the file does not exist, crawl the URL, and make the JSON file
    if os.path.isfile(filePath) != True:
        print "Using the crawler for " + str(url)
        jsonData = crawler.pullJsonEncodedHtml(str(url))
        print "Saving JSON data at filepath " + str(filePath)
        with open(filePath, 'w') as f:
            f.write(jsonData)
    
    # If the file does exist open it    
    with open(filePath) as data:
        print "JSON crawled data found for " + str(url) + " at " + str(filePath)
        soupdata = generateSoupData(data, nbc)    

    businessName = soupdata.name
    print businessName
    businessType = businessTypeTuple(soupdata.label['label'],soupdata.label['probability'])

    if businessName is None:
        businessName = "Not Found!"

    return businessTuple(soupdata.soups, businessName, businessType)

# Make URL safe for saving to file
def makeFileSafeURL(url):

    # remove http://, https://, www. from the front
    safeURL = url.replace("http://","").replace("https://","").replace("www.","")

    # remove trailing / if it exists
    if(safeURL[-1] == "/"):
        safeURL = safeURL[:-1]
     
    # Convert any / or . to underscores since the file system cant handle those symbols
    # NOTE: since both "/" and "." are converted to /, we dont differentiate between www.url/a.com and www.url.a.com
    safeURL = safeURL.replace("/","_").replace(".","_")

    return safeURL
