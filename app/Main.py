import threading
import sys
import os
import json
from parsers import JsonParser
from parsers import MenuParser
from parsers import LocationsParser

WINDOWS = 'nt'

# Set default encoding to UTF to avoid conflicts with symbols.
reload(sys)
sys.setdefaultencoding('utf-8')

soups = JsonParser.parse()

#### Locations #####
def locationCallback(allSoupsAddresses):
    print 'Formatted addresses in thread: %s' % threading.current_thread().name
    
    for address in allSoupsAddresses:
        if os.name == WINDOWS:
            print(address.encode('cp1252'))            
        else:
            print address
    
def locationsThread(callback):
    callback(LocationsParser.parse(soups))

def locations():
    return json.dumps(LocationsParser.parse(soups))

#### Menu #####
def menuCallback(menuItems):
    print 'Menu items in thread: %s' % threading.current_thread().name

    for address in formattedAddresses:
        if os.name == WINDOWS:
            print(address.encode('cp1252'))            
        else:
            print address

def menuThread(callback):
	callback(MenuParser.parse(soups))

def menu():
    return json.dumps(MenuParser.parse(soups))
    
#### Threads ####
threading.Thread(target=locationsThread, name="Location Thread", args=(locationCallback,)).start()
threading.Thread(target=menuThread, name="Menu Thread", args=(menuCallback,)).start()
