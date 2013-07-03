from bs4 import BeautifulSoup
import re

incorrectWords = set(["google","analytics","tag","ads"])

def parseSingleSoup(soup):
    
    removeScriptTagsPattern = re.compile(r"[{}\[\]\*>=]")
    finalAddresses = []
    if soup is not None:
        pageTitle = soup.title
        if pageTitle is not None and 'location' in str(pageTitle).lower():
            ''' 
            TODO: What if the location is not in the page title?
            TODO: Now this needs to call the naive bayes method to give % probablities of topic and 
                    if is subtopic of location print it.
            '''
            divTagsCollection = soup.findAll('div')
            for divTag in divTagsCollection:
                divTagTextCollection = divTag.findAll(text=True, recursive=False)
                finalText = ""
                for text in divTagTextCollection:        
                    if len(re.sub(r'\s+', '', text)) > 0: #removes whitespace, doesnt change text
                        if re.search(removeScriptTagsPattern, text) is None and not any(word in incorrectWords for word in text.lower().split()):
                            finalText += str(re.sub(r'\s+', ' ', text)) #change any white space into single space
            
                if finalText:
                    finalAddresses.append(finalText)             
    return finalAddresses     

def parse(soups):
    finalAddressesAllSoups = []
    for soup in soups:
        finalAddress = parseSingleSoup(soup)
        if finalAddress is not None and len(finalAddress) > 0:
            if finalAddressesAllSoups:
                finalAddressesAllSoups += finalAddress
            else:
                finalAddressesAllSoups = finalAddress


    return finalAddressesAllSoups
