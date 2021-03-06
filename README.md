# ESOWC-2018-visualisation
Innovative Visualisation - Communicate Weather at the ECMWF Summer of Code 2018
http://esowc.ecmwf.int/


![Example Meteogram](https://raw.githubusercontent.com/ktrask/ESOWC-2018-visualisation/master/wettvorhersage.png)

Legend:

![Legend of Meteogram](https://raw.githubusercontent.com/ktrask/ESOWC-2018-visualisation/master/pictogram/legend%2Btext_21_09_2018.png)

## Running the server


The script file needs an API-Key from the ecmwf. It can be obtained from https://api.ecmwf.int/v1/key/
If no key is available, example data can be used.

Using example data:
```
python3 plotMeteogram.py
```

Download data via API:
```
python3 plotMeteogram.py --location 'Berlin, Germany'
```

## Prerequisites

For the CLI-Script:
```bash
pip3 install numpy
pip3 install matplotlib
pip3 install pandas
pip3 install tzwhere
pip3 install geopy
pip3 install aiohttp
pip3 install async_timeout
pip3 install altitude
```

Due to filling the altitude cache, the first run will take a while.


For the webapp:
```bash
pip3 install flask_bootstrap
pip3 install flask_wtf
```

Preparing the webapp:
```bash
#install packages:
pip3 install flask-bootstrap
pip3 install flask-wtf
pip3 install altitude
#Making symlinks:
cd webapp/app/
ln -s ../../plotMeteogram.py plotMeteogram.py
ln -s ../../downloadJsonData.py downloadJsonData.py
ln -s ../../pictogram pictogram
```

Running the webapp:
```bash
cd ..
#cd webapp
python3 run.py
```
Afterwards you can go to the browser at http://127.0.0.1:5003


## Dockerfile

Note that the Dockerfile creates an image with a development
environment. I is not for productive use.

Build the webapp-docker image:
```bash
docker build -t meteogram:latest .
```

Run the webapp-docker container:
```bash
docker run -v /path/to/apikeyfolder:/root -p 5003:5003 -it meteogram
```
Afterwards go to http://127.0.0.1:5003 to access the webapp.
