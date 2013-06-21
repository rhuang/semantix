import threading
import sys
import os
import jsonParser
import locationParserTrial as locationsParser

WINDOWS = 'nt'

# Set default encoding to UTF to avoid conflicts with symbols.
reload(sys)
sys.setdefaultencoding('utf-8')

soups = jsonParser.parse()

##### LOCATIONS ###################################################################
def locationCBFunc(formattedAddresses):
    print 'Formatted Addresses in thread: %s' % threading.current_thread().name
    
    for address in formattedAddresses:
        if os.name == WINDOWS:
            print(address.encode('cp1252'))
        else:
            print address

def locationsThread(callback):
    callback(locationsParser.parseLocations(soups))

##### Hours #######################################################################
#def hoursCBFunc(formattedAddresses):
#def hoursThread(callback):
    

##### Menu ########################################################################    
#def menuCBFunc(formattedAddresses):  
#def menuThread(callback):
    

##### Threads #####################################################################
thr = threading.Thread(target=locationsThread, name="Location Thread", args=(locationCBFunc,)).start()
#thr = threading.Thread(target=hoursThread, name="Hours Thread", args=(hoursCBFunc,)).start()
#thr = threading.Thread(target=menuThread, name="Menu Thread", args=(menuCBFunc,)).start()
