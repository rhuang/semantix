'''
try:
	from mercurial import demandimport; demandimport.enable()
except ImportError:
    import sys
    sys.stderr.write("abort: couldn't find mercurial libraries in [%s]\n" %
    				' '.join(sys.path))
    sys.stderr.write("(check your install and PYTHONPATH)\n")
    sys.exit(-1)
'''

import os
from os import listdir
import sys
import collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from parsers import jsonparser as JsonParser
from parsers import contextparser as ContextParser
from parsers import businesstypeparser as BusinessTypeParser
from naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier

WINDOWS = 'nt'
reload(sys)
sys.setdefaultencoding('utf-8')     # Set default encoding to UTF to avoid conflicts with symbols.

# Parse a single business, identified by input file.
def parseBusiness(inputFile):
    soups = JsonParser.parseData(inputFile)
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, 'general'))
    contextMap = ContextParser.parseSoups(soups, nbc)
    # NOTE: contextMap may have repeats of similar texts, it needs to run through string comparison
    # taking bests.
    print contextMap

# Parse a single business file to identify its business type.
def parseBusinessType(inputFile):
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, 'businesses'))
    # Our data files are .txt files for now.
    if inputFile.endswith('.txt'):
        parsedBusinessTuple = JsonParser.parseData(inputFile,True)
        businessTuple       = collections.namedtuple('Business', ['businessName', 'businessType'])

        businessTuple.businessName = parsedBusinessTuple.businessName
        businessTuple.businessType = BusinessTypeParser.parseBusinessType(inputFile, parsedBusinessTuple.businessSoups, nbc)
        return businessTuple
        #return (businessName, BusinessTypeParser.parseBusinessType(inputFile, businessSoups, nbc))

#parseBusiness(settings.CPK_DATA)

business = parseBusinessType(os.path.join(settings.APP_DATA_HTML, 'baumstevens_com.txt'))

print business.businessName
print business.businessType.businessFile
print business.businessType.businessTypeLabel.businessLabel
print business.businessType.businessTypeLabel.businessAverageProbability