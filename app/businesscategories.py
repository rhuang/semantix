import os

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