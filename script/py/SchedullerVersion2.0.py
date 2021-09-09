#!/usr/bin/env python
# coding: utf-8

# In[162]:


import os
import sys
import time
import json
import math
import copy
import random
import _thread
import numpy as np
import matplotlib.pyplot as plt
from labellines import labelLines
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
from astropy.coordinates import ICRS, Galactic, FK4, FK5

start = "2021.07.24 02:00:00"
end = "2021.07.24 11:00:00"
telescope = [31, 121.9, 10] #[Lat., Lon., Hei.] TM Tele.
elev_range = [15, 75] #[min., max.] TM Tele.
#telescope = [32.701500, -109.891284, 3185] #[Lat., Lon., Hei.] AZ Tele.
#elev_range = [30, 80] #[min., max.] AZ Tele.

psrListFilename = "psr_list.txt"


# In[166]:


def getPsrName(array):
    if("3C" in array["source"]):
        return array["source"].replace("'", "").replace('"', "")
    if("G" in array["source"]):
        return array["source"].replace("'", "").replace('"', "")
    return "PSR" + array["source"].replace("'", "").replace('"', "")

def sorting_rewrite(array):
    listForSorting = list()
    for i in range(len(array)):
        listForSorting.append([i, array[i]["rises"][0][0]])
        
    listForSorting = sorted(listForSorting, key=lambda x:x[1])
    for i in range(len(listForSorting)):
        listForSorting[i] = array[listForSorting[i][0]]

    return listForSorting

def hours_plus(time1, time2):
    time0 = time1 + time2
    while(time0 > 24):
        time0 = time0 - 24
    
    return time0

def gen_axis(start, hours, gap=2):
    axis = []
    added_hours = 0
    while(hours > added_hours):
        added_hours = added_hours + gap
        axis.append(hours_plus(start, added_hours))
    
    return axis

# 绘制图像
def psr_plot(loadedKey):
    PSRS = list()
    #loadedKey = compute_durs(loadedKey)
    plt.rcParams['figure.figsize'] = (16,8)
    
    for key in range(len(loadedKey)):
        value = loadedKey[key]
        #print(loadedKey[key]["source"])
        star_name = getPsrName(loadedKey[key])
        # print(star_name)
        skyCo = SkyCoord.from_name(star_name.replace("'", ""))
        transformed = skyCo.transform_to(altazframe)
        PSRS.append(skyCo)
        # print(skyCo)

        plt.scatter(delta_midnight, transformed.alt,lw=0,s=5, c='k', alpha=0.1, cmap='coolwarm')
        #print(transformed.alt[1:3])
        #print(delta_midnight[math.floor(1000*(value["dur_started"]/86400)):math.floor(1000*(value["dur_ended"]/86400))])
        #plt.plot(delta_midnight[value["dur_started"]:value["dur_ended"]],PSR_B0329altazs[value["dur_ended"]:value["dur_ended"]].alt, c='b', label='PSR B0329+54' )

    for key in range(len(loadedKey)):
        value = loadedKey[key]
        #print(loadedKey[key]["source"])
        star_name = getPsrName(loadedKey[key])
        # print(star_name)
        skyCo = SkyCoord.from_name(star_name.replace("'", ""))
        transformed = skyCo.transform_to(altazframe)
        PSRS.append(skyCo)
        # print(skyCo)
        
        obs_begin = value["dur_started"] - startTimestamp
        obs_end = value["dur_ended"] - startTimestamp

        plt.scatter(delta_midnight[math.floor(1000*(obs_begin/(plotLength*60*60))):math.floor(1000*(obs_end/(plotLength*60*60)))], transformed.alt[math.floor(1000*(obs_begin/(plotLength*60*60))):math.floor(1000*(obs_end/(plotLength*60*60)))], label=star_name,lw=2,s=5)
        #print(transformed.alt[1:3])
        #print(delta_midnight[math.floor(1000*(value["dur_started"]/86400)):math.floor(1000*(value["dur_ended"]/86400))])
        #plt.plot(delta_midnight[value["dur_started"]:value["dur_ended"]],PSR_B0329altazs[value["dur_ended"]:value["dur_ended"]].alt, c='b', label='PSR B0329+54' )

    for key in range(len(loadedKey)):
        value = loadedKey[key]
        #print(loadedKey[key]["source"])
        star_name = getPsrName(loadedKey[key])
        # print(star_name)
        skyCo = SkyCoord.from_name(star_name.replace("'", ""))
        transformed = skyCo.transform_to(altazframe)
        PSRS.append(skyCo)
        # print(skyCo)
        
        obs_begin = value["dur_started"] - startTimestamp
        obs_end = value["dur_ended"] - startTimestamp

        plt.scatter(delta_midnight[math.floor(1000*((obs_end-value["gap"])/(plotLength*60*60))):math.floor(1000*((obs_end)/(plotLength*60*60)))], transformed.alt[math.floor(1000*((obs_end-value["gap"])/(plotLength*60*60))):math.floor(1000*((obs_end)/(plotLength*60*60)))],lw=2,s=5, c='k', alpha=1)
        #print(transformed.alt[1:3])
        #print(delta_midnight[math.floor(1000*(value["dur_started"]/86400)):math.floor(1000*(value["dur_ended"]/86400))])
        #plt.plot(delta_midnight[value["dur_started"]:value["dur_ended"]],PSR_B0329altazs[value["dur_ended"]:value["dur_ended"]].alt, c='b', label='PSR B0329+54' )

    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    plt.xlim(0, 0.7*24)
    plt.xticks(np.arange((plotLength/2)+1)*2)
    #plt.xticks(gen_axis(int(abs_start_hours), durations/60/60))
    #print(gen_axis(int(abs_start_hours), durations/60/60))
    plt.ylim(0, 90)
    plt.title("Schedule Preview")
    plt.grid()
    plt.xlabel('Hours from UTC '+ time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(start, "%Y.%m.%d %H:%M:%S")))
    plot = plt.ylabel('Altitude [deg]')
    plt.show()
    
    return True

