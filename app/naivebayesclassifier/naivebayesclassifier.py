import os
import sys
from nltk.probability import ELEProbDist, FreqDist
import nltk
from nltk.probability import ELEProbDist, FreqDist
from collections import defaultdict
from os import listdir
from os.path import isfile, join

"""
Example:
nbc = NaiveBayesClassifier('/path/to/training/folder')
item = nbc.classify('classify this')
# If you want to train other preset data, do this:
nbc.train('/path/to/training/folder')
"""
class NaiveBayesClassifier:   
    """
    These private variables are initialized by self.train()
        self.labels - ['label1, label2']
        self.__trainingSet - {'feature': ['label1, label2']}
        self.__featuresSet - {'feature: {'label1': 1, 'label2': 0}}
        self.__labelProbabilityDistribution
        self.__featureProbabilityDistribution

    @param trainingDirectory A valid absolute path from the training directory.
    """
    def __init__(self, trainingDirectory):
        if trainingDirectory is None:
            raise Exception('Please input an absolute path training directory.')
        # Start training.
        self.__trainingDirectory = trainingDirectory.lower()
        self.train(self.__trainingDirectory)

    """ Creates and returns a training set (dictionary) from one data file belonging to a label. """
    def __updateTrainingSet(self, fileName, label):
        trainingSet = defaultdict(list)
        with open(fileName) as trainingFile:
            lines = trainingFile.readlines()
            for line in lines:
                trainingSet[line.strip()].append(label)
        # Add the new features:labels to the training set.
        for item, labels in trainingSet.items():
            self.__trainingSet[item].extend(labels)

    """
    Train the classifier by iterating through the folder that contains the data.
    @param trainingDataType = 'data' or 'businesses' so far.
    """
    def __generateTrainingSet(self):
        # Use a defaultdict(list) because the same feature can belong to multiple labels.
        self.__trainingSet = defaultdict(list)
        self.labels = []
        # Ignore some OS generated files, as well as default folders that should not be included.
        # For example, we ignore 'businesses', but if we need 'businesses' we will only be looking
        # inside 'businesses' folder and nothing else.
        # Could be changed!
        ignores = ['.DS_Store']
        trainingDirectory = self.__trainingDirectory

        # Loop through each folder name for the training folder. The folder name corresponds to a label.
        for label in listdir(trainingDirectory):
            if label not in ignores:
                # Add the folder name as a 'label'.
                self.labels.append(label)
                # Obtain the absolute path of the folder.
                path = os.path.join(trainingDirectory, label)
                # Loop through each training file of each folder.
                for fileName in [f for f in listdir(path) if isfile(join(path, f))]:
                    # Obtain the absolute path of the file.
                    absFileName = os.path.join(path, fileName)
                    # Update the training set dictionary with the training set from the file.
                    self.__updateTrainingSet(absFileName, label)

    """ Check if a string is an integer. """
    def __isInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

    """
    Tokenize the input, perform some label specific feature work, and assign to kvp with
    value of true.
    """
    def __tokenizeInputToFeatures(self, item):
        words = item.split()
        splits = {}

        # Location feature.
        ordinals = ['st', 'nd', 'rd', 'th']

        for word in words:
            """
            LOCATION FEATURES SPECIFIC.
            """
            # Consider all numbers as one category for location. 10 because full address is about
            # 10 tokens.
            if self.__isInt(word) and len(words) < 10:
                word = 'number'
            elif len(word) > 2:
                # Check if this word is an ordinal number like '1st' for location feature.
                if word[-2:] in ordinals and self.__isInt(word[:-2]):
                    word = 'ordinal'
            """
            /LOCATION FEATURES SPECIFIC.
            """
            splits[word] = True
        return splits

    """ Generates the features set. """
    def __generateFeaturesSet(self):
        def generateDefaultFreq():
            frequencies = {}
            for label in self.labels:
                frequencies[label] = 0
            return frequencies

        featuresSet = {}
        for text, labels in self.__trainingSet.items():
            tokens = text.split()
            for token in tokens:
                if token not in featuresSet:
                    featuresSet[token] = generateDefaultFreq()
                # Loop through all labels associated with this feature.
                for label in labels:
                    featuresSet[token][label] += 1
        self.__featuresSet = featuresSet

    """ Generates expected likelihood distribution for labels. """
    def __generateLabelProbabilityDistribution(self):
        # Print this out to look at how many items were trained for each label.
        labelFrequencies = FreqDist()
        for item, counts in self.__featuresSet.items():
            for label in self.labels:
                if counts[label] > 0:
                    labelFrequencies.inc(label)

        self.__labelProbabilityDistribution = ELEProbDist(labelFrequencies)

    """ Generates expected likelihood distribution for features. """
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

    """
    Train the classifier.
    @param trainingDirectory A valid absolute path from the training directory.
    """
    def train(self, trainingDirectory):
        self.__trainingDirectory = trainingDirectory
        self.__generateTrainingSet()
        self.__generateFeaturesSet()
        self.__generateLabelProbabilityDistribution()
        self.__generateFeatureProbabilityDistribution()
        self.__classifier = nltk.NaiveBayesClassifier(self.__labelProbabilityDistribution, self.__featureProbabilityDistribution)

    """ Classify an item. """
    def classify(self, item):
        item = item.lower()
        label = self.__classifier.classify(self.__tokenizeInputToFeatures(item))
        return (label, self.__classifier.prob_classify(self.__tokenizeInputToFeatures(item)).prob(label))

    """ Print some demo items. """
    def demo(self):
        testingSet = {
            'We are at 444 Weber Street',
            'steak bread hot dog',
            '888 Socks Drive',
            'chicken broccoli',
            '8 oz steak',
            'turkey club',
            "2:00 pm",
            "8:00 AM to 8:00 PM",
            "6th street"
        }
        for item in testingSet:
            probs = {}
            results = self.classify(item)
            for label in self.labels:
                probs[label] = round(self.__classifier.prob_classify(self.__tokenizeInputToFeatures(item.lower())).prob(label), 2)
            print '%s | %s | %s | %s' % (item, results[0], results[1], probs)
        print '\n'
