import requests
from datetime import date, timedelta
import random
import json
import sys 
from geopy.geocoders import Nominatim
from tzwhere import tzwhere

tz = tzwhere.tzwhere()

if len(sys.argv) > 1:
    location = sys.argv[1]
else:
    location = "Braunschweig Germany"

geolocator = Nominatim()
loc = geolocator.geocode(location)
timezone = tz.tzNameAt(loc.latitude, loc.longitude)
 
with open("/home/ktrask/.ecmwfapirc") as fp:
    credentials = json.load(fp)

#lat = random.randrange(-90, 90)
#lon = random.randrange(-180, 180)
yesterday = date.today() - timedelta(1)
 
api  = { "url": "https://api.ecmwf.int/v1/services/meteogram/requests/",
                 "token": credentials['key']}
#Replace XXXX with your ECMWF token : Token can found at https://api.ecmwf.int/v1/key/

def getData(param):
    #Getting 2-metre temperature data ...
    request =  {
                        "meteogram": "10days",
                        "param": param,
                        "location": "%f/%f" % (loc.latitude, loc.longitude),
                        "date": yesterday.strftime('%Y%m%d'),# Date should be expresed as YYYYMMDD
                        "time": "0000"   # Time should bb expessed as HHHH [1200 or 0000]
                    }
    #Posting the request
    response = requests.post(api["url"], json=request, params={"token" : api["token"]})
    if response.status_code == 200:
        return(response.json())
    else:
        print(response.status_code)
        print(response.text)
        return(None)


for param in ["2t", "tp", "tcc", "ws", "sf"]:
    jsonData = getData(param)
    if jsonData:
        outputFile = param + "-10days.json"
        with open(outputFile, "w") as data :
            data.write(json.dumps(jsonData, indent=4, sort_keys=True))
