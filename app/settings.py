import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

APP_DATA = os.path.join(APP_ROOT, 'data')
APP_DATA_HTML = os.path.join(APP_DATA, 'html')
APP_DATA_TRAINING = os.path.join(APP_DATA, 'training')

###### HTML DATA ASSETS ######

CPK_DATA = os.path.join(APP_DATA_HTML, 'cpk.txt')
NEW_DATA = os.path.join(APP_DATA_HTML, 'data.txt')
