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
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "general"))
    return ContextParser.parseSoups(parsedJSON.soups, nbc)
    # NOTE: contextMap may have repeats of similar texts, it needs to run through string comparison
    # taking bests.

"""
Identify the business type of the business JSON data0.29782.
@return ("Business", ["name", "type"])
"""
def parseBusinessType(parsedJSON):
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "businesses"))
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
    countries = saveTrainingFileToSet(os.path.join(settings.APP_DATA_TRAINING, \
        "general/location/countries"))
    states = saveTrainingFileToSet(os.path.join(settings.APP_DATA_TRAINING, \
        "general/location/states"))
    # The threshold the string has to hit before we accept it as a valid location.
    threshold = 4

    uniqueLocations = set()
    parsedLocations = []
    for label, locations in businessData.items():
        if label.label == "location":
            for location in locations:
                currentThreshold = 0
                tokenized = filter(None, re.split("[ .,-?!]", location))
                if location not in uniqueLocations and 4 <= len(tokenized) <= 10:
                    uniqueLocations.add(location)
                    for token in tokenized:
                        if token in countries: currentThreshold += 1

                    print "%s, %s, %s" % (location, label.probability, len(tokenized))

def parse(inputFile):
    parsedJSON = JsonParser.parseData(inputFile)
    businessData = parseBusinessData(parsedJSON)
    businessType = parseBusinessType(parsedJSON)
    locations = parseLocations(businessData)
    menuItems = parseMenuItems(businessData)
    Business = namedtuple("Business", ["name", "type", "menu"])
    return Business(businessType.name, businessType.type, menuItems)


#business = parseBusinessType(os.path.join(settings.APP_DATA_HTML, 'partymixnyc_com.txt'))
#print (business.file, business.type.label, business.type.probability)

#business = parseBusiness(os.path.join(settings.APP_DATA_HTML, "alexandregallery_com.txt"))
nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, 'general'), settings.APP_DATA_COMMON_WORDS)
nbc.demo();

# business = parse(os.path.join(settings.APP_DATA_HTML, "cpk_com.txt"))

#nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, "general"))
#nbc.demo()

"""
business = parseBusinessType(os.path.join(settings.APP_DATA_HTML, "townhouseny_com.txt"))
>>>>>>> Stashed changes
print (business.file, business.type.label, business.type.probability)
"""

"""
results = []
for businessFile in listdir(settings.APP_DATA_HTML):
    business = parseBusinessType(os.path.join(settings.APP_DATA_HTML, businessFile))
    if business:
        results.append((business.file, business.type.label, business.type.probability))
for result in results:
    print result
"""