def psr_load(keyin_file):
    rawKey = ""
    fileHandler = open(keyin_file, "r")
    while  True:
        # Get next line from file
        line = fileHandler.readline()
        # If line is empty then end of file reached
        if not line :
            break;
        thisLineRaw = line.strip()
        
        if("source" in thisLineRaw):
            rawKey = rawKey + "\n" + thisLineRaw
        # Close Close    
    fileHandler.close()
    
    keyin_file = keyin_file + ".temp"
    open(keyin_file, "w+").write(rawKey)
    
    abs_start_hours = (time.strftime("%H", time.strptime(start, "%Y.%m.%d %H:%M:%S")))
    matrix_raw = np.loadtxt(open(keyin_file,"r"),delimiter=None, dtype=str, converters=None, skiprows=0)  
    shape_raw = matrix_raw.shape
    
    num_vars = ["dur", "gap"]
    keyLocats =[[0, 2], [3, 5], [6, 8], [9, 11]]
    loadedKey = list()
    for a in range(shape_raw[0]):
        #loadedKey[a] = dict()
        loadedKey.append(dict())
        for keyLoc in keyLocats:
            if(matrix_raw[a, keyLoc[0]] in num_vars):
                loadedKey[a][matrix_raw[a, keyLoc[0]]] = int(matrix_raw[a, keyLoc[1]])
            else:
                loadedKey[a][matrix_raw[a, keyLoc[0]]] = matrix_raw[a, keyLoc[1]]
    
    os.remove(keyin_file)
    return loadedKey

def loadJson(filename):
    rawJson = ""
    fileHandler = open(filename, "r")
    while  True:
        # Get next line from file
        line = fileHandler.readline()
        # If line is empty then end of file reached
        if not line :
            break;
        thisLineRaw = line.strip()
        
        thisLine = ""
        for thisChar in thisLineRaw:
            if(thisChar == "#"):
                break
            thisLine = thisLine + thisChar
        rawJson = rawJson + "\n" + thisLine
        # Close Close    
    fileHandler.close()
    
    return json.loads(rawJson)

def runOnCmd():
    global psrListFilename
    psrListFilename = sys.argv[1]
    
    return True

def loadConfigFromJson(psrListFile):
    rawJson = loadJson(psrListFile)
    
    global start
    global end
    global telescope
    global elev_range
    
    start = rawJson["obs_start"]
    end = rawJson["obs_end"]
    telescope = rawJson["tele_loc"]
    elev_range = rawJson["elev_range"]

