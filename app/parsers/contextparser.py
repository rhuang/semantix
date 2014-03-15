import re
import time

MAX_CONTEXT_PARSING_TIME = 30 # seconds

# The most common script tags
scriptTags = re.compile(r"[{}\[\]\*>=]")

# Input         -   soup        : A soup that 
#                   contextMap  : 
# Description   -   Iterates through the single soup looking for text and calling the classifier, classifying the text into the map

def parseSingleSoup(soup, contextMap, nbc):
    textList = []
    # A map that contains all classification types as keys, with their respective values as a list of text 
    if soup is not None:
        tags = soup.findAll()

        for tag in tags:
            tagText = tag.findAll(text=True, recursive=False)                                                # get one level of text depth
            finalText = ''
            for text in tagText:        
                text = re.sub('[.!;+_|]', '', text.strip())
                if len(re.sub(r'\s+', '', text)) > 0 and re.search(scriptTags, text) is None:                # if this actually contains text AND do not take characters with script chars in it
                        #print "text  is a" + re.sub(r'\s+', '', text.strip()) + "b"
                        #print "length is " + str(len(re.sub(r'\s+', '', text)))
                        finalText += str(re.sub(r'\s+',' ', text))            

            if finalText:
                
                # Clean up the string.
                finalText = ' '.join(finalText.split())

                # Classify the string.
                data = nbc.classify(finalText)

                # Push the classified text into the context Map
                if data in contextMap:
                    contextMap[data].append(finalText)
                else:
                    contextMap[data] = [finalText]

# Input         - soups     : A list of soups that Beautiful soup is capable of parsing
#               - nbc       : A trained naive bayes classifier
# Description   - 
# Output        - A map that contains all classification types as keys, with their respective values as a list of text 

def parseSoups(soups, nbc):
    
    contextMap = {}
    start_time = time.time()

    for soup in soups:

        # stop parsing at MAX_JSON_PARSING_TIME
        if (time.time() - start_time) > MAX_CONTEXT_PARSING_TIME:
            print "Passed context parser timer, finishing up"
            break

        parseSingleSoup(soup, contextMap, nbc)        

    print "Classification took " + str((time.time() - start_time))  + " seconds"
    return contextMap
