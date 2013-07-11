from nltk.probability import ELEProbDist, FreqDist
import nltk
from collections import defaultdict
import os
from os import listdir
from os.path import isfile, join
import settings

class NaiveBayesClassifier:
    def __init__(self):
        self.labels = []
        self.__trainingSet = {}
        self.train()

    # Creates and returns a training set (dictionary) from one data file belonging to a label.
    def __updateTrainingSet(self, fileName, label):
        trainingSet = {}
        with open(fileName) as trainingFile:
            lines = trainingFile.readlines()
            for line in lines:
                trainingSet[line.strip()] = label
        return self.__trainingSet.update(trainingSet)

    # Train the classifier by iterating through the folder that contains the data.
    def __generatesTrainingSet(self):
        # Loop through each folder name for the training folder. The folder name corresponds to a label.
        for label in listdir(settings.APP_DATA_TRAINING):
            # Add the folder name as a 'label'.
            self.labels.append(label)
            # Obtain the absolute path of the folder.
            path = os.path.join(settings.APP_DATA_TRAINING, label)
            # Loop through each training file of each folder.
            for fileName in [f for f in listdir(path) if isfile(join(path, f))]:
                # Obtain the absolute path of the file.
                absFileName = os.path.join(path, fileName)
                # Update the training set dictionary with the training set from the file.
                self.__updateTrainingSet(absFileName, label)

    # Check if a string is an integer.
    def __isInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

    def __splitTrue(self, item):
        words = item.split()
        splits = {}
        for word in words:
            # Consider all numbers as one category.
            if self.__isInt(word):
                word = 'number'
            splits[word.lower()] = True
        return splits

    # Generates the features set.
    def __generateFeaturesSet(self):
        def generateDefaultFreq():
            frequencies = {}
            for label in self.labels:
                frequencies[label] = 0
            return frequencies

        featuresSet = {}
        for text, label in self.__trainingSet.items():
            tokens = text.split()
            for token in tokens:
                # Consider all numbers as one category.
                if self.__isInt(token):
                    token = 'number'
                if token not in featuresSet:
                    featuresSet[token] = generateDefaultFreq()
                featuresSet[token][label] += 1
        self.__featuresSet = featuresSet

    # Generates expected likelihood distribution for labels.
    def __generateLabelProbabilityDistribution(self):
        labelFrequencies = FreqDist()
        for item, counts in self.__featuresSet.items():
            for label in self.labels:
                if counts[label] > 0:
                    labelFrequencies.inc(label)

        self.__labelProbabilityDistribution = ELEProbDist(labelFrequencies)

    # Generates expected likelihood distribution for features.
    def __generateFeatureProbabilityDistribution(self):
        frequencyDistributions = defaultdict(FreqDist)
        values = defaultdict(set)
        numberSamples = len(self.__trainingSet) / 2
        for token, counts in self.__featuresSet.items():
            for label in self.labels:
                frequencyDistributions[label, token].inc(True, count = counts[label])
                frequencyDistributions[label, token].inc(None, numberSamples - counts[label])
                values[token].add(None)
                values[token].add(True)
        probabilityDistribution = {}
        for ((label, name), freqDist) in frequencyDistributions.items():
            eleProbDist = ELEProbDist(freqDist, bins = len(values[name]))
            probabilityDistribution[label, name] = eleProbDist

        self.__featureProbabilityDistribution = probabilityDistribution

    def train(self):
        self.__generatesTrainingSet()
        self.__generateFeaturesSet()
        self.__generateLabelProbabilityDistribution()
        self.__generateFeatureProbabilityDistribution()
        self.__classifier = nltk.NaiveBayesClassifier(self.__labelProbabilityDistribution, self.__featureProbabilityDistribution)

    def classify(self, item):
        label = self.__classifier.classify(self.__splitTrue(item.lower()))
        return (label, self.__classifier.prob_classify(self.__splitTrue(item.lower())).prob(label))

    def demo(self):
        testingSet = {
            'We are at 444 Weber Street',
            'steak bread hot dog',
            '888 Socks Drive',
            'chicken broccoli lol',
            '8 oz steak',
            'turkey club',
            "2:00 pm"

        }
        for item in testingSet:
            result = self.classify(item)
            print "%s | %s | %s" % (item, result[0], result[1])
