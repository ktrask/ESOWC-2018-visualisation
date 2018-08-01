from flask import render_template,flash, redirect, request, jsonify
from app import app, controller
#from .models import CodeComments
from random import randint
import json

def calcCoordinates(x,y):
    x = int(x)
    y = int(y)
    halfLengthLon = (1183-31)/2
    halfLengthLat = (592-17)/2
    if(x < 31):
        longitude = -180
    elif(x < halfLengthLon):
        longitude = - (halfLengthLon - x) / halfLengthLon * 180
    elif(x > 1183):
        longitude = 180
    else:
        longitude = (x - halfLengthLon) / halfLengthLon * 180
    if(y < 17):
        latitude = 90
    elif(y < halfLengthLat):
        latitude = (halfLengthLat - y) / halfLengthLat * 90
    elif(y > 592):
        latitude = -90
    else:
        latitude = -(y - halfLengthLat) / halfLengthLat * 90
    return({'longitude': longitude,
            'latitude':  latitude})

@app.route('/', methods=("GET", "POST"))
def index():
    return render_template("index.html",
                           title='MSLP')
@app.route('/getInformation', methods=("GET", "POST"))
def getInformation():
    print('longitude: ' + request.form['x'])
    print('latitude: ' +  request.form['y'])
    return jsonify( calcCoordinates(request.form['x'], request.form['y']))
    #return jsonify( {'longitude': request.form['x'],
    #                 'latitude':  request.form['y'] } )