def psr_load_list(psrListFilename=False):
    psrList = list()
    psrListRaw = loadJson(psrListFilename)['sources']
    for thisPsr in psrListRaw:
        psrList.append({"source": thisPsr['identifier'], "dur": thisPsr['dur'], "gap": 0, "setup": ""})
    
    return psrList

def compute_durs(importedKey):
    durations = startTimestamp
    for a in range(len(importedKey)):
        #loadedKey[a] = dict()
        importedKey[a]["dur_started"] = durations
        
        durations = durations + int(importedKey[a]['dur']) + int(importedKey[a]['gap'])
                
        importedKey[a]["dur_ended"] = durations
    return importedKey

def coord(psrName, retList = False):
    skyCo = SkyCoord.from_name(psrName)
    if(retList == False):
        return skyCo
    
    skyCo = skyCo.to_string().split(" ")
    skyCo[0] = float(skyCo[0])
    skyCo[1] = float(skyCo[1])
    
    return skyCo

def gap_between(key1, key2, velocity = [.5, .6]):
    key1_coord = coord(getPsrName(key1), True)
    key2_coord = coord(getPsrName(key2), True)
    dCoord = [abs(key1_coord[0] - key2_coord[0]), abs(key1_coord[1] - key2_coord[1])]
    tCoord = [dCoord[0]/velocity[0], dCoord[1]/velocity[1]]
    # print(tCoord)
    return max(tCoord)

def Timestamp(timestamp):
    return Time(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)))

def riseTime(psrName, location, begin, end, gap = 500):
    lastAlt = -1
    rised = -1
    rises = list()
    for i in range(int((end-begin)/gap)):
        Timestamp(begin)
        thisAlt = float(coord(psrName).transform_to(AltAz(obstime=Timestamp(begin), location=shanghai)).to_string().split(" ")[1])
        
        if((lastAlt < elev_range[0] and thisAlt > elev_range[0])):
            rised = begin
        elif(lastAlt > elev_range[1] and thisAlt < elev_range[1]):
            rised = begin
        elif((lastAlt < elev_range[1] and thisAlt > elev_range[1])):
            rises.append([rised, begin])
            rised = -1
        elif(lastAlt > elev_range[0] and thisAlt < elev_range[0]):
            rises.append([rised, begin])
            rised = -1
            
        begin = begin + gap
        lastAlt = thisAlt
    
    if(rised != -1):
        rises.append([rised, begin])
    
    if(len(rises) <= 0):
        rises.append([end+1, end+1])
    
    return rises

def shortest_rise(array):
    shortest = False
    shortestlen = -1
    for i in range(len(array)):
        thisRiseLen = 0
        for a in range(len(array[i]["rises"])):
            thisRiseLen = thisRiseLen + array[i]["rises"][a][1] - array[i]["rises"][a][0]
            
        if(thisRiseLen < shortest or thisRiseLen == -1):
            shortest = i
            shortestlen = thisRiseLen
    
    return shortest
      
def nearest_sorting(importedKey, first = False):
    newList = list()
    impList = copy.deepcopy(importedKey)
    
    if(first == False):
        first = smallestRA(impList)
        
    newList = [impList[first]]
    del impList[first]
    while(len(impList) > 0):
        nextPsr = nearest(impList, len(impList)-1)
        newList.append(impList[nextPsr])
        del impList[nextPsr]
    
    return newList

def nearest(importedKey, k, farest = False):
    lastRA = -1
    lastDec = -1
    distKey = list()
    star_name = getPsrName(importedKey[k])
    skyCo = SkyCoord.from_name(star_name.replace("'", ""))
    sourceRA = float(skyCo.to_string().split(" ")[0])
    sourceDec = float(skyCo.to_string().split(" ")[1])
    
    testKey = [list(), list()]
    nearestKey = [0, False]
    for i in range(len(importedKey)):
        if(i != k):
            star_name = getPsrName(importedKey[i])
            skyCo = SkyCoord.from_name(star_name.replace("'", ""))
            thisRA = float(skyCo.to_string().split(" ")[0])
            thisDec = float(skyCo.to_string().split(" ")[1])
            dDist = math.sqrt(abs(thisRA - sourceRA)**2 + abs((thisDec - sourceDec))**2)
            
            if(nearestKey[0] > dDist or nearestKey[1] == False):
                nearestKey = [dDist, i]
                testKey[0].append(thisRA)
                testKey[1].append(thisDec)
    
    if(farest):
        nearestKey = [0, False]
        for i in range(len(importedKey)):
            if(i != k):
                star_name = getPsrName(importedKey[i])
                skyCo = SkyCoord.from_name(star_name.replace("'", ""))
                thisRA = float(skyCo.to_string().split(" ")[0])
                thisDec = float(skyCo.to_string().split(" ")[1])
                dDist = math.sqrt(abs(thisRA - sourceRA)**2 + abs((thisDec - sourceDec))**2)

                if(nearestKey[0] < dDist or nearestKey[1] == False):
                    nearestKey = [dDist, i]
        
        return nearestKey[1]
    
    return nearestKey[1]

