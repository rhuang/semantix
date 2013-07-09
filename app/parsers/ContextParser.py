from bs4 import BeautifulSoup
import re
from naivebayesclassifier import naivebayesclassifier as nbc


#incorrectWords = set(["google","analytics","tag","ads"])
#if not any(word in incorrectWords for word in text.lower().split()):

# Input         -   soup        : A soup that 
#                   contextMap  : A map that contains all classification types as keys, with their respective values as a list of text 
# Description   -   Iterates through the single soup looking for text and calling the classifier, classifying the text into the map

def parseSingleSoup(soup, contextMap):

    textList = []
    scriptTags = re.compile(r"[{}\[\]\*>=]")
    if soup is not None:
        pageTitle = soup.title
        if pageTitle is not None:
            tags = soup.findAll()
            for tag in tags:

                tagText = tag.findAll(text=True, recursive=False)                                                # get one level of text depth
                finalText = ""
                for text in tagText:        

                    if len(re.sub(r'\s+', '', text)) > 0 and re.search(scriptTags, text) is None:                # if this actually contains text AND do not take characters with script chars in it
                            finalText += str(re.sub(r'\s+', ' ', text))            

                if finalText:
                    #category = "test " 
                    category = nbc.classify(finalText)
                    # add into hash map
                    if contextMap.get(category) is not None:
                        contextMap.get(category).append(finalText)
                    else:
                        listOfWords = []
                        listOfWords.append(finalText)
                        contextMap[category] = listOfWords



# Input         - soups     : A list of soups that Beautiful soup is capable of parsing
# Description   - 
# Output        - A map that contains all classification types as keys, with their respective values as a list of text 

def parseSoups(soups):
    contextMap = {}
    for soup in soups:
        parseSingleSoup(soup,contextMap)
    return contextMap
