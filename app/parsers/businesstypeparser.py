import re
from collections import namedtuple

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
    
    
    # For testing.
    #
    #for label in frequencies:
    #    print '%s | %s' % (label, frequencies[label]['frequency'])
    
    
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

"""
Get the business type of the business file.
"""
def parse(soups, nbc):
    labels = []
    for soup in soups:
        #print "------------------------------------------------------------------------------"
        #print soup.getText()
        labels.append(nbc.classify(soup.getText()))


    #for label in labels:
    #    print label

    label = highestFrequency(labels)
    businessType = namedtuple('Type', ['label', 'probability'])

    return businessType(label['label'], label['probability'])
