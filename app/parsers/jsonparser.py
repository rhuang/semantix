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
        
    #labels = []
    soupText = ""
    scriptTags = re.compile(r"[{}\[\]\*>=]")
    if soup is not None:
        # clean up the text
        soupText = str(re.sub(r'\s+', ' ', soup.getText()))
        soupText = re.sub('[.!;+_]', '', soupText)
        soupText = soupText.strip()
        soupText = ' '.join(soupText.split())
        return nbc.classify(soupText)
        #labels.append(nbc.classify(soupText))
    #return labels

def generateSoupData(data, nbc):
    
    soup_data = namedtuple("SoupData", ["soups", "name", "label"])
    labels = []
    soups = []
    start_time = time.time()

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
def parseData(inputFilePath, fileName):
    
    businessTuple = collections.namedtuple("Business", ["soups", "name", "type"])
    businessTypeTuple = namedtuple('Type', ['label', 'probability'])

    nbc = getBusinessClassifier()

    # If the file does not exist make it
    if os.path.isfile(inputFilePath) != True:
        print "Using the crawler for " + str(inputFilePath)
        url = convertFileNameToUrl(fileName)
        jsonData = crawler.pullJsonEncodedHtml(url)
        with open(inputFilePath, 'w') as f:
            f.write(jsonData)
    
    # If the file does exist open it    
    with open(inputFilePath) as data:
        print "JSON crawled data found for" + str(inputFilePath)
        soupdata = generateSoupData(data, nbc)    

    businessName = soupdata.name
    print businessName
    businessType = businessTypeTuple(soupdata.label['label'],soupdata.label['probability'])

    if businessName is None:
        businessName = "Not Found!"

    return businessTuple(soupdata.soups, businessName, businessType)


def convertFileNameToUrl(filename):
    url = filename.encode('ascii', 'ignore')
    url = re.sub('_', '.', url)
    url = "http://www." + url
    return url