from netCDF4 import Dataset
import numpy as np
import pandas as pd
import datetime
import json
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

nc_f = './forecast.nc'  # Your filename
nc_fid = Dataset(nc_f, 'r')  # Dataset is the class behavior to open the file
nc_precip = Dataset('./precip.nc', 'r')
#print(nc_fid)

def getNearestLatIndex(lat):
    return (abs(nc_fid.variables['latitude'][:] - lat)).argmin()
def getNearestLonIndex(lon):
    return (abs(nc_fid.variables['longitude'][:] - lon)).argmin()


print(getNearestLatIndex(52))#52°N
print(getNearestLonIndex(10))#10°E
lat = getNearestLatIndex(52)#52°N
lon = getNearestLonIndex(10)#10°E
nc_fid.variables['longitude'][:]

with open("2t-10days.json", "r") as fp:
    temperatureData = json.load(fp)
with open("tp-10days.json", "r") as fp:
    precipitationData = json.load(fp)


df = pd.DataFrame(data = {'T'  : [],
                          'u10': [],
                          'v10': [],
                          'lcc': [],
                          'mcc': [],
                          'hcc': [],
                          'lsp': []
                 })
for i in range(0,len(nc_fid.variables['number'])):
    dfTmp = pd.DataFrame(data = {
                          'time': nc_fid.variables['time'][:40],
                          'number': [i for _ in range(0,40)],
                          'T'  : nc_fid.variables['t2m'][:40,i,lat,lon]-273.15,
                          'u10': nc_fid.variables['u10'][:40,i,lat,lon],
                          'v10': nc_fid.variables['v10'][:40,i,lat,lon],
                          'lcc': nc_fid.variables['lcc'][:40,i,lat,lon],
                          'mcc': nc_fid.variables['mcc'][:40,i,lat,lon],
                          'hcc': nc_fid.variables['hcc'][:40,i,lat,lon],
                          'lsp': nc_precip.variables['lsp'][:40,i,lat,lon]
                 })
    df = df.append(dfTmp)
df.time = [datetime.datetime(1900, 1, 1) + datetime.timedelta(hours=time) for time in df.time]
df['v'] = np.sqrt(df['v10']**2+df['u10']**2)

def convertWindToBeaufort(v):
    if v < 0.3:
        bft = 0
    elif v < 1.6:
        bft = 1
    elif v < 3.4:
        bft = 2
    elif v < 5.5:
        bft = 3
    elif v < 8.0:
        bft = 4
    elif v < 10.8:
        bft = 5
    elif v < 13.9:
        bft = 6
    elif v < 17.2:
        bft = 7
    elif v < 20.8:
        bft = 8
    elif v < 24.5:
        bft = 9
    elif v < 28.5:
        bft = 10
    elif v < 32.7:
        bft = 11
    else:
        bft = 12
    return bft
df['bft'] = [convertWindToBeaufort(i) for i in df['v'].tolist()]

quantileData = df.groupby('time').quantile([0,0.25,0.5,0.75,1])


def plotTemperature(ax, qdata):
    startDate = datetime.datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]))
    dates = [startDate + datetime.timedelta(hours=int(i)) for i in qdata['2t']['steps']]
    ax.fill_between(x= dates, y1=np.array(qdata['2t']['min'])-273.15, y2=np.array(qdata['2t']['max'])-273.15, color="lightblue", alpha = 0.5)
    ax.fill_between(x= dates, y1=np.array(qdata['2t']['twenty_five'])-273.15 , y2=np.array(qdata['2t']['seventy_five'])-273.15, color="blue", alpha = 0.5)
    #ax.plot(x = dates, y = np.array(qdata['2t']['median']) - 273.15, color="green")
    ax.plot_date(x = dates, y = np.array(qdata['2t']['median']) - 273.15, color="black", linestyle="solid", marker=None)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+'\N{DEGREE SIGN}'+'C'))

