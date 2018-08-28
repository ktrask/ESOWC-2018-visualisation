from flask import render_template,flash, redirect, request
from app import app
from datetime import datetime, timedelta
#from elasticsearch import Elasticsearch
import json
from .downloadJsonData import getData, getCoordinates
from .plotMeteogram import plotMeteogram, getTimeFrame
from tzwhere import tzwhere

tz = tzwhere.tzwhere()

def plotMeteogramFile(latitude = None, longitude = None, location = None, days = 3):
    if location:
        latitude, longitude = getCoordinates([("location", location)])
    elif not latitude and not longitude:
        latitude = 52.2646577
        longitude = 10.5236066
    allMeteogramData = getData(float(longitude), float(latitude), writeToFile = False)
    tzName = tz.tzNameAt(latitude, longitude)
    today = datetime.utcnow()
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + timedelta(days))
    fig = plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName)
    filename = str(today) + str(latitude) + str(longitude) + "forecast.png"
    fig.savefig("/tmp/" + filename, dpi=300)
    return filename
