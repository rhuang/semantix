import sys
from parsers import JsonParser
from parsers import ContextParser
WINDOWS = 'nt'

# Set default encoding to UTF to avoid conflicts with symbols.
reload(sys)
sys.setdefaultencoding('utf-8')

soups = JsonParser.parseData()
contextMap = ContextParser.parseSoups(soups)

#  NOTE : contextMap may have repeats of similar texts, it needs to run through string comparison taking bests

print contextMap
