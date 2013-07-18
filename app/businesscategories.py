import os
import settings

def getTextFromFile(path):
    terms = []
    with open(path) as inputFile:
        for line in inputFile:
            terms.append(line.strip())
    return terms

def getCategories(path):
    data = {}
    files = os.listdir(path)
    for f in files:
        new_path = os.path.join(path, f)
        if os.path.isdir(new_path):
            data[f] = getCategories(new_path)
        elif os.path.isfile(new_path):
            data[f] = getTextFromFile(new_path)
    return data


''' 
def renameFilesInDir():
    
    for f in training_dir:
        name = getBusinessName(f).strip()
        name = name.encode('ascii', 'ignore')
        name = name.lower()
        name = re.sub('[^A-Za-z0-9 ]+', '', name)
        name = name.replace(" ", "_")

        os.rename(settings.APP_DATA_HTML + "\\" + f, settings.APP_DATA_HTML + "\\" + name + ".txt")

def fileNameFromURL(url):
    url = url.encode('ascii', 'ignore')
    url = url.lower()
    url = re.sub('http://', '', url)
    url = re.sub('www\.', '', url)

    index = re.search('/\?', url)
    if index is not None:
        url = url[:index.start()]

    if url[-1] == '/':
        url = url[:-1]

    url = re.sub('[-\./]', '_', url)
    return url

    '''

'''
data = {'Upper Cata':{'bizA':['word1','word2','word1','word2','word1','word2','word1','word2adsafsd','word1','word2','word1safdasfas','word2asdfasdf','word1','word2','word1','word2','word1','word2' ]},
            'Lower Cata':{'bizB':['word3','word4']}
            }
    return data
'''