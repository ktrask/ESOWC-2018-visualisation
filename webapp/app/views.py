from flask import render_template,flash, redirect, request, jsonify
from flask_wtf import FlaskForm
from wtforms import TextField, validators, SubmitField, DecimalField, IntegerField
from app import app, controller
#from .models import 
from random import randint
import json
from .controller import plotMeteogramFile
from base64 import b64encode
import os

class searchForm(FlaskForm):
    search = TextField("Search")
    #lat = DecimalField("Latitude")
    #lon = DecimalField("Longitude")
    days = IntegerField("Length of Meteogram in Days", default=3)
    submit = SubmitField('Go!')

@app.route('/', methods=("GET", "POST"))
def index():
    form = searchForm(csrf_enable=False)
    if form.validate_on_submit():
        return redirect('/search')
    return render_template("index.html",
                           title='VSUP - Meteogram',
                           form = form)

@app.route('/getPlot', methods=("GET", "POST"))
def getInformation():
    print('latitude: ' +  request.form['latitude'])
    print('longitude: ' + request.form['longitude'])
    print('location: ' +  request.form['location'])
    filename = plotMeteogramFile(request.form['latitude'], request.form['longitude'], request.form['location'])
    return jsonify( filename )

@app.route('/search', methods=("GET", "POST"))
def search():
    #print('latitude: ' +  request.form['latitude'])
    #print('longitude: ' + request.form['longitude'])
    form = searchForm(csrf_enable=False)
    if form.validate_on_submit():
        #print(form.search.data)
        #print(form.days.data)
        searchLocation = form.search.data
        print('location: ' +  searchLocation)
        filename = plotMeteogramFile(latitude = None, longitude = None,
                                     location = searchLocation,
                                     days = form.days.data)
        with open("/tmp/"+filename, "rb") as fp:
            fileContent = b64encode(fp.read())
        #return jsonify( filename )
        os.remove("/tmp/"+filename)
        return render_template("meteogram.html",
                form = form,
                image = 'data:image/png;base64,{}'.format(fileContent.decode())
                )
    else:
        print("invalid form")
    return render_template("index.html",
                           title = 'VSUP - Meteogram',
                           form = form)
