import os
from os import listdir
import sys
from collections import defaultdict, namedtuple
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from parsers import jsonparser as JsonParser
from parsers import contextparser as ContextParser
from naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier
import re
import time

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
Saves a training file to a set to use as a keyword match when parsing.
"""
def saveTrainingFileToSet(inputFile):
    results = set()
    with open(inputFile) as inputFile:
        lines = inputFile.readlines()
        for line in lines:
            for token in line.split():
                results.add(token)
    return results

"""
Called by parseLabels. Parsing locations is a bit more convoluted for now, so it has its own
function.
"""
def parseLocations(type, extrainfo, item, prop):
    POSTAL_CODE_LENGTH = 5
    # Put this inside properties if other labels use it as well.
    MAX_PROB = 0.96

    ordinals = ['st', 'nd', 'rd', 'th']
    numOrdinals = 1
    threshold = prop["threshold"]
    tokenized = filter(None, re.split("[ .,-]", item))

    if prop["mintokens"] <= len(tokenized) <= prop["maxtokens"] and \
        type.probability >= prop["probability"]:
        # If greater than max probability, than return right away.
        if type.probability >= MAX_PROB:
            return item
        # A dict of thresholds to map points.
        thresholds = defaultdict(int)
        for token in tokenized:
            token = token.lower()
            if token in extrainfo["countries"] and "countries" not in thresholds: 
                thresholds["countries"] = 1 
            if token in extrainfo["states"] and "states" not in thresholds:
                thresholds["states"] = 1
            if token.isdigit():
                if "number" not in thresholds:
                    thresholds["number"] = 1
                if len(token) is POSTAL_CODE_LENGTH and "postalcode" not in thresholds: 
                    thresholds["postalcode"] = 1
            if token in extrainfo["keywords"] and "keywords" not in thresholds:
                thresholds["keywords"] = 1
            if len(token) > 2:
                # Check if this word is an ordinal number like '1st' for location feature.
                if token[-2:] in ordinals and token[:-2].isdigit():
                    thresholds["ordinals"] += 1
            if token[0:1] == "#":
                if "hash" not in thresholds:
                    thresholds["hash"] += 1

        totalValue = 0
        for key, value in thresholds.items():
            totalValue += value
        if totalValue >= threshold:
            return item
    return None

"""
Given the business data and the type, split the data into correct labels.
Eg. Given www.escada.com, get data for clothing, locations, and hours.
NOTE: This does not take into account threshold for now. Threshold is for locations only.
Returns a default dict:
    {"apparel": [ ... ], "locations": [ ... ], "hours": [ ... ]}
"""
def parseLabels(businessData, businesstype):
    # Some data to check keywords against.
    # Read in countries and state information.
    countries = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "countries"))
    states = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "states"))
    keywords = saveTrainingFileToSet(os.path.join(settings.ADDRESSES, "keywords"))
    extrainfo = {"countries": countries, "states": states, "keywords": keywords}

    parseditems = defaultdict(list)
    uniquesets = defaultdict(set)
    # Get the parsing properties for each label, such as probability threshold.
    properties = parsePropertiesMapping(businesstype.type.label)
    for type, items in businessData.items():
        if type.label in properties:
            prop = properties[type.label]
            # Special function for checking locations.
            if type.label == "location":
                for item in items:
                    location = parseLocations(type, extrainfo, item, prop)
                    if location is not None:
                        # Account for cases like "ADDRESS" AND "address" with .lower().
                        if item.lower() not in uniquesets[type.label]:
                            parseditems[type.label].append(item)
                        uniquesets[type.label].add(item.lower())
            elif type.probability >= prop["probability"]:
                #if type.label == "menu":
                    #for item in items:
                    #    print item
                for item in items:
                    if prop["mintokens"] <= len(item.split()) <= prop["maxtokens"]:
                        # Account for cases like "ADDRESS" AND "address" with .lower().
                        if item.lower() not in uniquesets[type.label]:
                            parseditems[type.label].append(item)
                        uniquesets[type.label].add(item.lower())
    return parseditems

"""
This maps a business type label to a list of general labels. 
An example of business type like "museum_gallery" to its corresponding "general" 
training directories.

Eg. a  label of "museum_gallery" will return ["art", "hours", "location", "noise"]
"""
def labelToDirsMapping(label):
    defaultdirs = ["hours", "location", "noise"]
    trainingdirs = []
    # The mapping part. The keys of the properties dict correspond to the folder names under the
    # "general" directory.
    if label == "museum_gallery": 
        trainingdirs.append("art")
    if label == "apparel": 
        trainingdirs.append("clothing")
    if label == "restaurant":
        trainingdirs.append("menu")
    if label == "furniture":
        trainingdirs.append("furniture")
        trainingdirs.append("jewellery")
    if label == "medical":
        trainingdirs.append("dental")
        trainingdirs.append("medicine")
    if label == "jewellery":
        trainingdirs.append("jewellery")
    if label == "hotel":
        trainingdirs.append("hotel")
    trainingdirs.extend(defaultdirs)
    return trainingdirs

def createProperties(probability=1, mintokens=0, maxtokens=sys.maxint, threshold=0):
    return {
        "probability": probability,
        "mintokens": mintokens,
        "maxtokens": maxtokens,
        "threshold": threshold
    }

"""
Given a label (business type like "museum_gallery"), return a mapping to its "general" data 
counterpart and the parsing properties such as:
    probability threshold
    max item length (in tokens)
