import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import sys, os, json
import matplotlib
matplotlib.use('Agg')#use Agg because default is tkinter and its not threadsafe
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import offsetbox
from tzwhere import tzwhere
import pytz
import getopt
from pathlib import Path
import matplotlib.font_manager as fm

home = str(Path.home())

if os.path.exists(home + "/.fonts/BebasNeue Regular.otf"):
    prop = fm.FontProperties(fname=home+'/.fonts/BebasNeue Regular.otf')
    prop.set_size(12)
else:
    prop = fm.FontProperties(family='DejaVu Sans')


if not os.path.exists("output/"):
    os.mkdir("output")

#print(home)

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
            newDate = datetime(newDate.year, newDate.month, newDate.day, 12,tzinfo=toDate.tzinfo)
        else:
            newDate = datetime(newDate.year, newDate.month, newDate.day, 0,tzinfo=toDate.tzinfo) + timedelta(1)
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

def plotTemperature(ax, qdata, fromIdx, toIdx, tzName, plotType):
    startDate = datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]))
    startDate = pytz.timezone('UTC').localize(startDate)
    if tzName:
        startDate = startDate.astimezone(pytz.timezone(tzName))
    dates = [startDate + timedelta(hours=int(i)) for i in qdata['2t']['steps']]
    #convert temperatures to numpy arrays:
    temps = {}
    temps['min'] = np.array(qdata['2t']['min']) - 273.15
    temps['max'] = np.array(qdata['2t']['max']) - 273.15
    temps['median'] = np.array(qdata['2t']['median']) - 273.15
    temps['twenty_five'] = np.array(qdata['2t']['twenty_five']) - 273.15
    temps['seventy_five'] = np.array(qdata['2t']['seventy_five']) - 273.15
    temps['ten'] = np.array(qdata['2t']['ten']) - 273.15
    temps['ninety'] = np.array(qdata['2t']['ninety']) - 273.15
    if plotType == "enhanced_hres":
        temps['hres'] = np.array(qdata['2t']['hres']) - 273.15
    #eighty_spread = temps['ninety'] - temps['ten']
    #alphaChannel = 2 / eighty_spread
    #alphaChannel[alphaChannel > 1] = 1
    #matplotlib does not support alpha as array
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['min'][fromIdx:toIdx], y2=temps['max'][fromIdx:toIdx], color="#85cbcfff", alpha = 0.5)
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['ten'][fromIdx:toIdx], y2=temps['ninety'][fromIdx:toIdx], color="#348292ff", alpha = 0.5)
    ax.fill_between(x= dates[fromIdx:toIdx], y1= temps['twenty_five'][fromIdx:toIdx], y2=temps['seventy_five'][fromIdx:toIdx], color="#004e5eff", alpha = 0.5)
    if plotType == "ensemble":
        ax.plot_date(x = dates[fromIdx:toIdx], y = temps['median'][fromIdx:toIdx], color="black", linestyle="solid", marker=None)
    elif plotType == "enhanced-hres":
        ax.plot_date(x = dates[fromIdx:toIdx], y = temps['hres'][fromIdx:toIdx], color="black", linestyle="solid", marker=None)
    dottedHours = getDottedHours(dates[fromIdx], dates[toIdx-1])
    ymin, ymax = ax.get_ylim()
    yscale = ymax-ymin
    #if the yscale is too small, small temperature changes would seem to be large.
    if yscale < 4:
        print(yscale)
        tmp = (4 - yscale) / 4
        print(tmp)
        ymin -= tmp
        ymax += tmp
        yscale = 4
        ax.set_ylim(ymin-2*tmp,ymax+2*tmp)
    #print(dottedHours)
    yscale = yscale / 7
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
    if plotType == "ensemble":
        localMinima = np.r_[True, temps['median'][1:] < temps['median'][:-1]] & np.r_[temps['median'][:-1] < temps['median'][1:], True]
        localMaxima = np.r_[True, temps['median'][1:] > temps['median'][:-1]] & np.r_[temps['median'][:-1] > temps['median'][1:], True]
    elif plotType == "enhanced-hres":
        localMinima = np.r_[True, temps['hres'][1:] < temps['hres'][:-1]] & np.r_[temps['hres'][:-1] < temps['hres'][1:], True]
        localMaxima = np.r_[True, temps['hres'][1:] > temps['hres'][:-1]] & np.r_[temps['hres'][:-1] > temps['hres'][1:], True]
        yscale /= 1.6
    #print(localMaxima)
    for i in range(fromIdx,toIdx):
        if localMinima[i]:
            date = dates[i]
            if plotType == "ensemble":
                temp = temps['median'][i]
            elif plotType == "enhanced-hres":
                temp = temps['hres'][i]
            #print(date)
            ax.scatter(date, temp - yscale, s=300, color = "darkcyan")
            ax.text(date, temp - yscale, str(int(np.round(temp))),
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    color = 'white', fontproperties=prop)
        if localMaxima[i]:
            date = dates[i]
            if plotType == "ensemble":
                temp = temps['median'][i]
            elif plotType == "enhanced-hres":
                temp = temps['hres'][i]
            #print(date)
            ax.scatter(date, temp + yscale, s=300, color = "orange")
            ax.text(date, temp + yscale, str(int(np.round(temp))),
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    color = "white", fontproperties=prop)

