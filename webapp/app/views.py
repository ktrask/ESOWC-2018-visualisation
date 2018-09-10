from flask import render_template,flash, redirect, request, jsonify
from flask_wtf import FlaskForm
from wtforms import TextField, validators, SubmitField, DecimalField, IntegerField, RadioField
from app import app, controller
#from .models import 
from random import randint
import json
from .controller import plotMeteogramFile
from base64 import b64encode
import os

class searchForm(FlaskForm):
    search = TextField("Search",  [validators.Optional()])
    lat = DecimalField("Latitude", [validators.Optional()])
    lon = DecimalField("Longitude",[validators.Optional()])
    days = IntegerField("Length of Meteogram in Days", default=3)
    plotType = RadioField("Plottype", choices=[
         ('ensemble', "Pure Ensemble Data"),
         ('enhanced-hres', "HRES Enhanced Ensemble Data")],
         default = 'ensemble', validators=[validators.Required()])
    submit = SubmitField('Go!')

@app.route('/', methods=("GET", "POST"))
def index():
    form = searchForm()
    if form.validate_on_submit():
        return redirect('/search')
    return render_template("index.html",
                           title='VSUP - Meteogram',
                           form = form)


@app.route('/search', methods=("GET", "POST"))
def search():
    #print('latitude: ' +  request.form['latitude'])
    #print('longitude: ' + request.form['longitude'])
    #form = searchForm(csrf_enable=False)
    #print(form)
    print(request.args)
    print([key for key in request.args.keys()])
    #print('latitude: ' +  request.form['lat'])
    #print('longitude: ' + request.form['lon'])
    form = searchForm()
    if request.method == 'GET':
        print("lon", request.args['lon'])
        if request.args['search']:
            searchLocation = str(request.args['search'])
            form.search.data = searchLocation
            print(searchLocation)
        else:
            searchLocation = ""
        if request.args['lat']:
            latitude = float(request.args['lat'])
            form.lat.data = latitude
        else:
            latitude = None
        if request.args['lon']:
            longitude = float(request.args['lon'])
            form.lon.data = longitude
        else:
            longitude = None
        days = int(request.args['days'])
        form.days.data = days
        plotType = str(request.args['plotType'])
        form.plotType.data = plotType
    if form.validate_on_submit():
        #print(form.search.data)
        #print(form.days.data)
        searchLocation = form.search.data
        latitude = form.lat.data
        longitude = form.lon.data
        days = form.days.data
        plotType = form.plotType.data
        print('location: ' +  searchLocation)
    else:
        print("invalid form")
    if "latitude" in locals():
        filename = plotMeteogramFile(latitude = latitude, longitude = longitude,
                                     location = searchLocation,
                                     days = days,
                                     plotType = plotType)
        with open("/tmp/"+filename, "rb") as fp:
            fileContent = b64encode(fp.read())
        #return jsonify( filename )
        os.remove("/tmp/"+filename)
        return render_template("meteogram.html",
                form = form,
                plotType = form.plotType.data,
                image = 'data:image/png;base64,{}'.format(fileContent.decode())
                )
    return render_template("index.html",
                           title = 'VSUP - Meteogram',
                           form = form)
