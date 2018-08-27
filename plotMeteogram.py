import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import sys, os, json
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from tzwhere import tzwhere
import pytz
import getopt
from pathlib import Path
import matplotlib.font_manager as fm

home = str(Path.home())

if os.path.exists(home + "/.fonts/BebasNeue Regular.otf"):
    prop = fm.FontProperties(fname=home+'/.fonts/BebasNeue Regular.otf')
else:
    prop = fm.FontProperties(family='DejaVu Sans')

if not os.path.exists("output/"):
    os.mkdir("output")

def getNextDottedHour(hour):
    if hour < 2:
        return 2
    if hour < 10:
        return 10
    if hour < 14:
        return 14
    if hour < 22:
        return 22
    raise ValueError

def getDottedHours(fromDate, toDate):
    newDate = fromDate + timedelta(hours=3)
    dottedDates = [newDate]
    #print(newDate)
    #print(toDate)
    while newDate < toDate:
        newDate = newDate + timedelta(hours=6)
        dottedDates.append(newDate)
    return(dottedDates[:-1])


def getNumberedHours(fromDate, toDate):
    newDate = fromDate
    numberedDates = []
    while newDate < toDate:
        if newDate.hour < 12:
            newDate = datetime.datetime(newDate.year, newDate.month, newDate.day, 12,tzinfo=toDate.tzinfo)
        else:
            newDate = datetime.datetime(newDate.year, newDate.month, newDate.day, 0,tzinfo=toDate.tzinfo) + datetime.timedelta(1)
        numberedDates.append(newDate)
    return(numberedDates[:-1])

def getWeekdayString(day):
    #print(day)
    if day == 0:
        return "Monday"
    if day == 1:
        return "Tuesday"
    if day == 2:
        return "Wednesday"
    if day == 3:
        return "Thursday"
    if day == 4:
        return "Friday"
    if day == 5:
        return "Saturday"
    if day == 6:
        return "Sunday"

