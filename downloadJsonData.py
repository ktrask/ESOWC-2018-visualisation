from datetime import date, timedelta, datetime
import time, json, sys
from pathlib import Path
from geopy.geocoders import Nominatim
import asyncio, async_timeout, aiohttp
import getopt

try:
    home = str(Path.home())
    with open(home + "/.ecmwfapirc") as fp:
        credentials = json.load(fp)
except:
    print("Could not read api credentials, put your credentials in a file .ecmwfapirc in your home directory.")
    print("You can download the credentials from https://api.ecmwf.int/v1/key/")
    sys.exit(2)

#lat = random.randrange(-90, 90)
#lon = random.randrange(-180, 180)
yesterday = datetime.utcnow() - timedelta(1)

api  = { "url": "https://api.ecmwf.int/v1/services/meteogram/requests/",
                 "token": credentials['key']}


async def downloadData(session, param,allMeteogramData, longitude, latitude, writeToFile = True):
    with async_timeout.timeout(10):
        #Getting 2-metre temperature data ...
        request =  {
                            "meteogram": "10days",
                            "param": param,
                            "location": "%f/%f" % (latitude, longitude),
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
                if writeToFile:
                    with open("data/" + outputFile, "w") as data :
                        data.write(json.dumps(jsonData, indent=4, sort_keys=True))
                allMeteogramData[param] = jsonData
            return await response.release()


async def main(loop, allMeteogramData, longitude, latitude, writeToFile = True):
    params = ["2t", "tp", "tcc", "ws", "sf"]
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [downloadData(session, param, allMeteogramData, longitude, latitude, writeToFile) for param in params]
        await asyncio.gather(*tasks)

def getCoordinates(opts):
    latitude = 0
    longitude = 0
    for opt, arg in opts:
        if opt == "-h":
            print("downloadJsonData.py --location 'Braunschweig, Germany'")
            print("downloadJsonData.py --lat 20 --lon 10")
            sys.exit(0)
        elif opt == "--location":
            #print("location", arg)
            geolocator = Nominatim(user_agent="ESOWC-Meteogram-2018")
            loc = geolocator.geocode(arg)
            latitude = loc.latitude
            longitude = loc.longitude
            print(latitude, longitude)
        elif opt == "--lat":
            latitude = float(arg)
        elif opt == "--lon":
            longitude = float(arg)
    return ( latitude, longitude )

def getData(longitude, latitude, writeToFile = True):
    allMeteogramData = {}
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop, allMeteogramData, longitude, latitude,  writeToFile))
    loop.close()
    return allMeteogramData

if __name__ == '__main__':
    latitude = 0
    longitude = 0
    startTime = time.time()
    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hd:", ["days=", "location=", "lat=","lon="])
            latitude, longitude = getCoordinates(opts)
        except getopt.GetoptError:
            print("downloadJsonData.py --location 'Braunschweig, Germany'")
            print("downloadJsonData.py --lat 20 --lon 10")
            sys.exit(2)
    else:
        location = "Braunschweig Germany"
        geolocator = Nominatim(user_agent="ESOWC-Meteogram-2018")
        loc = geolocator.geocode(location)
        latitude = loc.latitude
        longitude = loc.longitude
        #print(opts)
        latitude, longitude = getCoordinates(opts)
    midTime = time.time()
    print(latitude)
    print(longitude)
    allMeteogramData = getData(longitude, latitude)
    print(allMeteogramData)
    endTime = time.time()
    print("starting up: ", midTime-startTime)
    print("downloading: ", endTime-midTime)
