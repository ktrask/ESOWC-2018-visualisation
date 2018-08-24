import requests
from datetime import date, timedelta
import time
import random
import json
import sys 
from pathlib import Path
from geopy.geocoders import Nominatim
from tzwhere import tzwhere
import asyncio
import aiohttp
import async_timeout


home = str(Path.home())
with open(home + "/.ecmwfapirc") as fp:
    credentials = json.load(fp)

#lat = random.randrange(-90, 90)
#lon = random.randrange(-180, 180)
yesterday = date.today() - timedelta(1)

api  = { "url": "https://api.ecmwf.int/v1/services/meteogram/requests/",
                 "token": credentials['key']}
#Replace XXXX with your ECMWF token : Token can found at https://api.ecmwf.int/v1/key/

allMeteogramData = {}

async def getData(session, param):
    with async_timeout.timeout(10):
        #Getting 2-metre temperature data ...
        request =  {
                            "meteogram": "10days",
                            "param": param,
                            "location": "%f/%f" % (loc.latitude, loc.longitude),
                            "date": yesterday.strftime('%Y%m%d'),# Date should be expresed as YYYYMMDD
                            "time": "0000"   # Time should bb expessed as HHHH [1200 or 0000]
                        }
        #Posting the request
        async with session.post(api["url"], json=request, params={'token':api['token']}) as response:
            jsonData = await response.text()
            #print(jsonData)
            jsonData = json.loads(jsonData)
            if jsonData:
                outputFile = param + "-10days.json"
                with open(outputFile, "w") as data :
                    data.write(json.dumps(jsonData, indent=4, sort_keys=True))
                allMeteogramData[param] = jsonData
            return await response.release()


async def main(loop):
    params = ["2t", "tp", "tcc", "ws", "sf"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [getData(session, param) for param in params]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    startTime = time.time()
    tz = tzwhere.tzwhere()
    if len(sys.argv) > 1:
        location = sys.argv[1]
    else:
        location = "Braunschweig Germany"
    geolocator = Nominatim()
    loc = geolocator.geocode(location)
    timezone = tz.tzNameAt(loc.latitude, loc.longitude)
    midTime = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    #print(allMeteogramData)
    endTime = time.time()
    #print("starting up: ", midTime-startTime)
    #print("downloading: ", endTime-midTime)
