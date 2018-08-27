# ESOWC-2018-visualisation
Innovative Visualisation - Communicate Weather at the ECMWF Summer of Code 2018
http://esowc.ecmwf.int/

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
```


For the webapp:
```bash
pip3 install flask_bootstrap
pip3 install flask_wtf
```

## Dockerfile

Note that the Dockerfile creates an image with a development
environment. I is not for productive use.

Build the webapp-docker image:
```bash
docker build -t meteogram:latest .
```

Run the webapp-docker container:
```bash
docker run -v /path/to/apikeyfolder:/root -it meteogram
```