def plotWindBft(ax, qdata, fromIdx, toIdx, plotType):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    if plotType == "enhanced-hres":
        #vsupFilenames = ["Stufe1_Windstille.png", "Stufe2_Windstille.png", "Stufe3_Windstille.png", "Stufe1_leichterWind.png", "Stufe2_leichterWind.png", "Stufe3_leichterWind.png", "Stufe1_starkerWind.png", "Stufe2_starkerWind.png", "Stufe3_starkerWind.png", "Stufe1_Sturm.png", "Stufe2_Sturm.png", "Stufe3_Sturm.png"]
        vsupFilenames = ["Stufe1_Windstille.png", "Stufe2_Windstille.png", "Stufe3_Windstille.png", "Stufe4_Windstille.png", "Stufe1_leichterWind.png", "Stufe2_leichterWind.png", "Stufe3_leichterWind.png", "Stufe4_leichterWind.png", "Stufe1_starkerWind.png", "Stufe2_starkerWind.png", "Stufe3_starkerWind.png", "Stufe4_starkerWind.png", "Stufe1_Sturm.png", "Stufe2_Sturm.png", "Stufe3_Sturm.png", "Stufe4_Sturm.png"]
        files = [vsupFilenames[getHresWindCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/wind/enhanced_hres/'
    else:
        vsupFilenames = ["wind_step1_variant.svg.png", "Stufe2_kaumWind.png", "Stufe2_vielWind.png", "Stufe3_Windstille.png", "Stufe3_leichterWind.png", "Stufe3_starkerWind.png", "Stufe3_Sturm.png"]
        files = [vsupFilenames[getVSUPWindCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/wind/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.45:
        zoomFactor = 0.45
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = zoomFactor)
    ax.axis('off')

def plotCloudVSUP(ax, qdata, fromIdx, toIdx, plotType):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    if plotType == "enhanced-hres":
        #vsupFilenames = ["Stufe1_klarerHimmel.png", "Stufe2_klarerHimmel.png", "Stufe3_klarerHimmel.png", "Stufe1_leichtBedeckt.png", "Stufe2_leichtBedeckt.png", "Stufe3_leichtBedeckt.png", "Stufe1_mittlereBewoelkung.png", "Stufe2_mittlereBewoelkung.png", "Stufe3_mittlereBewoelkung.png", "Stufe1_starkBewoelkt.png", "Stufe2_starkBewoelkt.png", "Stufe3_starkBewoelkt.png"]
        vsupFilenames = ["Stufe1_klarerHimmel.png", "Stufe2_klarerHimmel.png", "Stufe3_klarerHimmel.png", "Stufe4_klarerHimmel.png", "Stufe1_leichtBedeckt.png", "Stufe2_leichtBedeckt.png", "Stufe3_leichtBedeckt.png", "Stufe4_leichtBedeckt.png", "Stufe1_mittlereBewoelkung.png", "Stufe2_mittlereBewoelkung.png", "Stufe3_mittlereBewoelkung.png", "Stufe4_mittlereBewoelkung.png", "Stufe1_starkBewoelkt.png", "Stufe2_starkBewoelkt.png", "Stufe3_starkBewoelkt.png", "Stufe4_starkBewoelkt.png"]
        files = [vsupFilenames[getHresCloudCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/cloud/enhanced_hres/'
    else:
        vsupFilenames = ["cloud_step1_variant.svg.png", "Stufe2_eherSonnig.png", "Stufe2_eherBewoelkt.png", "Stufe3_klarerHimmel.png", "Stufe3_leichtBedeckt.png", "Stufe3_mittlereBewoelkung.png", "Stufe3_starkBewoelkt.png"]
        files = [vsupFilenames[getVSUPCloudCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/cloud/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.45:
        zoomFactor = 0.45
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

def getHresCloudCoordinate(qdata):
    if qdata['hres'] < 0.1:#no cloud 0-3
        if(qdata['ninety'] < 0.1):
            return 3
        elif(qdata['median'] < 0.1):
            return 2
        elif qdata['twenty_five'] < 0.1:
            return 1
        else:
            return 0
    if qdata['hres'] < 0.5:#light clouds 4-7
        if(qdata['ninety'] < 0.5):
            return 7
        elif(qdata['median'] < 0.5):
            return 6
        elif(qdata['twenty_five'] < 0.5):
            return 5
        else:
            return 4
    if qdata['hres'] > 0.9:#strong clouds 12-15
        if(qdata['ten'] > 0.9):
            return 15
        elif(qdata['median'] > 0.9):
            return 14
        elif(qdata['twenty_five'] > 0.9):
            return 13
        else:
            return 12
    else: #medium clouds 8-11
        if(qdata['ten'] > 0.5):
            return 11
        elif(qdata['median'] > 0.5):
            return 10
        elif(qdata['twenty_five'] > 0.5):
            return 9
        else:
            return 8

def getVSUPCloudCoordinate(qdata):
    #print(qdata)
    #print(qdata[1])
    if qdata['ninety'] < 0.1:#m/s
        return(3)#no cloud
    if qdata['ten'] > 0.9:
        return(6)#all cloudy
    if qdata['ten'] > 0.5:
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

def getHresWindCoordinate(qdata):
    if qdata['hres'] < 3:#no wind 0-3
        if(qdata['ninety'] < 3):
            return 3
        elif(qdata['median'] < 3):
            return 2
        elif(qdata['twenty_five'] < 3):
            return 1
        else:
            return 0
    if qdata['hres'] < 10:#light wind 4-7
        if(qdata['ninety'] < 10):
            return 7
        elif(qdata['median'] < 10):
            return 6
        elif(qdata['twenty_five'] < 10):
            return 5
        else:
            return 4
    if qdata['hres'] > 17.2:#strong wind 12-15
        if(qdata['ten'] > 17.2):
            return 15
        elif(qdata['median'] > 17.2):
            return 14
        elif(qdata['twenty_five'] > 17.2):
            return 13
        else:
            return 12
    else: #medium wind 8-11
        if(qdata['ten'] > 10):
            return 11
        elif(qdata['median'] > 10):
            return 10
        elif(qdata['twenty_five'] > 10):
            return 9
        else:
            return 8

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

def getHresrainCoordinate(qdata):
    #print(qdata)
    #print(qdata[1])
    if qdata['hres'] < 1e-4:#no rain 0-3
        if(qdata['ninety'] < 1e-4):
            return 3
        elif(qdata['median'] < 1e-4):
            return 2
        elif(qdata['twenty_five'] < 1e-4):
            return 1
        else:
            return 0
    if qdata['hres'] < 1e-3:#light rain 4-7
        if(qdata['ninety'] < 1e-3):
            return 7
        elif(qdata['median'] < 1e-3):
            return 6
        elif(qdata['twenty_five'] < 1e-3):
            return 5
        else:
            return 4
    if qdata['hres'] > 2e-3:#strong rain 12-15
        if(qdata['ten'] > 2e-3):
            return 15
        elif(qdata['median'] > 2e-3):
            return 14
        elif(qdata['twenty_five'] > 2e-3):
            return 13
        else:
            return 12
    else: #medium rain 8-11
        if(qdata['ten'] > 1e-3):
            return 11
        elif(qdata['median'] > 1e-3):
            return 10
        elif(qdata['twenty_five'] > 1e-3):
            return 9
        else:
            return 8
        pass

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
    if qdata['seventy_five'] < 1.5e-3:
        return(1)
    if qdata['median'] > 1e-3:
        return(2)
    return(0)

def plotPrecipitationVSUP(ax, qdata, fromIdx, toIdx, plotType):
    #vsupFilenames = ["rain_fuzzy.png", "rain_fuzzynotraining.png", "rain_fuzzyraining.png", "rain_norain.png", "rain_lightrain.png", "rain_rain.png", "rain_strongrain.png"]
    if plotType == "enhanced-hres":
        #hresFilenames = ["Stufe1_KeinRegen.png", "Stufe2_KeinRegen.png", "Stufe3_KeinRegen.png", "Stufe1_leichterRegen.png", "Stufe2_leichterRegen.png", "Stufe3_leichterRegen.png", "Stufe1_MittlererRegen.png", "Stufe2_MittlererRegen.png", "Stufe3_MittlererRegen.png", "Stufe1_Starkregen.png", "Stufe2_Starkregen.png",  "Stufe3_Starkregen.png"]
        hresFilenames = ["Stufe1_KeinRegen.png", "Stufe2_KeinRegen.png", "Stufe3_KeinRegen.png", "Stufe4_KeinRegen.png", "Stufe1_leichterRegen.png", "Stufe2_leichterRegen.png", "Stufe3_leichterRegen.png", "Stufe4_leichterRegen.png", "Stufe1_MittlererRegen.png", "Stufe2_MittlererRegen.png", "Stufe3_MittlererRegen.png", "Stufe4_MittlererRegen.png", "Stufe1_Starkregen.png", "Stufe2_Starkregen.png", "Stufe3_Starkregen.png", "Stufe4_Starkregen.png"]
        files = [hresFilenames[getHresrainCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/rain/enhanced_hres/'
    else:
        vsupFilenames = ["Rain_step1_variant.svg.png", "Stufe2_KaumRegen.png", "Stufe2_Regen.png", "Stufe3_KeinRegen.png", "Stufe3_leichterRegen.png", "Stufe3_MittlererRegen.png", "Stufe3_Starkregen.png"]
        files = [vsupFilenames[getVSUPrainCoordinate({key: qdata[key][i] for key in qdata})] for i in range(fromIdx,toIdx)]
        image_path = './pictogram/rain/'
    zoomFactor = 7.72 / (toIdx - fromIdx)
    if zoomFactor > 0.45:
        zoomFactor = 0.45
    print(zoomFactor)
    for (idx, filename) in zip(range(0,len(files)),files):
        imscatter(idx,1, image_path+filename, ax=ax, zoom = zoomFactor)
    ax.axis('off')


def getTimeFrame(allMeteogramData,fromDate, toDate):
    #print(allMeteogramData)
    if '2t' in allMeteogramData:
        qdata = allMeteogramData['2t']
        startDate = datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]), int(qdata['time'][0:2]))
        dates = [startDate + timedelta(hours=int(i)) for i in qdata['2t']['steps']]
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
    elif 'tp24' in allMeteogramData:
        qdata = allMeteogramData['tp24']
        startDate = datetime(int(qdata['date'][0:4]),int(qdata['date'][4:6]),int(qdata['date'][6:8]), int(qdata['time'][0:2]))
        dates = [startDate + timedelta(int(i)) for i in range(1,16)]
        fromIndex = 0
        if fromDate:
            for date in dates:
                if date < fromDate:
                    fromIndex += 1
                else:
                    break
        toIndex = 15
        if toDate:
            for date in dates[::-1]:
                if date < toDate:
                    break
                else:
                    toIndex -= 1
    #print(toIndex)
    #print(fromIndex)
    return (fromIndex, toIndex)

def plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName, plotType):
    fig = plt.figure(figsize=(14,6))
    gs = gridspec.GridSpec(4, 1, height_ratios=[1, 1, 4, 1])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    ax4 = fig.add_subplot(gs[3])
    if 'tp' in allMeteogramData:#10days 6hourly meteogram
        plotCloudVSUP(ax1, allMeteogramData['tcc']['tcc'], fromIndex, toIndex, plotType)
        plotPrecipitationVSUP(ax2, allMeteogramData['tp']['tp'], fromIndex, toIndex, plotType)
        plotTemperature(ax3, allMeteogramData['2t'], fromIndex, toIndex, tzName, plotType)
        plotWindBft(ax4, allMeteogramData['ws']['ws'], fromIndex, toIndex, plotType)
    elif 'tp24' in allMeteogramData:#15days daily meteogram
        plotCloudVSUP(ax1, allMeteogramData['tcc24']['tcc24'], fromIndex, toIndex, plotType)
        plotPrecipitationVSUP(ax2, allMeteogramData['tp24']['tp24'], fromIndex, toIndex, plotType)
        dictNew = {'time':allMeteogramData['mn2t24']['time'],
           'date': allMeteogramData['mx2t24']['date'],
           '2t': {}}
        for key in ['max','median','min','ninety','seventy_five','ten','twenty_five']:
            tmpList = []
            for mn, mx in zip(allMeteogramData['mn2t24']['mn2t24'][key],allMeteogramData['mx2t24']['mx2t24'][key]):
                tmpList.append(mn)
                tmpList.append(mx)
            dictNew['2t'][key] = tmpList
        startDate = datetime(int(dictNew['date'][0:4]),int(dictNew['date'][4:6]),int(dictNew['date'][6:8]))
        startDate = pytz.timezone('UTC').localize(startDate)
        if tzName:
            startDate = startDate.astimezone(pytz.timezone(tzName))
        steps = [28 - startDate.utcoffset().total_seconds()/3600]
        print(steps)
        for _ in range(1,len(dictNew['2t']['max'])):
            steps.append(steps[-1]+12)
        dictNew['2t']['steps'] = steps
        allMeteogramData['2t'] = dictNew
        plotTemperature(ax3, allMeteogramData['2t'], fromIndex, toIndex + (toIndex+fromIndex), tzName, plotType)
        plotWindBft(ax4, allMeteogramData['ws24']['ws24'], fromIndex, toIndex, plotType)
    return fig


if __name__ == '__main__':
    #today = datetime.date.today()
    today = datetime.utcnow()
    days = 3
    plotType = "ensemble"
    if len(sys.argv) > 1:
        print(sys.argv)
        from downloadJsonData import getData, getCoordinates
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hd:", ["days=", "lat=", "lon=", "location=", "ensemble", "hres"])
        except getopt.GetoptError:
            print("downloadJsonData.py --location 'Braunschweig, Germany'")
            print("downloadJsonData.py --lat 20 --lon 10")
            print("downloadJsonData.py --ensemble")
            print("downloadJsonData.py --hres")
            sys.exit(2)
        #opts = [i for i in opts]
        #print(opts)
        latitude, longitude, altitude, location = getCoordinates(opts)
        for opt, arg in opts:
            if opt == "-h":
                print("downloadJsonData.py --location 'Braunschweig, Germany'")
                print("downloadJsonData.py --lat 20 --lon 10")
                print("downloadJsonData.py --ensemble")
                print("downloadJsonData.py --hres")
                sys.exit(0)
            elif opt == "--days" or opt == "-d":
                days = int(arg)
            elif opt == "--ensemble":
                plotType = "ensemble"
            elif opt == "--hres":
                plotType = "enhanced-hres"
        if days <= 10:
            allMeteogramData = getData(float(longitude), float(latitude), altitude, writeToFile = False)
        else:
            allMeteogramData = getData(float(longitude), float(latitude), altitude, writeToFile = False, meteogram = "15days")
    else:
        latitude = 52.2646577
        longitude = 10.5236066
        altitude = 79
        location = "Braunschweig, Germany"
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
    fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + timedelta(days))
    fig = plotMeteogram(allMeteogramData, fromIndex, toIndex, tzName, plotType)
    if location is None:
        location = ""
    fig.suptitle(location + " " + str(np.round(latitude, decimals = 5)) +\
                 "°/" + str(np.round(longitude, decimals = 5)) +\
                 "°/" + str(altitude) + "m", fontproperties=prop)

    #fromIndex, toIndex = getTimeFrame(allMeteogramData, today, today + timedelta(10))
    #plt.gcf().autofmt_xdate()
    #logofile = './logo/ECMWF.png'
    #logo = plt.imread(logofile)
    #fig.figimage(logo, 30, 1700)
    #logofile = './logo/ESoWC.png'
    #logo = plt.imread(logofile)
    #fig.figimage(logo, 0, 400)
    if '2t' in allMeteogramData:
        fig.text(0.1,0.03,allMeteogramData['2t']['date']+"-"+allMeteogramData['2t']['time'],fontproperties=prop)
    if 'tp24' in allMeteogramData:
        fig.text(0.1,0.03,allMeteogramData['tp24']['date']+"-"+allMeteogramData['tp24']['time'],fontproperties=prop)
    fig.savefig("./output/forecast.png", dpi = 300)

