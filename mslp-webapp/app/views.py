from flask import render_template,flash, redirect, request, jsonify
from app import app, controller
#from .models import 
from random import randint
import json


@app.route('/', methods=("GET", "POST"))
def index():
    return render_template("index.html",
                           title='MSLP')
@app.route('/getInformation', methods=("GET", "POST"))
def getInformation():
    print('longitude: ' + request.form['x'])
    print('latitude: ' +  request.form['y'])
    return jsonify( controller.getInformationAtCoordinate(request.form['x'], request.form['y']))
    #return jsonify( {'longitude': request.form['x'],
    #                 'latitude':  request.form['y'] } )
