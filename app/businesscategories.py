import os
import settings

filelist = os.listdir(settings.APP_DATA_TRAINING)

def getBusinessCatagories(dirName):
    data = {}
    directoryPath = os.path.join(settings.APP_DATA_TRAINING, dirName)
    businessCatagories = os.listdir(directoryPath)
    for bizCat in businessCatagories:
        terms = []
        catagoryPath = os.path.join(directoryPath, bizCat)
        with open(catagoryPath) as inputFile:
            for line in inputFile:
                terms.append(line)



def getCategories():
    data = {'Upper Cata':{'bizA':['word1','word2','word1','word2','word1','word2','word1','word2adsafsd','word1','word2','word1safdasfas','word2asdfasdf','word1','word2','word1','word2','word1','word2' ]},
            'Lower Cata':{'bizB':['word3','word4']}
            }
    return data

    '''        
    for f in filelist:
        if f == 'businesses':
            businessData = getBusinessCatagories(f)
            break
    '''    


''' 
def renameFilesInDir():
    
    for f in filelist:
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