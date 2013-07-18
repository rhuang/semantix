import os

# Input         -   map     :   The map that contains the newly trained values from the UI. This map has key with filename and value with a list of words
#                               Example structure : 
#
#                               "Outer_Folder": {
#                                  "InnerFolder" : {
#                                    "FileName": 
#                                      [
#                                         "apples",
#                                         "BANANA",
#                                      ]
#                                    },
#                                }
#
#                   path    :   The running path while recursing through the map
#
# Description   -   Iterate through the map structure and take the values from the map and overwrite/create the file from the path that the map specifies
#                   The path is created through recursing until there is no more dict type, at which point the list of values is written into the file
#                   If the folder structure does not exist, it is created else the file that had old data is now over-written

def recurseAndApplyData(map, path):
    for key, value in map.iteritems():
        if isinstance(value, dict):
            recurseAndApplyData(value, os.path.join(path, key))
        else:
            if not os.path.exists(path):
                os.makedirs(path)
            filePath = os.path.join(path, key)
            file = open(filePath, 'w+')

            value = list(set(value))                    # remove duplicates
            value.sort()                                # sort
            for item in value:                          # iterate
                file.write("%s\n" % item.lower())       # lower

# Input         - map                   : The map that contains the newly trained values from the UI. This map has key with filename and value with a list of words
#               - trainingFolder        : The folder that has all the training data
# Description   - Check if the map has been received correctly from the client. If yes then call recurseAndApplyData
# Output        - True if the new data has been correctly saved , False if there was a problem while saving the data

def saveTrainedData(map, trainingFolder):

    if map is None:
        sys.stderr.write("abort: could not receive trained map of data")
        return False

    recurseAndApplyData(map, trainingFolder)
    return True

def getTextFromFile(path):
    terms = []
    with open(path) as inputFile:
        for line in inputFile:
            terms.append(line.strip())
    return terms

def getCategories(path):
    data = {}
    files = os.listdir(path)
    for f in files:
        new_path = os.path.join(path, f)
        if os.path.isdir(new_path):
            data[f] = getCategories(new_path)
        elif os.path.isfile(new_path):
            data[f] = getTextFromFile(new_path)
    return data