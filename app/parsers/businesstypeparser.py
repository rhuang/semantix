import re

# Go through list of all categories and finds the 
# category with highest total probability
def getHighestProbability(allCategories):
    uniqueCategories = []
    probabilities = []

    highestProbability = 0;
    for category in allCategories:
        if not category[0] in uniqueCategories:
            uniqueCategories.append(category[0])
            probabilities.append(category[1])
            if(highestProbability < category[1]):
                highestProbability = category[1];
        else:
            categoryIndex = uniqueCategories.index(category[0])
            probabilities[categoryIndex] += category[1]
            if(highestProbability < probabilities[categoryIndex]):
                highestProbability = probabilities[categoryIndex]

    returnIndex = probabilities.index(highestProbability)
    
    highestProbCategory = []
    highestProbCategory.append(uniqueCategories[returnIndex])
    highestProbCategory.append(highestProbability)
    
    return highestProbCategory

def parseSoups(soups,nbc):

    # Parse all soups and put all categories found in an array
    allCategories = []
    for soup in soups:
        allCategories.append(nbc.classify(soup.getText()))
    
    businessType = getHighestProbability(allCategories)
    print businessType