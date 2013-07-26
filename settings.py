import os

SEMANTIX_ROOT =  os.path.dirname((os.path.abspath(__file__)))
APP_ROOT = os.path.join(SEMANTIX_ROOT, 'app')
APP_DATA = os.path.join(APP_ROOT, 'data')
APP_DATA_HTML = os.path.join(APP_DATA, 'html')
APP_DATA_TRAINING = os.path.join(APP_DATA, 'training')
APP_DATA_COMMON_WORDS = os.path.join(APP_DATA, 'common_words')

###### HTML DATA ASSETS ######

CPK_DATA = os.path.join(APP_DATA_HTML, 'cpk_com.txt')
