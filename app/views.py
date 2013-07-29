from flask import render_template, request
from app import app
import main
import os
import settings
from trainer import businesscategories

import json

# Input         - 
# Description   - 
# Output        - 

@app.route("/")
def index():
    data = { 
    """
        "name"		: "California Pizza Kitchen",
        "business"	: "Restaurant",
        "location"	: "123 Pizza Drive, San Francisco, US, 12345",
        "hours"		: "8:00 AM to 10:00 PM"
    """
    }

    return render_template("index.html", data = data)

# Input         - 
# Description   - 
# Output        - 

@app.route("/trainer")
def trainer():
    return render_template("trainer.html")

# Input         - 
# Description   - 
# Output        - 

@app.route("/classify_business", methods=["GET"])
def classify_business():
    businessesDirectory = settings.APP_DATA_HTML
    businessName = json.loads(request.args["business_name"]).lower() 
    for root, dirs, files in os.walk(businessesDirectory):
        for filename in files:
            originalFileName = filename = filename.lower()           
            if(filename.endswith(".txt")):
                filename = filename[:-4]
            if filename == businessName:
                business = main.parse(os.path.join(settings.APP_DATA_HTML, originalFileName))

                return json.dumps({
                    "name": business.name,
                    "type": {
                        "label": business.type.label, 
                        "probability": business.type.probability
                    },
                    "labels": business.labels
                })
    return json.dumps(None)

# Input         - 
# Description   - 
# Output        - 

@app.route("/business_categories")
def BusinessCategories():
    path = settings.APP_DATA_TRAINING
    data = businesscategories.getCategories(path)
    return json.dumps(data)

# Input         - 
# Description   - 
# Output        - 

@app.route("/save_classified_data", methods=["POST"])
def function_name():
    path = settings.APP_DATA_TRAINING
    classifiedData = json.loads(request.form["classified_data"]) 
    return  "True" if  businesscategories.saveTrainedData(classifiedData,path) else "False"
