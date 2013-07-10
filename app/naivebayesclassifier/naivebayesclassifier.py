'''
import nltk
from nltk.corpus import names
import random

def gender_features(word):
    return {'last_leter': word[-1]}

names = ([(name, 'male') for name in names.words('male.txt')] +
         [(name, 'female') for name in names.words('female.txt')])
random.shuffle(names)

featuresets = [(gender_features(n), g) for (n, g) in names]

train_set = featuresets[500:]
test_set = featuresets[:500]

classifier = nltk.NaiveBayesClassifier.train(train_set)

def test_set():
    return [(gender_features('raymond'), '')]

print classifier.classify(gender_features('Raymond'))
print nltk.classify.accuracy(classifier, [(gender_features('Josephine'), 'female'),
                                          (gender_features('Raymond'), 'female')])

classifier.show_most_informative_features(5)

#[({'last_leter': 'l'}, 'male'), 
# ({'last_leter': 's'}, 'female')

def generateFeatures(text, label):
    features = []
    tokens = text.split
    for token in tokens:
        features.append({token: })

def menu_features(item):
    return {'menu': item}

def location_features(location):
    return {'location': location}

def training_set():
    return [(menu_features('oven-roasted chicken'), 'menu'),
        (menu_features('rib eye steak'), 'menu'),
        (menu_features('mushroom burger'), 'menu'),
        (menu_features('fried chicken'), 'menu'),
        (location_features('10511 168 Street'), 'location'),
        (location_features('293 Hemlock Street'), 'location'),
        (location_features('11-45 46th Road, Long Island City'), 'location'),
        (location_features('321 Lester Street, #201'), 'location')]

def test_set():
    return [(location_features('888 Foder Street'), 'location')]

nbc = nltk.NaiveBayesClassifier.train(training_set())
print nbc.classify(menu_features('bacon stuffed chicken'))
print nbc.classify(location_features('148 Weber Street, Waterloo'))
print nbc.show_most_informative_features(4)
print nltk.classify.accuracy(nbc, test_set())
'''

from nltk.probability import ELEProbDist, FreqDist
from nltk import NaiveBayesClassifier
from collections import defaultdict
import os
import settings

testingSet = {
    'We are at 444 Weber Street',
    'steak bread hot dog',
    '888 Socks Drive',
    'chicken broccoli lol',
    '8 oz steak',
    'turkey club'
}

def labels():
    return ['menu', 'location', 'noise']

def trainingSet():
    def createTrainingDict(fileName, category):
        trainingSet = {}
        with open(fileName) as file:
            lines = file.readlines()
            for line in lines:
                trainingSet[line.strip()] = category
        return trainingSet

    def training(files, label):
        for file in files:
            trainingSet.update(createTrainingDict(os.path.join(settings.APP_DATA_ASSETS, file), label))

    trainingSet = {}
    locationFiles = ['countries', 'states', 'addresses']
    menuFiles = ['menus']
    noiseFiles = ['noise']

    training(locationFiles, 'location')
    training(menuFiles, 'menu')
    training(noiseFiles, "noise")

    return trainingSet

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def splitTrue(item):
    words = item.split()
    splits = {}
    for word in words:
        # Consider all numbers as one category.
        if isInt(word):
            word = 'number'
        splits[word.lower()] = True
    return splits

# Generates features set: {'steak': {'menu': 1, 'location': 0}}.
def generateFeaturesSet(trainingSet):
    def generateDefaultFreq():
        frequencies = {}
        for category in labels():
            frequencies[category] = 0
        return frequencies

    frequencies = {}
    for text, label in trainingSet.items():
        tokens = text.split()
        for token in tokens:
            # Consider all numbers as one category.
            if isInt(token):
                token = 'number'
            if token not in frequencies:
                frequencies[token] = generateDefaultFreq()
            frequencies[token][label] += 1
    return frequencies

# Generates expected likelihood distribution for labels.
def getLabelProbabilityDistribution(features):
    labelFrequencies = FreqDist()
    for item, counts in features.items():
        for label in labels():
            if counts[label] > 0:
                labelFrequencies.inc(label)
    print labelFrequencies
    return ELEProbDist(labelFrequencies)

# Generates expected likelihood distribution for features.
def getFeatureProbabilityDistribution(features):
    frequencyDistributions = defaultdict(FreqDist)
    values = defaultdict(set)
    numberSamples = len(trainingSet()) / 2
    for token, counts in features.items():
        for label in labels():
            frequencyDistributions[label, token].inc(True, count = counts[label])
            frequencyDistributions[label, token].inc(None, numberSamples - counts[label])
            values[token].add(None)
            values[token].add(True)
    '''
    for item in frequencyDistributions.items():
        print item[0], item[1]
    '''
    probabilityDistribution = {}
    for ((label, name), freqDist) in frequencyDistributions.items():
        eleProbDist = ELEProbDist(freqDist, bins = len(values[name]))
        probabilityDistribution[label, name] = eleProbDist
    return probabilityDistribution

featuresSet = generateFeaturesSet(trainingSet())

labelProbabilityDistribution = getLabelProbabilityDistribution(featuresSet)

featureProbabilityDistribution = getFeatureProbabilityDistribution(featuresSet)

classifier = NaiveBayesClassifier(labelProbabilityDistribution, featureProbabilityDistribution)

def classify(item):
    label = classifier.classify(splitTrue(item.lower()))
    return (label, classifier.prob_classify(splitTrue(item.lower())).prob(label))

for item in testingSet:
    result = classify(item)
    print "%s | %s | %s" % (item, result[0], result[1])

#classifier.show_most_informative_features()
