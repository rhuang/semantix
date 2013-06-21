from bs4 import BeautifulSoup
import re

def parseSingleSoupTrial(soup):
    
    removeScriptTagsPattern = re.compile(r"[{}\[\]\*]")
    if soup is not None:
        pageTitle = soup.title
        if pageTitle is not None and 'location' in str(pageTitle).lower():

            ''' what if the location is not in the page title? this algorithm will not work'''

            divTagsCollection = soup.findAll('div')
            for divTag in divTagsCollection:
                divTagTextCollection = divTag.findAll(text=True, recursive=False)
                
                finalText = ""
                for text in divTagTextCollection:        
                    if len(re.sub(r'\s+', '', text)) > 0:
                        if re.search(removeScriptTagsPattern, text) is None:
                            finalText += str(re.sub(r'\s+', ' ', text))
                
                if finalText:
                    print finalText
                    print "____________________________________"



def parseLocations(soups):
    finalAddresses = []
    for soup in soups:
        finalAddress = parseSingleSoupTrial(soup)
        if finalAddress is not None and len(finalAddress) > 0:
            finalAddresses.append(finalAddress)

    return finalAddresses