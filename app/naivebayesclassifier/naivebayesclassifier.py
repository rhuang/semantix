import os, sys, re
from nltk.probability import ELEProbDist, FreqDist, DictionaryProbDist, sum_logs, _NINF
from collections import defaultdict, namedtuple
from os import listdir
from os.path import isfile, join

"""
Example:
nbc = NaiveBayesClassifier('/path/to/training/folder')
item = nbc.classify('classify this')
"""
class NaiveBayesClassifier:   
    """
    These private variables are initialized by self._train()
        self._labels - ['label1, label2']
        self._trainingset - {'feature': ['label1, label2']}
        self._featuresset - {'feature: {'label1': 1, 'label2': 0}}
        self._featureprobabilitydistribution

    @param trainingfolders An array of valid absolute paths.
    @param commonwordsfolder Aa valid absolute path to the common words folder.
    """
    def __init__(self, trainingfolders, commonwordsfolder):
        if trainingfolders is None:
            raise Exception('Please input an absolute path training directory.')

        # Start training.
        self._commonwords = self._getCommonWords(commonwordsfolder)
        self._trainingfolders = trainingfolders
        self._trainingset = defaultdict(list)
        self._labels = set()
        self._generateTrainingSet()
        self._generateFeaturesSet()
        self._generateFeatureProbabilityDistribution()

    """
    Creates and returns a training set (dictionary) from one data file belonging to a label.
    """
    def _updateTrainingSet(self, filename, label):
        trainingset = defaultdict(list)
        with open(filename) as trainingfile:
            lines = trainingfile.readlines()
            for line in lines:
                trainingset[line.strip()].append(label)
        # Add the new features:labels to the training set.
        for item, labels in trainingset.items():
            self._trainingset[item].extend(labels)

    """
    Ensures that common words are not considered to avoid under representing matched words.
    @returns A list of common words extracted from the common words directory.
    """
    def _getCommonWords(self, commonwordsfolder):
        commonwords = [] 
        for root, dirs, files in os.walk(commonwordsfolder):
            for file in files:
                if file.endswith(".txt"):
                    f = open(os.path.join(commonwordsfolder, file), 'r')
                    for line in f:
                        commonwords.append(line.strip('\r\n') )
                    f.close()
        return commonwords

    """
    Train the classifier by iterating through the folder that contains the data.
    """
    def _generateTrainingSet(self):
        ignores = [".DS_Store"]
        for folderpath in self._trainingfolders:
            basename = os.path.basename(folderpath)
            if basename not in ignores:
                for sublabel in listdir(folderpath):
                    if sublabel not in ignores:
                        label = str(basename) + ":" + str(sublabel)
                        self._labels.add(label)
                        sublabelpath = os.path.join(folderpath, sublabel)
                        with open(sublabelpath) as trainingfile:
                            lines = trainingfile.readlines()
                            for line in lines:
                                self._trainingset[line.strip()].append(label)

    """
    Tokenize the input, perform some label specific feature work, and assign to kvp with
    value of true.
    Generates the features set for the input data
    """
    def _tokenizeInputToFeatures(self, item):
        words = filter(None, re.split("[ ?!.,-]", item))
        splits = {}

        # Location feature.
        ordinals = ['st', 'nd', 'rd', 'th']
        numOrdinals = 1

        for word in words:
            if word not in self._commonwords:
                """
                LOCATION FEATURES SPECIFIC.
                """
                # Consider all numbers as one category for location. 10 because full address is
                # about 10 tokens.
                if word.isdigit() and len(words) < 10:
                    word = 'number'
                elif len(word) > 2:
                    # Check if this word is an ordinal number like '1st' for location feature.
                    if word[-2:] in ordinals and word[:-2].isdigit():
                        word = 'ordinal' + str(numOrdinals)
                        numOrdinals += 1
                """
                /LOCATION FEATURES SPECIFIC.
                """
                splits[word] = True

        return splits

    """
    Generates the features set for the training data.
    """
    def _generateFeaturesSet(self):
        def generateDefaultFreq():
            frequencies = {}
            for label in self._labels:
                frequencies[label] = 0
            return frequencies

        featuresset = {}
        for text, labels in self._trainingset.items():
            # Split on these characters.
            tokens = re.split('[ .,-]', text)
            for token in tokens:
                if token not in self._commonwords:
                    if token not in featuresset:
                        featuresset[token] = generateDefaultFreq()
                    # Loop through all labels associated with this feature.
                    for label in labels:
                        featuresset[token][label] += 1
        self._featuresset = featuresset

    """
    Generates expected likelihood distribution for features.
    """
    def _generateFeatureProbabilityDistribution(self):
        frequencyDistributions = defaultdict(FreqDist)
        values = defaultdict(set)
        numberSamples = len(self._trainingset) /2 

        for token, counts in self._featuresset.items():
            for label in self._labels:
                frequencyDistributions[label, token].inc(True, count = counts[label])
                frequencyDistributions[label, token].inc(None, numberSamples - counts[label])
                values[token].add(None)
                values[token].add(True)

        probabilityDistribution = {}
        for ((label, name), freqDist) in frequencyDistributions.items():
            eleProbDist = ELEProbDist(freqDist, bins=len(values[name]))
            probabilityDistribution[label, name] = eleProbDist

        self._featureprobabilitydistribution = probabilityDistribution

    """
    Classifies an item.
    @return A tuple of best classified label with its probability.
    """
    def classify(self, input): 
        input = input.lower()
        inputFeatureSet = self._tokenizeInputToFeatures(input)
        classifiedDataTuple = namedtuple('ClassifiedData', ['label', 'probability'])

        probabilityDistribution = self._prob_classify(inputFeatureSet)
        # Max is taking the label with the highest probability.
        label = probabilityDistribution.max()
        # Get the probability.
        probability = probabilityDistribution.prob(label)

        return classifiedDataTuple(label, probability)

    """
    Overwrites _prob_classify of nltk so that we can force label frequencies to be empty, otherwise
    label frequencies will skew our results in favor of which label has the most trained data.
    """
    def _prob_classify(self, featureset):
        featureset = featureset.copy() 
        for fname in featureset.keys(): 
            for label in self._labels: 
                if (label, fname) in self._featureprobabilitydistribution: 
                    break 
            else: 
                #print 'Ignoring unseen feature %s' % fname 
                del featureset[fname] 

        # Start with a log probability of 0 to avoid skewing towards larger data sets
        logprob = {} 
        for label in self._labels: 
            logprob[label] = 0                 

        # Add in the log probability of features given labels. 

        for label in self._labels: 
            for (fname, fval) in featureset.items(): 

                if (label, fname) in self._featureprobabilitydistribution: 
                    feature_probs = self._featureprobabilitydistribution[label,fname] 
                    #print "log prob for " + str(label) +  " is " + str(feature_probs.logprob(fval) )
                    logprob[label] += feature_probs.logprob(fval) 
                else: 
                # nb: This case will never come up if the classifier was created by 
                # NaiveBayesClassifier.train(). 
                    logprob[label] += sum_logs([]) # = -INF.
        
        # print out the log prob for each label before normalizing
        #for key,value in  self._featureprobabilitydistribution.items():
        #    print "key value of featureProbabilityDistribution " + str(key) + "," + str(value.freqdist() )

        #print "log prob with features is " + str(logprob)    
        dictprobDist = DictionaryProbDist(logprob, normalize=True, log=True)

        ## print out the probability for each label
        #for label in dictprobDist.samples():
        #    print label + " is probability " + str(dictprobDist.prob(label))

        return dictprobDist

    """
    Print some demo items.
    """
    def demo(self):
        testingSet = {
            "1st Street and 2nd Street, Canada",
            'We are at 444 Weber Street, CA',
            'steak bread hot dog',
            '888 Socks Drive, CA',
            'chicken broccoli',
            '8 oz steak',
            'turkey club',
            "9:00 aM",
            "pm canada facebook",
            "8:00 AM to 9:00 PM",
            "6th street",
            "Mona Lisa",
            "Margaret Magnetic North: The Landscapes of Tom Uttech Milwaukee: Milwaukee Art Museum",
            "pizzas"
        }

        for item in testingSet:
            probs = {}
        
            print "-------------------------------------------------------"

            item = item.lower()
            featureset = self._tokenizeInputToFeatures(item)

            probabilityDistribution = self._prob_classify(featureset)
            # Max is taking the label with highest probability.
            label = probabilityDistribution.max()
            # Getting its probability.
            probability = probabilityDistribution.prob(label)

            for labelItem in probabilityDistribution.samples():
                probs[labelItem] = str(probabilityDistribution.prob(labelItem))
            print '%s | %s | %s | %s' % (item, label, probability, probs)

        print '\n'

