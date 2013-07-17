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
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import settings
from parsers import jsonparser as JsonParser
from parsers import contextparser as ContextParser
from naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier

WINDOWS = 'nt'
reload(sys)
sys.setdefaultencoding('utf-8') # Set default encoding to UTF to avoid conflicts with symbols.

'''
soups = JsonParser.parseData(settings.CPK_DATA)
nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, 'general'))
contextMap = ContextParser.parseSoups(soups, nbc)
'''

# NOTE: contextMap may have repeats of similar texts, it needs to run through string comparison
# taking bests.
# print contextMap

