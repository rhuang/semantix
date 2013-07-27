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
sys.setdefaultencoding("utf-8")     # Set default encoding to UTF to avoid conflicts with symbols.

"""
Parses the business JSON data for a dict of labels and items.
@return Dict where key is a label and value is an array of items for that 
        {"label": ["item1", "item2"]}
"""
def parseBusinessData(parsedJSON):
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "general"), settings.APP_DATA_COMMON_WORDS)
    return ContextParser.parseSoups(parsedJSON.soups, nbc)
    # NOTE: contextMap may have repeats of similar texts, it needs to run through string comparison
    # taking bests.

"""
Identify the business type of the business JSON data.
@return ("Business", ["name", "type"])
"""
def parseBusinessType(parsedJSON):
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "businesses"), settings.APP_DATA_COMMON_WORDS)
    # Our data files are .txt files for now.
    businessTuple = namedtuple("Business", ["name", "type"])
    businessTuple.name = parsedJSON.name
    businessTuple.type = BusinessTypeParser.parse(parsedJSON.soups, nbc)
    return businessTuple

# Filter and prune menu items.
def parseMenuItems(businessData):
    parsedMenuItems = []
    for label, menuItems in businessData.items():
        if label.label == "menu" and label.probability >= 0.6:
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
    countries = saveTrainingFileToSet(os.path.join(settings.COUNTRIES,"countries"))
    states = saveTrainingFileToSet(os.path.join(settings.COUNTRIES,"states"))
    addresses = saveTrainingFileToSet(os.path.join(settings.COUNTRIES,"addresses"))
    # The threshold the string has to hit before we accept it as a valid location.
    threshold = 4

    uniqueLocations = set()
    parsedLocations = []
    for label, locations in businessData.items():
        if label.label == "location":
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
                        if token in addresses and "addresses" not in thresholds:
                            thresholds["addresses"] = 1
                    totalValue = 0
                    for key, value in thresholds.items():
                        totalValue += value
                    if totalValue >= 4:
                        print "%s, %s, %s" % (location, label.probability, len(tokenized))
                        parsedLocations.append(location)
    return locations

def parse(inputFile):
    parsedJSON = JsonParser.parseData(inputFile)
    businessData = parseBusinessData(parsedJSON)
    businessType = parseBusinessType(parsedJSON)
    locations = parseLocations(businessData)
    menuItems = parseMenuItems(businessData)
    Business = namedtuple("Business", ["name", "type", "data", "menu", "locations"])
    return Business(businessType.name, businessType.type, businessData, menuItems, locations)



business = parse(os.path.join(settings.APP_DATA_HTML, "cpk_com.txt"))

print business.name
print business.type
print business.locations

"""
# Prints out all attributes from general that have been classified.
for key, value in business.data.items():
    print "----------------------------------------"
    print key, list(set(value))

nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "general"), settings.APP_DATA_COMMON_WORDS)
nbc.demo();
"""

