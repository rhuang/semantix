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
                This needs to be implemented as a strategy somehow so that parse locations filter can use it too.
                """
                # Consider all numbers as one category for location. 10 because full address is
                # about 10 tokens.
                if len(word) == 5:
                    word = "postalcode"
                elif len(word) > 2:
                    # Check if this word is an ordinal number like '1st' for location feature.
                    if word[-2:] in ordinals and word[:-2].isdigit():
                        word = 'ordinal' + str(numOrdinals)
                        numOrdinals += 1
                elif word.isdigit() and len(words) < 10:
                    word = 'number'

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
            if text not in self._commonwords:
                if text not in featuresset:
                    featuresset[text] = generateDefaultFreq()
                # Loop through all labels associated with this feature.
                for label in labels:
                    featuresset[text][label] += 1
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

        self._featureProbabilityDistribution = probabilityDistribution

    """
    Classifies an item.
    @return A tuple of best classified label with its probability.
    """
    def classify(self, input): 
        input = input.lower()
        inputFeatureSet = self._tokenizeInputToFeatures(input)
        classifiedDataTuple = namedtuple('ClassifiedData', ['label', 'probability'])

        probabilityDistribution = self._prob_classify(inputFeatureSet)

        probabilityMap = self.generalizeAndNormalize(probabilityDistribution)

        highestProbabilityLabel = ""
        probability = 0
        for key,value in probabilityMap.items():
            if value > probability:
                probability = value
                highestProbabilityLabel = key

        return classifiedDataTuple(highestProbabilityLabel, probability)

    """
    Overwrites _prob_classify of nltk so that we can force label frequencies to be empty, otherwise
    label frequencies will skew our results in favor of which label has the most trained data.
    """
    def _prob_classify(self, featureset):
        featureset = featureset.copy() 
        for fname in featureset.keys(): 
            for label in self._labels: 
                if (label, fname) in self._featureProbabilityDistribution: 
                    break 
            else: 
                #print 'Ignoring unseen feature %s' % fname 
                del featureset[fname] 

        # Start with a log probability of 0 to avoid skewing towards larger data sets
        logprob = {} 
        for label in self._labels: 
            #print "in here adding labels"
            logprob[label] = 0                 

        # Add in the log probability of features given labels. 

        for label in self._labels: 
            for (fname, fval) in featureset.items(): 
                
                if (label, fname) in self._featureProbabilityDistribution: 
                    feature_probs = self._featureProbabilityDistribution[label,fname] 
                    #print "log prob for " + str(label) + " for string " + str(fname)+  " is " + str(feature_probs.logprob(fval) )
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


    # gets art from art:artists
    def getLabel(self, label):
        if ":" in label:
            return label[:label.index(":")]
        return label

    '''
    Takes in a DictionaryProbDist which has probabilites for all categories including spefific categories like clothing:brands
    This function makes all specific categories into one. It uses the max from the list of probabilities + average of rest
    All the values are then normalized to scale to 1, thus raising each individual probability
    '''
    def generalizeAndNormalize(self, probabilityDistribution):
        probabilityListMap = {}

        # iterates through probability distribtion making a mapping like {'clothing': [0.011363636363636258, 0.011363636363636258], 'location': [0.011363636363636258]}
        # where the 2 values in array correspond to 2 specific values in clothing like clothing:brands and clothing:type as example
        for label in probabilityDistribution.samples():
            generalLabel = self.getLabel(label)
            probabilityValuesList = []
            if generalLabel in probabilityListMap:
                probabilityValuesList = probabilityListMap[generalLabel]   
            probabilityValuesList.append(probabilityDistribution.prob(label))
            probabilityListMap[generalLabel] = probabilityValuesList
        #print probabilityListMap
        
        # makes probability map where the probability for a category is the "max" in the list + the average of the rest of the values
        probabilityMap = {}
        sumOfAllValues = 0
        for key,value in probabilityListMap.items():
            probabilityValuesList = value
            maxProbability = max(probabilityValuesList)
            average = 0
            if len(probabilityValuesList) > 1:
                average = ( sum(probabilityValuesList) - maxProbability ) / (len(probabilityValuesList) - 1)
            probabilityMap[key] = maxProbability + average
            sumOfAllValues += probabilityMap[key]
        #print probabilityMap

        # now normalize these so all values make sense on a scale to 1
        for key,value in probabilityMap.items():
            probabilityMap[key] = probabilityMap[key] / sumOfAllValues
        #print probabilityMap
    
        return probabilityMap

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
            "Chicken & Shrimp",
            "New Jersey - Cherry Hill Mall",
            "CPKids Fundraisers & Activities",
            "From a legendary pizza to a global brand",
            "Seasonal Selection - Artichoke & Broccoli",
            "California Pizza Kitchen - About Catering & Events",
            "LA Food Show Grill & Bar Opens in Beverly Hills, California",
            "Pizza & The Presidency: National Survey Reveals Leading Candidates and America's Dining Preferences"
            "Margaret Magnetic North: The Landscapes of Tom Uttech Milwaukee: Milwaukee Art Museum",
            "pizzas",
            "JEANS",
            "denim jeans",
            "18601 Airport Way # 135 Santa Ana, CA 92707 949-252-6125",
            "180 El Camino Real Palo Alto, CA 94304 (650) 325-2753",
            "201 No 1 Long 507 Fu Xing (Mid) Rd Lu Wan District Shanghai, China 2000"
        }

        for item in testingSet:
            probs = {}
        
            print "-------------------------------------------------------"

            item = item.lower()
            featureset = self._tokenizeInputToFeatures(item)

            probabilityDistribution = self._prob_classify(featureset)
            probabilityMap = self.generalizeAndNormalize(probabilityDistribution)

            highestProbabilityLabel = ""
            probability = 0
            for key,value in probabilityMap.items():
                if value > probability:
                    probability = value
                    highestProbabilityLabel = key
        

            for labelItem in probabilityDistribution.samples():
                probs[labelItem] = str(probabilityDistribution.prob(labelItem))
            print '%s | %s | %s | %s' % (item, highestProbabilityLabel, probability, probabilityMap)

        print '\n'