def sortedbyRA(importedKey, listi = False):
    listForSorting = list()
    for i in range(len(importedKey)):
        star_name = getPsrName(importedKey[i])
        skyCo = SkyCoord.from_name(star_name.replace("'", ""))
        thisRA = float(skyCo.to_string().split(" ")[0])
        thisDec = float(skyCo.to_string().split(" ")[1])
        
        listForSorting.append([i, thisRA])
    
    sortedList = list()
    listForSorting = sorted(listForSorting, key=lambda x:x[1])
    if(listi):
        return listForSorting
    
    for i in range(len(listForSorting)):
        sortedList.append(importedKey[listForSorting[i][0]])
    
    return sortedList

def smallestRA(importedKey):
    return sortedbyRA(importedKey, True)[0][0]
        
def previewKey(importedKey):
    psr_plot(importedKey)
    #print(importedKey)
    #for i in range(len(importedKey)):
    #    print(importedKey[i]['source'])
    print("##########################\n## EXPORTED KEY PREVIEW ##\n##########################")
    print(saveAsKeyinFile(importedKey))

def saveAsKeyinFile(importedKey, filename = False):
    keyinFile = ""
    for i in range(len(sortedKey)):
        if(i == 0):
            keyinFile = keyinFile + "year=" + time.strftime("%Y", time.localtime(importedKey[i]['dur_started'])) + "\n"
            keyinFile = keyinFile + "month=" + time.strftime("%m", time.localtime(importedKey[i]['dur_started'])) + "\n"
            keyinFile = keyinFile + "day=" + time.strftime("%d", time.localtime(importedKey[i]['dur_started'])) + "\n"
            keyinFile = keyinFile + "start=" + time.strftime("%H:%M:%S", time.localtime(importedKey[i]['dur_started'])) + "\n"
            
        keyinFile = keyinFile + "source = "+sortedKey[i]['source']+"		dur = "+str(sortedKey[i]['dur'])+"	gap = "+str(int(sortedKey[i]['gap']))+" setup = 'pfb20cm2'	/" + "\n" 
        
    if(filename != False):
        open(filename, "w+").write(keyinFile)
        
    return keyinFile

def get_cmd(indicator="scheduller"):
    cmd = input("[" + indicator + "] > ").split(" ")
    cmd_dict = dict()
    
    for i in range(len(cmd)):
        cmd_dict[i] = cmd[i]
    
    return cmd_dict

def if_in_list(theList, key):
    theList_dict = dict()
    for i in range(len(theList)):
        theList_dict[i] = theList[i]
    
    if(key in theList_dict):
        return True
    
    return False

def monitoring_txt(filename):
    auto = False
    while(1):
        psr_plot(compute_durs(psr_load(filename)))
        
        if(auto):
            time.sleep(1)
        else:
            cmd = get_cmd("EDITING "+filename)[0]
            if(cmd == "exit"):
                break
            elif(cmd == "auto"):
                auto = True

def scoring(importedPossibility, obsLength):
    thisScore = 0
        
    ## 基于时间的利用率
    durations = 0
    for thisKey in importedPossibility['key']:
        durations = durations + thisKey['dur']
    thisScore = thisScore + ((durations)/obsLength)*10

    ## 基于转动时长（gap）打分
    gap_len = 0.00000001
    for thisKey in importedPossibility['key']:
        gap_len = gap_len + thisKey['gap']
    thisScore = thisScore + (1/gap_len)*10
    
    return thisScore

