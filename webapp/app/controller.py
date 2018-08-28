from flask import render_template,flash, redirect, request
from app import app
from datetime import datetime, timedelta
#from elasticsearch import Elasticsearch
import json
from .downloadJsonData import getData, getCoordinates
from .plotMeteogram import plotMeteogram, getTimeFrame, prop
from tzwhere import tzwhere
import numpy as np

tz = tzwhere.tzwhere()

def plotMeteogramFile(latitude = None, longitude = None, location = None, days = 3):
    print(latitude, longitude)
    latitude = float(latitude)
    longitude = float(longitude)
    if location:
        latitude, longitude, altitude, _ = getCoordinates([("--location", location)])
    elif latitude is not None and longitude is not None:
        from altitude import ElevationService
        e = ElevationService('.cache/')
        altitude = e.get_elevation(latitude, longitude)
        if altitude is None:
            altitude = -999
    else:
        latitude = 52.2646577
        longitude = 10.5236066
        altitude = 79
    allMeteogramData = getData(float(longitude), float(latitude), altitude, writeToFile = False)
    tzName = tz.tzNameAt(latitude, longitude)
    today = datetime.utcnow()
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + timedelta(days))
    fig = plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName)
    filename = str(today) + str(latitude) + str(longitude) + "forecast.png"
    tmpSize = prop.get_size()
    prop.set_size(16)
    print(tmpSize)
    fig.suptitle(location + " " + str(np.round(latitude, decimals = 5)) +\
                  "°/" + str(np.round(longitude, decimals = 5)) +\
                  "°/" + str(altitude) + "m", fontproperties=prop)
    fig.savefig("/tmp/" + filename, dpi=300)
    prop.set_size(tmpSize)
    return filename
