from flask import render_template,flash, redirect, request
from app import app
#from config import basedir, esHost
from datetime import datetime
#from elasticsearch import Elasticsearch
import json
from netCDF4 import Dataset

nc_spread = Dataset("./app/data/mslp_spread.nc", 'r')  # Dataset is the class behavior to open the file
nc_msl = Dataset("./app/data/mslp_mean.nc")



def getNearestLatIndex(lat):
    return ((nc_msl.variables['latitude'][:] - (lat))**2).argmin()
def getNearestLonIndex(lon):
    return ((nc_msl.variables['longitude'][:] - (lon))**2).argmin()

def calcCoordinates(x,y):
    x = int(x)
    y = int(y)
    halfLengthLon = (1183-31)/2
    halfLengthLat = (592-17)/2
    if(x < 31):
        longitude = 180
    elif(x < halfLengthLon):
        longitude = (halfLengthLon - x) / halfLengthLon * 180
    elif(x > 1183):
        longitude = 180
    else:
        longitude = 360 - (x - halfLengthLon) / halfLengthLon * 180
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

def getInformationAtCoordinate(x,y):
    outputData = calcCoordinates(x,y)
    latIndex = getNearestLatIndex(outputData['latitude'])
    lonIndex = getNearestLatIndex(outputData['longitude'])
    outputData['msl'] = nc_msl['msl'][19,latIndex,lonIndex]/100
    outputData['spread'] = nc_spread['msl'][19,latIndex,lonIndex]/100
    return outputData