def plotTemperature(ax, qdata, fromIdx, toIdx, tzName):
    startDate = datetime.datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]))
    startDate = pytz.timezone('UTC').localize(startDate)
    if tzName:
        startDate = startDate.astimezone(pytz.timezone(tzName))
    dates = [startDate + datetime.timedelta(hours=int(i)) for i in qdata['2t']['steps']]
    #convert temperatures to numpy arrays:
    temps = {}
    temps['min'] = np.array(qdata['2t']['min']) - 273.15
    temps['max'] = np.array(qdata['2t']['max']) - 273.15
    temps['median'] = np.array(qdata['2t']['median']) - 273.15
    temps['twenty_five'] = np.array(qdata['2t']['twenty_five']) - 273.15
    temps['seventy_five'] = np.array(qdata['2t']['seventy_five']) - 273.15
    temps['ten'] = np.array(qdata['2t']['ten']) - 273.15
    temps['ninety'] = np.array(qdata['2t']['ninety']) - 273.15
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['min'][fromIdx:toIdx], y2=temps['max'][fromIdx:toIdx], color="lightblue", alpha = 0.5)
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['ten'][fromIdx:toIdx], y2=temps['ninety'][fromIdx:toIdx], color="cyan", alpha = 0.5)
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['twenty_five'][fromIdx:toIdx], y2=temps['seventy_five'][fromIdx:toIdx], color="blue", alpha = 0.5)
    ax.plot_date(x = dates[fromIdx:toIdx], y = temps['median'][fromIdx:toIdx], color="black", linestyle="solid", marker=None)
    #ax.fill_between(x= dates[fromIdx:toIdx], y1=np.array(qdata['2t']['min'][fromIdx:toIdx])-273.15, y2=np.array(qdata['2t']['max'][fromIdx:toIdx])-273.15, color="lightblue", alpha = 0.5)
    #ax.fill_between(x= dates[fromIdx:toIdx], y1=np.array(qdata['2t']['twenty_five'][fromIdx:toIdx])-273.15 , y2=np.array(qdata['2t']['seventy_five'][fromIdx:toIdx])-273.15, color="blue", alpha = 0.5)
    #ax.plot_date(x = dates[fromIdx:toIdx], y = np.array(qdata['2t']['median'][fromIdx:toIdx]) - 273.15, color="black", linestyle="solid", marker=None)
    dottedHours = getDottedHours(dates[fromIdx], dates[toIdx-1])
    ymin, ymax = ax.get_ylim()
    yscale = (ymax-ymin)/7
    #print(dottedHours)
    ax.vlines(dottedHours, ymin, ymax, linestyle = ':', color = "gray")
    numberedHours = getNumberedHours(dates[fromIdx], dates[toIdx-1])
    #print(numberedHours)
    #ax.yaxis.set_major_formatter(FormatStrFormatter('%d'+'\N{DEGREE SIGN}'+'C'))
    for hour in numberedHours:
        #ax.text(hour, ymin, str(hour.hour), horizontalalignment = "center", verticalalignment = "top" )
        ax.text(hour, ymax, str(hour.hour), horizontalalignment = "center", verticalalignment = "bottom", fontproperties=prop)
        if hour.hour == 12:
            ax.text(hour, ymin-yscale/1.7, getWeekdayString(hour.weekday()), horizontalalignment = "center", verticalalignment = "top", fontproperties=prop)
    ax.axis('off')
    #ax.box(on=None)
    #ax.get_xaxis().set_visible(False)
    localMinima = np.r_[True, temps['median'][1:] < temps['median'][:-1]] & np.r_[temps['median'][:-1] < temps['median'][1:], True]
    #print(localMinima)
    #print(np.r_[temps['median'][1:] < temps['median'][:-1]])
    #print(np.r_[temps['median'][:-1] < temps['median'][1:]])
    localMaxima = np.r_[True, temps['median'][1:] > temps['median'][:-1]] & np.r_[temps['median'][:-1] > temps['median'][1:], True]
    #print(localMaxima)
    for i in range(fromIdx,toIdx):
        if localMinima[i]:
            date = dates[i]
            temp = temps['median'][i]
            #print(date)
            ax.scatter(date, temp - yscale, s=300, color = "darkcyan")
            ax.text(date, temp - yscale, str(int(np.round(temp))),
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    color = 'white', fontproperties=prop)
        if localMaxima[i]:
            date = dates[i]
            temp = temps['median'][i]
            #print(date)
            ax.scatter(date, temp + yscale, s=300, color = "orange")
            ax.text(date, temp + yscale, str(int(np.round(temp))),
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    color = "white", fontproperties=prop)

