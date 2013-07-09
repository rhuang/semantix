from bs4 import BeautifulSoup
import re


commonlyAppearingIncorrectParses = set(["google","analytics","tag","ads"])


def parseSingleSoup(soup):
    
    removeScriptTagsPattern = re.compile(r"[{}\[\]\*>=]")
    finalAddresses = []
    if soup is not None:
        pageTitle = soup.title
        finalText = ""
        if pageTitle is not None and 'location' in str(pageTitle).lower():

            ''' TODO: what if the location is not in the page title?  '''
            ''' TODO: now this needs to call the naive bayes method to give % probablities of topic and if is subtopic of location print it'''

            divTagsCollection = soup.findAll('div')
            for divTag in divTagsCollection:
                divTagTextCollection = divTag.findAll(text=True, recursive=False)
                finalText = ""
                for text in divTagTextCollection:        
                    if len(re.sub(r'\s+', '', text)) > 0:
                        if re.search(removeScriptTagsPattern, text) is None and not any(word in commonlyAppearingIncorrectParses for word in text.lower().split()):
                            finalText += str(re.sub(r'\s+', ' ', text))
            
                if finalText:
                    finalAddresses.append(finalText)             
    return finalAddresses     

def parseLocations(soups):
    finalAddressesAllSoups = []
    for soup in soups:
        finalAddress = parseSingleSoup(soup)
        if finalAddress is not None and len(finalAddress) > 0:
            finalAddressesAllSoups.append(finalAddress)

    return finalAddressesAllSoups