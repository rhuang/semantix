#doesn't work yet
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DATA_HOME = os.path.join(APP_ROOT, 'data')
APP_DATA_HTML = os.path.join(APP_DATA_HOME, 'html')
APP_DATA_ASSETS = os.path.join(APP_DATA_HOME, 'assets')

###### HTML DATA ASSETS ######

CPK_DATA = os.path.join(APP_DATA_HTML, 'cpk.txt')  	

###### KEYWORD ASSETS ########

LOCATION_ASSETS = os.path.join(APP_DATA_ASSETS, 'locations.txt')  
MENU_ASSETS = os.path.join(APP_DATA_ASSETS, 'menu.txt')  










