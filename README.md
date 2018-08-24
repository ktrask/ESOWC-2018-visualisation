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