Eg. "museum_gallery" ==> 
        returns {"art": {"probability": 0.7, "itemlength": 10},
                 "hours": {"probability": 0.6, "itemlength": 5},
                 "location": {"probability": 0.6, "itemlength": 10}}
"""
def parsePropertiesMapping(label):
    # TUNING PARAMETERS.
    ART_PROB = 0.7; ART_MIN = 0; ART_MAX = 10
    CLO_PROB = 0.7; CLO_MIN = 0; CLO_MAX = 15
    MENU_PROB = 0.7; MENU_MIN = 0; MENU_MAX = 10
    HOURS_PROB = 0.6; HOURS_MIN = 0; HOURS_MAX = 10
    # Location threshold kept to 3 since at times just the street is mentioned
    # Location max kept to 35 for some locations that are all squished together
    LOC_PROB = 0.6; LOC_MIN = 4; LOC_MAX = 35; LOC_THRES = 3
    # furniture kept to 0.4 probability since any furniture classifications will include the labels
    # hours, noise, location, jewelery, and furniture and the minimum probability goes lower
    FUR_PROB = 0.4; FUR_MIN = 1; FUR_MAX = 15;
    DENT_PROB = 0.6; DENT_MIN = 3; DENT_MAX = 25;
    MED_PROB = 0.6; MED_MIN = 3; MED_MAX = 25;
    JEW_PROB = 0.6; JEW_MIN = 3; JEW_MAX = 25;
    HOTEL_PROB = 0.6; HOTEL_MIN = 3; HOTEL_MAX = 10;
    MEDICINE_PROB = 0.6; MEDICINE_MIN = 3; MEDICINE_MAX = 10;

    properties = {}
    # The mapping part. The keys of the properties dict correspond to the folder names under the
    # "general" directory.
    if label == "museum_gallery":
        properties["art"] = createProperties(ART_PROB, ART_MIN, ART_MAX)
    if label == "apparel":
        properties["clothing"] = createProperties(CLO_PROB, CLO_MIN, CLO_MAX)
    if label == "restaurant":
        properties["menu"] = createProperties(MENU_PROB, MENU_MIN, MENU_MAX)
    if label == "furniture":
        properties["furniture"] = createProperties(FUR_PROB, FUR_MIN, FUR_MAX)
        properties["jewellery"] = createProperties(JEW_PROB, JEW_MIN, JEW_MAX)
    if label == "medical":
        properties["dental"] = createProperties(DENT_PROB, DENT_MIN, DENT_MAX)
        properties["medicine"] = createProperties(MEDICINE_PROB, MEDICINE_MIN, MEDICINE_MAX)
    if label == "jewellery":
        properties["jewellery"] = createProperties(JEW_PROB, JEW_MIN, JEW_MAX)
    if label == "hotel":
        properties["hotel"] = createProperties(HOTEL_PROB, HOTEL_MIN, HOTEL_MAX)

    properties["hours"] = createProperties(HOURS_PROB, HOURS_MIN, HOURS_MAX)
    properties["location"] = createProperties(LOC_PROB, LOC_MIN, LOC_MAX, LOC_THRES)    
    return properties

"""
Takes in an input path and returns a namedtuple.
"labels" contain all the information:
    {"location": [...], "clothing": [...], ... }
"""
def parse(inputFilePath, fileName):

    start_time = time.time()
    print inputFilePath
    print fileName
    parsedJSON = JsonParser.parseData(inputFilePath, fileName)

    # Obtain the correct general training folder mappings.
    label = parsedJSON.type.label
    print label
    trainingdirs = labelToDirsMapping(label)
    generalpath = os.path.join(settings.APP_DATA_TRAINING, "general")

    # Generate the training paths to be passed into the NBC.
    trainingpaths = []
    for dir in trainingdirs:
        trainingpaths.append(os.path.join(generalpath, dir))

    businessData = parseBusinessData(parsedJSON, trainingpaths)
    labels = parseLabels(businessData, parsedJSON)

    print "Total time approximatately " + str((time.time() - start_time))  + " seconds"
    Business = namedtuple("Business", ["name", "type", "data", "labels"])
    return Business(parsedJSON.name, parsedJSON.type, businessData, labels)

"""
business = parse(os.path.join(settings.APP_DATA_HTML, "escada_com.txt"))
for label, items in business.labels.items():
    print label
    print "\n"
    print items
    print "\n\n"
"""

"""
# Prints out all attributes from general that have been classified.
for key, value in business.data.items():
    print "----------------------------------------"
    print key, list(set(value))
"""

def demo():
    generalpath = os.path.join(settings.APP_DATA_TRAINING, "general")
    trainingfolders = []
    for generallabel in listdir(generalpath):
        if generallabel in ["menu", "location", "noise", "hours"]:
            trainingfolders.append(os.path.join(generalpath, generallabel))
    nbc = NaiveBayesClassifier(trainingfolders, settings.APP_DATA_COMMON_WORDS)
    nbc.demo()

#demo()

