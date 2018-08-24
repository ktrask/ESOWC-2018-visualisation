import numpy as np
import pandas as pd
import datetime
import sys
import json
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox



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
#df['bft'] = [convertWindToBeaufort(i) for i in df['v'].tolist()]

#quantileData = df.groupby('time').quantile([0,0.25,0.5,0.75,1])


def plotTemperature(ax, qdata, fromIdx, toIdx):
    startDate = datetime.datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]))
    dates = [startDate + datetime.timedelta(hours=int(i)) for i in qdata['2t']['steps']]
    ax.fill_between(x= dates[fromIdx:toIdx], y1=np.array(qdata['2t']['min'][fromIdx:toIdx])-273.15, y2=np.array(qdata['2t']['max'][fromIdx:toIdx])-273.15, color="lightblue", alpha = 0.5)
    ax.fill_between(x= dates[fromIdx:toIdx], y1=np.array(qdata['2t']['twenty_five'][fromIdx:toIdx])-273.15 , y2=np.array(qdata['2t']['seventy_five'][fromIdx:toIdx])-273.15, color="blue", alpha = 0.5)
    #ax.plot(x = dates, y = np.array(qdata['2t']['median']) - 273.15, color="green")
    ax.plot_date(x = dates[fromIdx:toIdx], y = np.array(qdata['2t']['median'][fromIdx:toIdx]) - 273.15, color="black", linestyle="solid", marker=None)
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


def plotPrecipitationVSUP(ax, qdata, fromIdx, toIdx):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    vsupFilenames = ["Stufe1.png", "Stufe2_KaumRegen.png", "Stufe2_Regen.png", "Stufe3_KeinRegen.png", "Stufe3_leichterRegen.png", "Stufe3_MittlererRegen.png", "Stufe2_Regen.png"]
    files = [vsupFilenames[getVSUPrainCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
    image_path = './pictogram/rain/'
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = 0.2)


def getTimeFrame(allMeteogramData,fromDate, toDate):
    qdata = allMeteogramData['2t']
    startDate = datetime.datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]))
    dates = [startDate + datetime.timedelta(hours=int(i)) for i in qdata['2t']['steps']]
    fromIndex = 0
    if fromDate:
        for date in dates:
            if date < fromDate:
                fromIndex += 1
            else:
                break
    toIndex = len(allMeteogramData['2t']['2t']['steps'])
    if toDate:
        for date in dates[::-1]:
            if date < toDate:
                break
            else:
                toIndex -= 1
    print(toIndex)
    print(fromIndex)
    return (fromIndex, toIndex)

if __name__ == '__main__':
    #today = datetime.date.today()
    today = datetime.datetime.today()
    if len(sys.argv) > 1 :
        from downloadJsonData import getData, getCoordinates
        latitude, longitude = getCoordinates(sys.argv[1:])
        allMeteogramData = getData(float(longitude), float(latitude), writeToFile = False)
    else:
        allMeteogramData = {}
        with open("data/2t-10days.json", "r") as fp:
            allMeteogramData['2t'] = json.load(fp)
        with open("data/tp-10days.json", "r") as fp:
            allMeteogramData['tp'] = json.load(fp)
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + datetime.timedelta(3))
    plt.figure(figsize=(14,6))
    #plt.xkcd()
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 2, 4])
    ax1 = plt.subplot(gs[1])
    ax2 = plt.subplot(gs[0])
    ax3 = plt.subplot(gs[2])
    #plotPrecipitationBars(ax1, quantileData)
    plotPrecipitationVSUP(ax1, allMeteogramData['tp']['tp'], fromIndex, toIndex)
    plotTemperature(ax3, allMeteogramData['2t'], fromIndex, toIndex)
    #plotWindBft(ax2, quantileData)
    plt.gcf().autofmt_xdate()
    plt.savefig("./output/forecast.png", dpi = 300)

