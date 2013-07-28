import os
from os import listdir
import sys
from collections import namedtuple
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from parsers import jsonparser as JsonParser
from parsers import contextparser as ContextParser
from parsers import businesstypeparser as BusinessTypeParser
from naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier
import re

WINDOWS = "nt"
reload(sys)
# Set default encoding to UTF to avoid conflicts with symbols.
sys.setdefaultencoding("utf-8")

"""
Parses the business JSON data for a dict of labels and items.
@return Dict where key is a label and value is an array of items for that 
        {"label": ["item1", "item2"]}
"""
def parseBusinessData(parsedJSON, trainingfolders):
    nbc = NaiveBayesClassifier(trainingfolders, settings.APP_DATA_COMMON_WORDS)
    return ContextParser.parseSoups(parsedJSON.soups, nbc)
    # NOTE: contextMap may have repeats of similar texts, it needs to run through string comparison
    # taking bests.

"""
Identify the business type of the business JSON data.
@return ("Business", ["name", "type"])
"""
def parseBusinessType(parsedJSON):
    businessespath = os.path.join(settings.APP_DATA_TRAINING, "businesses")
    businessfolders = []
    for businesslabel in listdir(businessespath):
        ignores = [".DS_Store"]
        if businesslabel not in ignores:
            businessfolders.append(os.path.join(businessespath, businesslabel))

    nbc = NaiveBayesClassifier(businessfolders, settings.APP_DATA_COMMON_WORDS)
    # Our data files are .txt files for now.
    businesstuple = namedtuple("Business", ["name", "type"])
    businesstuple.name = parsedJSON.name
    businesstuple.type = BusinessTypeParser.parse(parsedJSON.soups, nbc)
    return businesstuple

# Filter and prune menu items.
def parseMenuItems(businessData):
    parsedMenuItems = []
    for label, menuItems in businessData.items():
        if getLabel(label.label) == "menu" and label.probability >= 0.6:
            for item in menuItems:
                if len(item.split()) <= 5:
                    parsedMenuItems.append(item)
    parsedMenuItems = list(set(parsedMenuItems))
    return parsedMenuItems

def saveTrainingFileToSet(inputFile):
    results = set()
    with open(inputFile) as inputFile:
        lines = inputFile.readlines()
        for line in lines:
            for token in line.split():
                results.add(token)
    return results

def parseLocations(businessData):
    # Read in countries and state information.
    countries = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "countries"))
    states = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "states"))
    keywords = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "keywords"))
    # The threshold the string has to hit before we accept it as a valid location.
    threshold = 4

    uniqueLocations = set()
    parsedLocations = []
    for label, locations in businessData.items():
        if getLabel(label.label) == "location":
            for location in locations:
                tokenized = filter(None, re.split("[ .,-]", location))
                if location not in uniqueLocations and 4 <= len(tokenized) <= 10:
                    # A dict of thresholds to map points.
                    thresholds = {}
                    uniqueLocations.add(location)
                    for token in tokenized:
                        token = token.lower()
                        if token in countries and "countries" not in thresholds: 
                            thresholds["countries"] = 1 
                        if token in states and "states" not in thresholds:
                            thresholds["states"] = 1
                        if token.isdigit():
                            if "number" not in thresholds:
                                thresholds["number"] = 1
                            if len(token) is 5 and "postalcode" not in thresholds: 
                                thresholds["postalcode"] = 1
                        if token in keywords and "keywords" not in thresholds:
                            thresholds["keywords"] = 1
                    totalValue = 0
                    for key, value in thresholds.items():
                        totalValue += value
                    if totalValue >= 4:
                        parsedLocations.append(location)
    return locations

def getLabel(label):
    return label[:label.index(":")]

"""
Sets up the mapping from training labels to specific general data.
Eg. "museum_gallery": ["art", "hours", "location", "noise"]
This is a bit more complicated than described.
"""
def mapping():
    ignores = [".DS_Store"]

    defaulttraining = ["hours", "location", "noise"]
    mapping = {}
    businessFolder = os.path.join(settings.APP_DATA_TRAINING, "businesses")
    for businessType in listdir(businessFolder):
        if businessType not in ignores:
            typetraining = []
            if businessType == "museum_gallery": typetraining.extend(["art"])
            if businessType == "apparel": typetraining.extend(["clothing"])
            if businessType == "restaurant": typetraining.extend(["menu"])
            typetraining.extend(defaulttraining)
            mapping[businessType] = typetraining
    return mapping

def parse(inputFile):
    typemapping = mapping()
    parsedJSON = JsonParser.parseData(inputFile)
    businesstype = parseBusinessType(parsedJSON)

    # Obtain the correct general training folder mappings.
    label = businesstype.type.label
    # label = "museum_gallery:museum_gallery", so we have to split on first ":".
    traininglabels = typemapping[getLabel(label)]
    generalpath = os.path.join(settings.APP_DATA_TRAINING, "general")

    # The training folders to be passed into the NBC.
    trainingfolders = []
    for generallabel in listdir(generalpath):
        if generallabel in traininglabels:
            trainingfolders.append(os.path.join(generalpath, generallabel))

    businessData = parseBusinessData(parsedJSON, trainingfolders)

    # So I still need to generalize these things here, since not all businesses will need to parse
    # menu. 
    locations = parseLocations(businessData)
    menuItems = parseMenuItems(businessData)
    Business = namedtuple("Business", ["name", "type", "data", "menu", "locations"])
    return Business(businesstype.name, businesstype.type, businessData, menuItems, locations)



'''
business = parse(os.path.join(settings.APP_DATA_HTML, "escada_com.txt"))

print business.name
print business.type
# Prints out all attributes from general that have been classified.
for key, value in business.data.items():
    print "----------------------------------------"
    print key, list(set(value))
'''

def demo():
    generalpath = os.path.join(settings.APP_DATA_TRAINING, "general")
    trainingfolders = []
    for generallabel in listdir(generalpath):
        if generallabel in ["menu", "location", "noise", "hours"]:
            trainingfolders.append(os.path.join(generalpath, generallabel))
    nbc = NaiveBayesClassifier(trainingfolders, settings.APP_DATA_COMMON_WORDS)
    nbc.demo()

demo()