def plotWindBft(ax, qdata):
    #plots wind beaufort scale
    bar050 = ax.bar(x=qdata['bft'][:,0.5].index,height=qdata['bft'][:,0.5],width = 0.2, color = "#2A7FFF")
    bar075 = ax.bar(x=qdata['bft'][:,0.5].index,height=(qdata['bft'][:,0.75]-qdata['bft'][:,0.5]),width = 0.2, bottom = qdata['bft'][:,0.5], color = "#AACCFF")
    bar100 = ax.bar(x=qdata['bft'][:,0.5].index,height=(qdata['bft'][:,1]-qdata['bft'][:,0.75]),width = 0.2, bottom = qdata['bft'][:,0.75], color = "#D5E5FF", alpha=0.5)
    ax.set_ylim(0,10)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+' bft'))

def imscatter(x, y, image, ax=None, zoom=1):
    #taken from https://stackoverflow.com/questions/22566284/matplotlib-how-to-plot-images-instead-of-points
    if ax is None:
        ax = plt.gca()
    try:
        image = plt.imread(image)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists

def getVSUPrainCoordinate(qdata):
    #print(qdata)
    #print(qdata[1])
    if qdata['ninety'] < 1e-4:
        return(3)
    if qdata['ten'] > 2e-3:
        return(6)
    if qdata['ten'] > 1e-3 and qdata['ninety'] < 2e-3:
        return(5)
    if qdata['ten'] > 1e-3:
        return(2)
    if qdata['ninety'] < 1e-3:
        return(4)
    if qdata['seventy_five'] < 1e-3:
        return(1)
    if qdata['twenty_five'] > 1e-3:
        return(2)
    return(0)


def plotPrecipitationVSUP(ax, qdata):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    vsupFilenames = ["Stufe1.png", "Stufe2_KaumRegen.png", "Stufe2_Regen.png", "Stufe3_KeinRegen.png", "Stufe3_leichterRegen.png", "Stufe3_MittlererRegen.png", "Stufe2_Regen.png"]
    files = [vsupFilenames[getVSUPrainCoordinate({key: qdata['tp'][key][i] for key in qdata['tp']})] for i in range(0,len(qdata['tp']['ten']))]
    image_path = './pictogram/rain/'
    #for (date, filename) in zip(qdata['lsp'][:, :].index.levels[0],files):
    for (date, filename) in zip(range(0,len(files)),files):
        imscatter(date,1, image_path+filename, ax=ax, zoom = 0.2)



plt.figure(figsize=(14,6))
#plt.xkcd()
gs = gridspec.GridSpec(3, 1, height_ratios=[1, 2, 4]) 
ax1 = plt.subplot(gs[1])
ax2 = plt.subplot(gs[0])
ax3 = plt.subplot(gs[2])
#plotPrecipitationBars(ax1, quantileData)
plotPrecipitationVSUP(ax1, precipitationData)
plotTemperature(ax3, temperatureData)
#plotWindBft(ax2, quantileData)
plt.gcf().autofmt_xdate()
plt.savefig("./output/forecast.png", dpi = 300)

#plot ensemble members:
#for ens in range(0,50):
#    plt.figure(figsize=(14,6))
#    gs = gridspec.GridSpec(3, 1, height_ratios=[4, 2, 1]) 
#    ax1 = plt.subplot(gs[1])
#    ax2 = plt.subplot(gs[0])
#    ax3 = plt.subplot(gs[2])
#    plotPrecipitationBars(ax1, quantileData)
#    plotTemperature(ax2, quantileData)
#    plotWindBft(ax3, quantileData)
#    tmp = df.loc[df['number'] == ens]
#    ax2.plot(tmp['time'], tmp['T'], color = "r")
#    ax1.plot(tmp['time'], tmp['lsp']*1e3, color = "r")    
#    ax3.plot(tmp['time'], tmp['bft'], color = "r")
#    plt.gcf().autofmt_xdate()
#    plt.savefig("./output/forecast" + str(ens).zfill(2) + ".png")
#    plt.close()
