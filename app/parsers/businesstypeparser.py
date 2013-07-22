import re
import collections

# Go through list of all categories and finds the category with highest total probability.
def getHighestProbability(allCategories):
    uniqueCategories = []
    probabilities = []

    highestProbability = 0;
    for category in allCategories:
        if not category[0] in uniqueCategories:
            uniqueCategories.append(category[0])
            probabilities.append(category[1])
            if(highestProbability < category[1]):
                highestProbability = category[1];
        else:
            categoryIndex = uniqueCategories.index(category[0])
            probabilities[categoryIndex] += category[1]
            if(highestProbability < probabilities[categoryIndex]):
                highestProbability = probabilities[categoryIndex]

    returnIndex = probabilities.index(highestProbability)
  
    highestProbCategory = []
    highestProbCategory.append(uniqueCategories[returnIndex])
    highestProbCategory.append(highestProbability)
    
    return highestProbCategory

"""
From a list of labels and their frequencies, retrieve the label with highest frequency and the
average probability of that label.
"""
def highestFrequency(labels):
    frequencies = {}
    for label in labels:
        if label[0] not in frequencies:
            frequencies[label[0]] = {'frequency': 1, 'probabilities': [label[1]]}
        else:
            frequencies[label[0]]['frequency'] += 1
            # Accumulate a list of probabilities.
            frequencies[label[0]]['probabilities'].append(label[1])
    
    result = []
    highest = 0
    for label in frequencies:
        frequency = frequencies[label]['frequency']
        if frequency > highest:
            highest = frequency
            # Calculate average probability.
            averageProbability = 0
            for probability in frequencies[label]['probabilities']:
                averageProbability += probability
            averageProbability /= frequency

            businessTypeLabel = collections.namedtuple('BusinessTypeLabel', ['businessLabel', 'businessAverageProbability'])
            result = businessTypeLabel(label, averageProbability)

    """
    # For testing.
    for label in frequencies:
        print '%s | %s' % (label, frequencies[label]['frequency'])
    """
    return result

"""
Get the business type of the business file.
"""
def parseBusinessType(businessFile, soups, nbc):
    labels = []
    for soup in soups:
        labels.append(nbc.classify(soup.getText()))
    businessTypeTuple = collections.namedtuple('BusinessType', ['businessFile', 'businessTypeLabel'])

    return businessTypeTuple(businessFile,highestFrequency(labels))