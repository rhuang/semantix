from bs4 import BeautifulSoup
import quopri
import json
import os, errno
import settings
import re

def getBusinessName(fileName):
    INPUT_FILE = os.path.join(settings.APP_DATA_HTML, fileName)

    with open(INPUT_FILE) as inputFile:
        for line in inputFile:
            seqVal = json.loads(line)['sequence_number']

            if seqVal == 0:
                body = json.loads(line)['body']
                decodedQP = quopri.decodestring(body)
                soup = BeautifulSoup(decodedQP)
                pageTitle = soup.title
                if pageTitle is not None:
                    return pageTitle.text

    return 'No Name Found'


def createSeperateFiles(largeFileName):
    INPUT_FILE = os.path.join(settings.APP_DATA_HTML, largeFileName)
    
    with open(INPUT_FILE) as inputFile:
        for line in inputFile:
            biz_id = json.loads(line)['biz_id']

            ## a will append, w will over-write
            target = open (settings.APP_DATA_HTML + "\\" + str(biz_id) + ".txt", 'a')
            target.write(line)
            target.close()


def renameFilesInDir():
    filelist = os.listdir(settings.APP_DATA_HTML)
    
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