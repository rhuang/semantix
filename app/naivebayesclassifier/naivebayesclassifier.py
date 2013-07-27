import os, sys, re
from nltk.probability import ELEProbDist, FreqDist, DictionaryProbDist, sum_logs, _NINF
from collections import defaultdict,namedtuple
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
        self._trainingSet - {'feature': ['label1, label2']}
        self._featuresSet - {'feature: {'label1': 1, 'label2': 0}}
        self._labelProbabilityDistribution
        self._featureProbabilityDistribution

    @param trainingDirectory A valid absolute path from the training directory.
    """
    def __init__(self, trainingDirectory, commonWordsDirectory):
        if trainingDirectory is None:
            raise Exception('Please input an absolute path training directory.')

        # Start training.
        self._commonwords = self._getCommonWords(commonWordsDirectory)
        self._trainingDirectory = trainingDirectory
        self.train(self._trainingDirectory)

    """ Creates and returns a training set (dictionary) from one data file belonging to a label. """
    def _updateTrainingSet(self, fileName, label):
        trainingSet = defaultdict(list)
        with open(fileName) as trainingFile:
            lines = trainingFile.readlines()
            for line in lines:
                trainingSet[line.strip()].append(label)
        # Add the new features:labels to the training set.
        for item, labels in trainingSet.items():
            self._trainingSet[item].extend(labels)

    '''returns a list of common words extracted from the common words directory'''
    '''ensures that none of the tokens in the training or input get higher ratings based on common words'''
    def _getCommonWords(self, commonWordsDirectory):
        commonwords = [] 
        for root,dirs,files in os.walk(commonWordsDirectory):
            for file in files:
                if file.endswith(".txt"):
                    f = open(os.path.join(commonWordsDirectory,file), 'r')
                    for line in f:
                        commonwords.append(line.strip('\r\n') )
                    f.close()
        return commonwords

    """
    Train the classifier by iterating through the folder that contains the data.
    @param trainingDataType = 'data' or 'businesses' so far.
    """
    def _generateTrainingSet(self):
        # Use a defaultdict(list) because the same feature can belong to multiple labels.
        self._trainingSet = defaultdict(list)
        self.labels = []
        # Ignore some OS generated files, as well as default folders that should not be included.
        # For example, we ignore 'businesses', but if we need 'businesses' we will only be looking
        # inside 'businesses' folder and nothing else.
        # Could be changed!
        ignores = ['.DS_Store']
        trainingDirectory = self._trainingDirectory

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
                    self._updateTrainingSet(absFileName, label)

    """ Check if a string is an integer. """
    def _isInt(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

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

        for word in words:
            if word not in self._commonwords :

                """
                LOCATION FEATURES SPECIFIC.
                """
                # Consider all numbers as one category for location. 10 because full address is about
                # 10 tokens.
                if self._isInt(word) and len(words) < 10:
                    word = 'number'
                elif len(word) > 2:
                    # Check if this word is an ordinal number like '1st' for location feature.
                    if word[-2:] in ordinals and self._isInt(word[:-2]):
                        word = 'ordinal'
                """
                /LOCATION FEATURES SPECIFIC.
                """
                splits[word] = True

        return splits

    """ Generates the features set for the training data """
    def _generateFeaturesSet(self):
        def generateDefaultFreq():
            frequencies = {}
            for label in self.labels:
                frequencies[label] = 0
            return frequencies

        featuresSet = {}
        for text, labels in self._trainingSet.items():
            tokens = re.split('[ .,-]', text) # split on space, period, comma, dash
            for token in tokens:

                if token not in self._commonwords :
                    if token not in featuresSet:
                        featuresSet[token] = generateDefaultFreq()
                    # Loop through all labels associated with this feature.
                    for label in labels:
                        featuresSet[token][label] += 1
        self._featuresSet = featuresSet

    """ Generates expected likelihood distribution for features. """
    def _generateFeatureProbabilityDistribution(self):
        frequencyDistributions = defaultdict(FreqDist)
        values = defaultdict(set)
        numberSamples = len(self._trainingSet) /2 

        for token, counts in self._featuresSet.items():
            for label in self.labels:
                frequencyDistributions[label, token].inc(True, count = counts[label])
                frequencyDistributions[label, token].inc(None, numberSamples - counts[label])
                values[token].add(None)
                values[token].add(True)

        probabilityDistribution = {}
        for ((label, name), freqDist) in frequencyDistributions.items():
            eleProbDist = ELEProbDist(freqDist, bins=len(values[name]))
            probabilityDistribution[label, name] = eleProbDist

        self._featureProbabilityDistribution = probabilityDistribution

    """
    Train the classifier.
    @param trainingDirectory A valid absolute path from the training directory.
    """
    def train(self, trainingDirectory):
        self._trainingDirectory = trainingDirectory
        self._generateTrainingSet()
        self._generateFeaturesSet()
        self._generateFeatureProbabilityDistribution()


    """ Classify an item"""
    """ returns a tuple of best classified label with its probability"""
    def classify(self, input): 

        input = input.lower()
        inputFeatureSet = self._tokenizeInputToFeatures(input)
        classifiedDataTuple = namedtuple('ClassifiedData', ['label', 'probability'])

        probabilityDistribution = self.prob_classify(inputFeatureSet)
        label = probabilityDistribution.max()                       # max is taking the label with highest probability
        probability = probabilityDistribution.prob(label)           # getting its probability

        return classifiedDataTuple(label, probability)

    def prob_classify(self, featureset):
    
        featureset = featureset.copy() 
        for fname in featureset.keys(): 
            for label in self.labels: 
                if (label, fname) in self._featureProbabilityDistribution: 
                    break 
            else: 
                #print 'Ignoring unseen feature %s' % fname 
                del featureset[fname] 

        # Start with a log probability of 0 to avoid skewing towards larger data sets
        logprob = {} 
        for label in self.labels: 
            logprob[label] = 0                 

        # Add in the log probability of features given labels. 

        for label in self.labels: 
            for (fname, fval) in featureset.items(): 

                if (label, fname) in self._featureProbabilityDistribution: 
                    feature_probs = self._featureProbabilityDistribution[label,fname] 
                    #print "log prob for " + str(label) +  " is " + str(feature_probs.logprob(fval) )
                    logprob[label] += feature_probs.logprob(fval) 
                else: 
                # nb: This case will never come up if the classifier was created by NaiveBayesClassifier.train(). 
                    logprob[label] += sum_logs([]) # = -INF.
        
        ## print out the log prob for each label before normalizing
        #for key,value in  self._featureProbabilityDistribution.items():
        #    print "key value of featureProbabilityDistribution " + str(key) + "," + str(value.freqdist() )

        #print "log prob with features is " + str(logprob)    
        dictprobDist = DictionaryProbDist(logprob, normalize=True, log=True)

        ## print out the probability for each label
        #for label in dictprobDist.samples():
        #    print label + " is probability " + str(dictprobDist.prob(label))

        return dictprobDist


    """ Print some demo items. """
    def demo(self):
        testingSet = {
            
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
             "Margaret Magnetic North: The Landscapes of Tom Uttech Milwaukee: Milwaukee Art Museum"
            
        }
        for item in testingSet:
            probs = {}
        
            print "-------------------------------------------------------"

            item = item.lower()
            featureset = self._tokenizeInputToFeatures(item)

            probabilityDistribution = self.prob_classify(featureset)
            label = probabilityDistribution.max()                       # max is taking the label with highest probability
            probability = probabilityDistribution.prob(label)           # getting its probability

            for labelItem in probabilityDistribution.samples():
                probs[labelItem] = str(probabilityDistribution.prob(labelItem))
            print '%s | %s | %s | %s' % (item, label, probability, probs)

        print '\n'

