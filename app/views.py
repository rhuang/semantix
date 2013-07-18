from flask import render_template, request
from app import app
import main
import settings
from trainer import businesscategories
import json


@app.route('/')
def index():
    data = { 
        'name'		: 'California Pizza Kitchen',
        'business'	: 'Restaurant',
        'location'	: '123 Pizza Drive, San Francisco, US, 12345',
        'hours'		: '8:00 AM to 10:00 PM'
    }
    return render_template('index.html', data = data)

@app.route('/trainer')
def trainer():
    return render_template('trainer.html')

@app.route('/business_categories')
def BusinessCategories():

    path = settings.APP_DATA_TRAINING
    data = businesscategories.getCategories(path)
    return json.dumps(data)

@app.route('/save_classified_data', methods=['POST'])
def function_name():

    path = settings.APP_DATA_TRAINING
    classifiedData = json.loads(request.form['classified_data']) 
    return  "True" if  businesscategories.saveTrainedData(classifiedData,path) else "False"