def if_observable(start, end, array, step=1800):
    star_name = getPsrName(array)
    observable = True
    
    rises = array['rises']
    rise_obs = False
    for rise in rises:
        if(rise[0] <= start and rise[1] >= end):
            rise_obs = True
    if(rise_obs != True):
        observable = False
    
    #nowTime = start
    #while(nowTime < end):
    #    elevation = float(coord(star_name).transform_to(AltAz(obstime=Timestamp(nowTime), location=shanghai)).to_string().split(" ")[1])
    #    if(elevation < 15 and elevation > 75):
    #        observable = False
    #        
    #    nowTime = nowTime + step
        
    return observable

#print(if_observable(0, 100000, psrList[0]))

#sortedbyRA(loadedKey)
#smallestRA(loadedKey)
#riseTime("PSR J1809-1943", shanghai, startTimestamp, endTimestamp, gap = 599)
#sortedbyRA(psr_load(keyin_file), True)


# In[165]:


runOnCmd()
loadConfigFromJson(psrListFilename)
startTimestamp = time.mktime(time.strptime(start, "%Y.%m.%d %H:%M:%S"))
endTimestamp = time.mktime(time.strptime(end, "%Y.%m.%d %H:%M:%S"))
plotLength = int(endTimestamp - startTimestamp)/60/60 + 1
psrList = psr_load_list(psrListFilename)
shanghai = EarthLocation(lat=telescope[0]*u.deg, lon=telescope[1]*u.deg, height=telescope[2]*u.m)
midnight = Time(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTimestamp)), scale='utc')
delta_midnight = np.linspace(0, plotLength, 1000)*u.hour
times = midnight + delta_midnight
altazframe = AltAz(obstime=times, location=shanghai)

#print(psrList)
for i in range(len(psrList)):
    psrName = (getPsrName(psrList[i])).replace("'", "")
    print("[PROCESSING " + str(i+1) + "/" + str(len(psrList)) + "] " + psrName)
    psrList[i]['rises'] = riseTime(psrName, shanghai, startTimestamp, endTimestamp)

#previewKey(loadedKey)


# In[102]:


possibilities = list()
for i in range(len(psrList)):
    print("[SORTING " + str(i+1) + "/" + str(len(psrList)) + "] Starting with " + psrList[i]['source'])
    loadedKey = nearest_sorting(psrList, i)
    #loadedKey = sortedbyRA(loadedKey)
    #loadedKey = nearest_sorting(loadedKey)

    search_gap = 500
    nowTime = startTimestamp
    procedKey = copy.deepcopy(sorting_rewrite(loadedKey))
    sortedKey = list()
    lastSearchGap = 0
    while(nowTime < endTimestamp):
        if(len(procedKey) <= 0):
            break

        thisSched = False

        for i in range(len(procedKey)):
            thisprocedKey = procedKey[i]
            thisDur = float(thisprocedKey['dur'])

            if(if_observable(nowTime, nowTime + thisDur, thisprocedKey)):
                #print(thisprocedKey["source"])
                #sortedKey.append(thisprocedKey)
                #nowTime = nowTime + thisDur
                #del procedKey[i]
                thisSched = [i, thisDur]
                #print(procedKey)
                break

        shortestRisekeyi = shortest_rise(procedKey)
        if(if_observable(nowTime, nowTime + float(procedKey[shortestRisekeyi]['dur']), procedKey[shortestRisekeyi])):
            #print(procedKey[shortestRisekeyi]["source"])
            #sortedKey.append(procedKey[shortestRisekeyi])
            #nowTime = nowTime + thisDur
            #del procedKey[shortestRisekeyi]
            if(thisSched != False):
                if(if_observable(nowTime + thisSched[1], nowTime + thisSched[1] + float(procedKey[shortestRisekeyi]['dur']), procedKey[shortestRisekeyi]) == False):
                    thisSched = [shortestRisekeyi, float(procedKey[shortestRisekeyi]['dur'])]
            else:
                thisSched = [shortestRisekeyi, float(procedKey[shortestRisekeyi]['dur'])]
            #print(procedKey)

        if(thisSched == False):
            nowTime = nowTime + search_gap #如果这次循环没有匹配到可观测的源就把时间往后
            if(len(sortedKey) >= 1):
                lastSearchGap = lastSearchGap + search_gap
        else:
            sortedKey.append(procedKey[thisSched[0]])
            sortedKey[len(sortedKey) - 1]['dur_started'] = nowTime
            nowTime = nowTime + thisSched[1]
            sortedKey[len(sortedKey) - 1]['dur_ended'] = nowTime
            del procedKey[thisSched[0]]

            if(len(sortedKey) >= 2):
                sortedKey[len(sortedKey) - 2]["gap"] = gap_between(sortedKey[len(sortedKey) - 2], sortedKey[len(sortedKey) - 1]) + lastSearchGap
                sortedKey[len(sortedKey) - 2]["dur_ended"] = sortedKey[len(sortedKey) - 2]["dur_ended"] +  sortedKey[len(sortedKey) - 2]["gap"]
                nowTime = nowTime + sortedKey[len(sortedKey) - 2]["gap"]
            
            lastSearchGap = 0
            
    possibilities.append({"key": sortedKey, "scheduled": sortedKey, "non_scheduled": procedKey})
    
    scheduled = ""
    for a in sortedKey:
        scheduled = scheduled + " " + a['source']
    #print("scheduled: ", scheduled)
    
    non_scheduled = ""
    for a in procedKey:
        non_scheduled = non_scheduled + " " + a['source']
    #print("non-scheduled: ", non_scheduled)
    #print()


