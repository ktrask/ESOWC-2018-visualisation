from flask import render_template,flash, redirect, request
from app import app
from datetime import datetime, timedelta
#from elasticsearch import Elasticsearch
import json
from .downloadJsonData import getData, getCoordinates
from .plotMeteogram import plotMeteogram, getTimeFrame, prop
from tzwhere import tzwhere
from matplotlib.pyplot import close as pltclose
import numpy as np

tz = tzwhere.tzwhere()

def plotMeteogramFile(latitude = None, longitude = None, location = None, days = 3, plotType = "enhanced-hres"):
    print(latitude, longitude)
    print(plotType)
    if location:
        latitude, longitude, altitude, _ = getCoordinates([("--location", location)])
    elif latitude is not None and longitude is not None:
        latitude = float(latitude)
        longitude = float(longitude)
        from altitude import ElevationService
        e = ElevationService('.cache/')
        altitude = e.get_elevation(latitude, longitude)
        if altitude is None:
            altitude = -999
    else:
        latitude = 52.2646577
        longitude = 10.5236066
        altitude = 79
    if days <= 10:
        allMeteogramData = getData(float(longitude), float(latitude), altitude, writeToFile = False)
    else:
        allMeteogramData = getData(float(longitude), float(latitude), altitude, writeToFile = False, meteogram = "15days")
    tzName = tz.tzNameAt(latitude, longitude)
    today = datetime.utcnow()
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + timedelta(days))
    fig = plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName, plotType)
    filename = str(today) + str(latitude) + str(longitude) + "forecast.png"
    tmpSize = prop.get_size()
    prop.set_size(16)
    print(tmpSize)
    fig.suptitle(location + " " + str(np.round(latitude, decimals = 2)) +\
                  "°/" + str(np.round(longitude, decimals = 2)) +\
                  "°/" + str(altitude) + "m", fontproperties=prop)
    prop.set_size(tmpSize)
    if '2t' in allMeteogramData:
        #fig.text(0.1,0.03,allMeteogramData['2t']['date']+"-"+allMeteogramData['2t']['time'],fontproperties=prop)
        fig.text(0.2,0.06,"Forecast from the European Weather Centre from " + allMeteogramData['2t']['date']+" at "+allMeteogramData['2t']['time'][0:2] + ":" + allMeteogramData['2t']['time'][0:2] + " UTC",fontproperties=prop)
    if 'tp24' in allMeteogramData:
        fig.text(0.2,0.06,"Forecast from the European Weather Centre from " + allMeteogramData['tp24']['date']+" at "+allMeteogramData['tp24']['time'][0:2] + ":" + allMeteogramData['tp24']['time'][0:2] + " UTC",fontproperties=prop)
        #fig.text(0.1,0.03,allMeteogramData['tp24']['date']+"-"+allMeteogramData['tp24']['time'],fontproperties=prop)
    fig.savefig("/tmp/" + filename, dpi=300, bbox_inches = 'tight')
    pltclose(fig)
    return filename
