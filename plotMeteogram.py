from netCDF4 import Dataset
import numpy as np
import pandas as pd
import datetime
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter

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

def plotPrecipitationBars(ax, qdata):
    bar050 = ax.bar(x=qdata['lsp'][:,0.5].index,height=qdata['lsp'][:,0.5]*1e3,width = 0.2, color = "#2A7FFF")
    bar075 = ax.bar(x=qdata['lsp'][:,0.5].index,height=(qdata['lsp'][:,0.75]-qdata['lsp'][:,0.5])*1e3,width = 0.2, bottom = qdata['lsp'][:,0.5]*1e3, color = "#AACCFF")
    bar100 = ax.bar(x=qdata['lsp'][:,0.5].index,height=(qdata['lsp'][:,1]-qdata['lsp'][:,0.75])*1e3,width = 0.2, bottom = qdata['lsp'][:,0.75]*1e3, color = "#D5E5FF", alpha=0.5)
    ax.set_ylim(0,2)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+' mm'))


def plotTemperature(ax, qdata):
    ax.fill_between(x= qdata['T'][:,0.75].index, y1=qdata['T'][:,0] , y2=qdata['T'][:,1], color="lightblue", alpha = 0.5)
    ax.fill_between(x= qdata['T'][:,0.75].index, y1=qdata['T'][:,0.25] , y2=qdata['T'][:,0.75], color="blue", alpha = 0.5)
    ax.plot(quantileData['T'][:,0.5], color="black")
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+'\N{DEGREE SIGN}'+'C'))

def plotWindBft(ax, qdata):
    #plots wind beaufort scale
    bar050 = ax.bar(x=qdata['bft'][:,0.5].index,height=qdata['bft'][:,0.5],width = 0.2, color = "#2A7FFF")
    bar075 = ax.bar(x=qdata['bft'][:,0.5].index,height=(qdata['bft'][:,0.75]-qdata['bft'][:,0.5]),width = 0.2, bottom = qdata['bft'][:,0.5], color = "#AACCFF")
    bar100 = ax.bar(x=qdata['bft'][:,0.5].index,height=(qdata['bft'][:,1]-qdata['bft'][:,0.75]),width = 0.2, bottom = qdata['bft'][:,0.75], color = "#D5E5FF", alpha=0.5)
    ax.set_ylim(0,10)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+' bft'))


plt.figure(figsize=(14,6))
#plt.xkcd()
gs = gridspec.GridSpec(3, 1, height_ratios=[4, 2, 1]) 
ax1 = plt.subplot(gs[1])
ax2 = plt.subplot(gs[0])
ax3 = plt.subplot(gs[2])
plotPrecipitationBars(ax1, quantileData)
plotTemperature(ax2, quantileData)
plotWindBft(ax3, quantileData)
plt.gcf().autofmt_xdate()
plt.savefig("./output/forecast.png")

#plot ensemble members:
for ens in range(0,50):
    plt.figure(figsize=(14,6))
    gs = gridspec.GridSpec(3, 1, height_ratios=[4, 2, 1]) 
    ax1 = plt.subplot(gs[1])
    ax2 = plt.subplot(gs[0])
    ax3 = plt.subplot(gs[2])
    plotPrecipitationBars(ax1, quantileData)
    plotTemperature(ax2, quantileData)
    plotWindBft(ax3, quantileData)
    tmp = df.loc[df['number'] == ens]
    ax2.plot(tmp['time'], tmp['T'], color = "r")
    ax1.plot(tmp['time'], tmp['lsp']*1e3, color = "r")    
    ax3.plot(tmp['time'], tmp['bft'], color = "r")
    plt.gcf().autofmt_xdate()
    plt.savefig("./output/forecast" + str(ens).zfill(2) + ".png")
    plt.close()