def plotWindBft(ax, qdata, fromIdx, toIdx):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    vsupFilenames = ["Stufe1.png", "Stufe2_KaumWind.png", "Stufe2_vielWind.png", "Stufe3_Windstille.png", "Stufe3_leichterWind.png", "Stufe3_starkerWind.png", "Stufe3_Sturm.png"]
    files = [vsupFilenames[getVSUPWindCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
    image_path = './pictogram/wind/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.5:
        zoomFactor = 0.5
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = zoomFactor)
    ax.axis('off')

def plotCloudVSUP(ax, qdata, fromIdx, toIdx):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    vsupFilenames = ["Stufe1.png", "Stufe2_eherSonnig.png", "Stufe2_eherBewoelkt.png", "Stufe3_klarerHimmel.png", "Stufe3_leichtBedeckt.png", "Stufe3_mittlereBewoelkung.png", "Stufe3_starkBewoelkt.png"]
    files = [vsupFilenames[getVSUPCloudCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
    image_path = './pictogram/cloud/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.5:
        zoomFactor = 0.5
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = zoomFactor)
    ax.axis('off')

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

def getVSUPCloudCoordinate(qdata):
    #print(qdata)
    #print(qdata[1])
    if qdata['ninety'] < 0.1:#m/s
        return(3)#no cloud
    if qdata['ten'] > 0.9:
        return(6)#all cloudy
    if qdata['ten'] > 0.5 and qdata['ninety'] < 0.95:
        return(5)#lot of clouds
    #if qdata['ten'] > 10:
    #    return(2)
    if qdata['ninety'] < 0.5:
        return(4)#light clouds
    if qdata['seventy_five'] < 0.7:
        return(1)
    if qdata['twenty_five'] > 0.3:
        return(2)
    return(0)

def getVSUPWindCoordinate(qdata):
    #print(qdata)
    #print(qdata[1])
    if qdata['ninety'] < 3:#m/s
        return(3)#no wind
    if qdata['ten'] > 17.2:
        return(6)#storm
    if qdata['ten'] > 10 and qdata['ninety'] < 17.2:
        return(5)#strong wind
    #if qdata['ten'] > 10:
    #    return(2)
    if qdata['ninety'] < 10:
        return(4)#light wind
    if qdata['seventy_five'] < 10:
        return(1)
    if qdata['twenty_five'] > 10:
        return(2)
    return(0)

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
    vsupFilenames = ["Stufe1.png", "Stufe2_KaumRegen.png", "Stufe2_Regen.png", "Stufe3_KeinRegen.png", "Stufe3_leichterRegen.png", "Stufe3_MittlererRegen.png", "Stufe3_Starkregen.png"]
    files = [vsupFilenames[getVSUPrainCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
    image_path = './pictogram/rain/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.5:
        zoomFactor = 0.5
    print(zoomFactor)
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = zoomFactor)
    ax.axis('off')


def getTimeFrame(allMeteogramData,fromDate, toDate):
    #print(allMeteogramData)
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
    #print(toIndex)
    #print(fromIndex)
    return (fromIndex, toIndex)

def plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName):
    fig = plt.figure(figsize=(14,6))
    #plt.xkcd()
    gs = gridspec.GridSpec(4, 1, height_ratios=[1, 1, 4, 1])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    ax4 = fig.add_subplot(gs[3])
    #plotPrecipitationBars(ax1, quantileData)
    plotCloudVSUP(ax1, allMeteogramData['tcc']['tcc'], fromIndex, toIndex)
    plotPrecipitationVSUP(ax2, allMeteogramData['tp']['tp'], fromIndex, toIndex)
    plotTemperature(ax3, allMeteogramData['2t'], fromIndex, toIndex, tzName)
    plotWindBft(ax4, allMeteogramData['ws']['ws'], fromIndex, toIndex)
    return fig


if __name__ == '__main__':
    #today = datetime.date.today()
    today = datetime.datetime.utcnow()
    days = 3
    if len(sys.argv) > 1 :
        from downloadJsonData import getData, getCoordinates
        latitude, longitude = getCoordinates(sys.argv[1:])
        allMeteogramData = getData(float(longitude), float(latitude), writeToFile = False)
        try:
            opts, args = getopt.getopt(sys.argv, "hd:", ["days=", "lat=", "lon=", "location="])
        except getopt.GetoptError:
            print("downloadJsonData.py --location 'Braunschweig, Germany'")
            print("downloadJsonData.py --lat 20 --lon 10")
            sys.exit(2)
        #print(opts)
        for opt, arg in opts:
            if opt == "-h":
                print("downloadJsonData.py --location 'Braunschweig, Germany'")
                print("downloadJsonData.py --lat 20 --lon 10")
                sys.exit(0)
            elif opt == "--days" or opt == "-d":
                days = int(arg)
    else:
        latitude = 52.2646577
        longitude = 10.5236066
        allMeteogramData = {}
        with open("data/2t-10days.json", "r") as fp:
            allMeteogramData['2t'] = json.load(fp)
        with open("data/tp-10days.json", "r") as fp:
            allMeteogramData['tp'] = json.load(fp)
        with open("data/ws-10days.json", "r") as fp:
            allMeteogramData['ws'] = json.load(fp)
        with open("data/tcc-10days.json", "r") as fp:
            allMeteogramData['tcc'] = json.load(fp)
    tz = tzwhere.tzwhere()
    tzName = tz.tzNameAt(latitude, longitude)
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + datetime.timedelta(days))
    fig = plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName)
    #fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + datetime.timedelta(10))
    #plt.gcf().autofmt_xdate()
    fig.savefig("./output/forecast.png", dpi = 300)