# In[156]:


# 寻最佳纲要
scores = list()
for i in range(len(possibilities)):
    possibilities[i]['score'] = scoring(possibilities[i], endTimestamp - startTimestamp)
    scores.append([possibilities[i]['score'], i])
scores = sorted(scores, key=lambda x:x[0], reverse=True)

keyPreviewing = list()
for i in range(1):
    print("#", i, "Previewing [ Key", scores[i][1], "]")
    print("Scheduled ", len(possibilities[scores[i][1]]['scheduled']), "out of", len(possibilities[scores[i][1]]['scheduled']) + len(possibilities[scores[i][1]]['non_scheduled']))
    #print("Scheduled ", possibilities[scores[i][1]]['scheduled'])
    #print("Non-scheduled ", possibilities[scores[i][1]]['non_scheduled'])
    previewKey(possibilities[scores[i][1]]['key'])
    keyPreviewing = possibilities[scores[i][1]]


# In[159]:


while(1):
    try:
        cmd = get_cmd()
        if(cmd[0] == "save"):
            if(1 in cmd):
                if(cmd[1] == "sched" or cmd[1] == ".key"):
                    if(2 in cmd):
                        savedName = cmd[2]
                        saveAsKeyinFile(keyPreviewing['key'], savedName)
                        print("saved.")
                        #monitoring_txt(savedName)
                    else:
                        print('No filename specified.\n Do you means "save sorted.key"? ')
                else:
                    print('Unsupported type.\n Supported type(s): "sched", ".key". ')
            else:
                print('No type of file specified.\n Try "save .key sorted.key". ')
        elif(cmd[0] == "edit"):
            if(1 in cmd):
                monitoring_txt(cmd[1])
            else:
                print('No filename specified.\n Do you means "edit sorted.key"? ')
        elif(cmd[0] == "preview"):
            if(1 in cmd):
                thisPreviewId = int(cmd[1]) - 1
                if(if_in_list(scores, thisPreviewId)):
                    keyPreviewing = possibilities[scores[thisPreviewId][1]]
                    previewKey(possibilities[scores[thisPreviewId][1]]['key'])
                else:
                    print("Preview ID does not exists.")
            else:
                print(cmd)
                print('No preview specified.\n Try "preview 1".')
        #sorted/non-sorted
        elif(cmd[0] == "show"):
            if(cmd[1] == "scheduled"):
                scheduled = ""
                for a in keyPreviewing['scheduled']:
                    scheduled = scheduled + " " + a['source']
                print(scheduled)
            elif(cmd[1] == "not" and cmd[2] == "scheduled"):
                non_scheduled = ""
                for a in keyPreviewing['non_scheduled']:
                    non_scheduled = non_scheduled + " " + a['source']
                print(non_scheduled)
            else:
                print("Unknown variable", cmd[1])
        elif(cmd[0] == "exit"):
            break
    except Exception as e:
        print("Fatal Error Catched: ", str(e))


# In[ ]:




