# coding=utf-8
"""
/***************************************************************************
Name                 : Spatial Scan
Description          : Spatial Scan Statistic - Spatial Clustering Detection
Date                 : 2014.07.19
copyright            : (C) 2014 by BJ Jang of Gaia3D.com
email                : jangbi882@gmail.com
Sample Data          : juvenile.shp
reference:
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
if not iface:
    iface = qgis.gui.QgisInterface()

import qgis
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math
from math import log
import numpy as np
import time
from bisect import bisect_right

# 전역변수 설정
RANDOM_SEED = int(time.time())
np.random.seed(RANDOM_SEED)

POPULATION_COLUMN = "POPULATION"
CASE_COLUMN = "CASE"
NUM_SIMULATION = 99
LAYER_PREFIX = "Scan_"


def createCircle(center, radius):
    retPointList = []

    centerX = center.x()
    centerY = center.y()
    angleList = np.linspace(0, math.pi*2, 60)

    for angle in angleList:
        crrX = centerX + math.sin(angle)*radius
        crrY = centerY + math.cos(angle)*radius
        retPointList.append(QgsPoint(crrX, crrY))
    return retPointList


#########################
# Collect source data
zoneDic = {} # [0]: centroid, [1]: n, [2]: c

# Select source layer
oLayer = iface.activeLayer()
if not oLayer:
    gErrorMsg = u"You must first select source layer."
    raise UserWarning # 종료


layerName = oLayer.name()
layerType = oLayer.geometryType();
crs = oLayer.crs()

# ID 리스트 확보
zoneList = oLayer.allFeatureIds()

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"Data information collecting...")
progress = QProgressBar()
progress.setMaximum(len(zoneList))
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# centroid, population,case 모으기
sum_n = 0 # sum of populations
sum_c = 0 # sum of cases
for i, zone in enumerate(zoneList):
    progress.setValue(i)

    iFeature = oLayer.getFeatures(QgsFeatureRequest(zone)).next()
    iCent = iFeature.geometry().centroid()
    n = iFeature[POPULATION_COLUMN]
    c = iFeature[CASE_COLUMN]
    zoneDic[zone] = [iCent, n, c]
    sum_n += n
    sum_c += c
# Progress 제거
iface.messageBar().clearWidgets()

############################
# Create Result Layer

#  "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", or "MultiPolygon".
tLayerOption = "{0}?crs={1}&index=yes".format("LineString", crs.authid())
tLayer = QgsVectorLayer(tLayerOption, LAYER_PREFIX+layerName, "memory")
tProvider = tLayer.dataProvider()
tLayer.startEditing()
tProvider.addAttributes([QgsField("ZoneID", QVariant.Int),
                         QgsField("ScannedZone", QVariant.String),
                         QgsField("Grade", QVariant.Int)
])

# Apply symbol
symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(255,0,0))
category1 = QgsRendererCategoryV2(1, symbol, "1st Scanned")

symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(0,255,0))
category2 = QgsRendererCategoryV2(2, symbol, "2nd Scanned")

symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(0,0,255))
category3 = QgsRendererCategoryV2(3, symbol, "3rd Scanned")

categories = [category1, category2, category3]
renderer = QgsCategorizedSymbolRendererV2("Grade", categories)
tLayer.setRendererV2(renderer)


#########################
# LR: Likelihood Ratio

# calculate LR of all zone
LR_list = []
N = float(sum_n) # Population Total
C = float(sum_c) # Case Total
for zone in zoneList:
    n = zoneDic[zone][1]
    c = zoneDic[zone][2]
    if c == 0:
        LR = 0
        LR_list.append([zone, LR])
        continue
    n = float(n) # Population of Zone
    c = float(c) # Case of Zone
#    LR = (((c/n)**c) * ((1.0-(c/n))**(n-c)) * (((C-c)/(N-n))**(C-c)) * ((1-((C-c)/(N-n)))**((N-n)-(C-c)))) \
#         / (((C/N)**C) * ((1-(C/N))**(N-C)))
    # ((C/N)**C) 값의 너무 작아져 실수표현시 항상 0.0 이되어 문제 --> log로 극복
    log_LR = ( c*log(c/n) + (n-c)*log(1.0-(c/n)) + (C-c)*log((C-c)/(N-n)) + ((N-n)-(C-c))*log(1-(C-c)/(N-n)) ) \
             - ( C*log(C/N) + (N-C)*log(1-C/N) )
    LR = math.e ** log_LR
    LR_list.append([zone, LR])

getKey = lambda item: item[1]

obsFstLR = None
obsSndLR = None
osbTrdLR = None

fst_sim_LR = []
snd_sim_LR = []
trd_sim_LR = []


#################################
# Search First aggregated zone
LR_list.sort(key=getKey, reverse=True)
fstZone = LR_list[0][0]
obsFstLR = LR_list[0][1]
fst_sim_LR = [obsFstLR]

fstCent = zoneDic[fstZone][0]
distList = []
for zone in zoneList:
    iCent = zoneDic[zone][0]
    if zone == fstZone:
        continue
    dist = fstCent.distance(iCent)
    distList.append([zone, dist])

# order by distance
distList.sort(key=getKey)

# search maximum range of popTotal < N/2
scannedZoneList = [fstZone]
popTotal = zoneDic[fstZone][1]
for info in distList:
    if popTotal >= (N/2):
        print("First Scanned: %d/%d (%.1f%%)" % (popTotal, N, float(popTotal)/N*100))
        break
    zone = info[0]
    n = zoneDic[zone][1]
    popTotal += n
    scannedZoneList.append(zone)
sndZone = scannedZoneList[-1]
sndCent = zoneDic[sndZone][0]

# Draw circle
tFeature = QgsFeature(tProvider.fields())
tFeature.setGeometry(QgsGeometry.fromPolyline(createCircle(fstCent.vertexAt(0), fstCent.distance(sndCent))))
tFeature.setAttribute(0, fstZone)
tFeature.setAttribute(1, scannedZoneList)
tFeature.setAttribute(2, 1)
tProvider.addFeatures([tFeature])

# Draw Tic
TIC_DIST = 1000
for zone in scannedZoneList:
    cent = zoneDic[zone][0]
    pnt = cent.vertexAt(0)
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()-TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()+TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 1)
    tProvider.addFeatures([tFeature])
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()+TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()-TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 1)
    tProvider.addFeatures([tFeature])

tLayer.commitChanges()
tLayer.updateExtents()
iface.mapCanvas().refresh()


#################################
# Search Second aggregated zone
sndLR_list = []
for LR in LR_list:
    zone = LR[0]
    if scannedZoneList.count(zone) == 0:
        sndLR_list.append([zone, LR])
sndLR_list.sort(key=getKey)

sub_n = 0
fstZone = sndLR_list[0][0]
obsSndLR = sndLR_list[0][1]
snd_sim_LR = [obsSndLR]

fstCent = zoneDic[fstZone][0]
distList = []
for LR in sndLR_list:
    zone = LR[0]
    n = zoneDic[zone][1]
    sub_n += n
    if zone == fstZone:
        continue
    iCent = zoneDic[zone][0]
    dist = fstCent.distance(iCent)
    distList.append([zone, dist])

# order by distance
distList.sort(key=getKey)

# search maximum range of popTotal < N/2
scannedZoneList = [fstZone]
popTotal = zoneDic[fstZone][1]
for info in distList:
    if popTotal >= (sub_n/2):
        print("Second Scanned: %d/%d (%.1f%%)" % (popTotal, sub_n, float(popTotal)/sub_n*100))
        break
    zone = info[0]
    n = zoneDic[zone][1]
    popTotal += n
    scannedZoneList.append(zone)
sndZone = scannedZoneList[-1]
sndCent = zoneDic[sndZone][0]

# Draw circle
tLayer.startEditing()
tFeature = QgsFeature(tProvider.fields())
tFeature.setGeometry(QgsGeometry.fromPolyline(createCircle(fstCent.vertexAt(0), fstCent.distance(sndCent))))
tFeature.setAttribute(0, fstZone)
tFeature.setAttribute(1, scannedZoneList)
tFeature.setAttribute(2, 2)
tProvider.addFeatures([tFeature])

# Draw Tic
TIC_DIST = 1000
for zone in scannedZoneList:
    cent = zoneDic[zone][0]
    pnt = cent.vertexAt(0)
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()-TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()+TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 2)
    tProvider.addFeatures([tFeature])
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()+TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()-TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 2)
    tProvider.addFeatures([tFeature])

tLayer.commitChanges()
tLayer.updateExtents()
iface.mapCanvas().refresh()


#################################
# Search Third aggregated zone
trdLR_list = []
for LR in sndLR_list:
    zone = LR[0]
    if scannedZoneList.count(zone) == 0:
        trdLR_list.append([zone, LR])
trdLR_list.sort(key=getKey)

sub_n = 0
fstZone = trdLR_list[0][0]
obsTrdLR = trdLR_list[0][1]
trd_sim_LR = [obsTrdLR]

fstCent = zoneDic[fstZone][0]
distList = []
for LR in trdLR_list:
    zone = LR[0]
    n = zoneDic[zone][1]
    sub_n += n
    if zone == fstZone:
        continue
    iCent = zoneDic[zone][0]
    dist = fstCent.distance(iCent)
    distList.append([zone, dist])

# order by distance
distList.sort(key=getKey)

# search maximum range of popTotal < N/2
scannedZoneList = [fstZone]
popTotal = zoneDic[fstZone][1]
for info in distList:
    if popTotal >= (sub_n/2):
        print("Third Scanned: %d/%d (%.1f%%)" % (popTotal, sub_n, float(popTotal)/sub_n*100))
        break
    zone = info[0]
    n = zoneDic[zone][1]
    popTotal += n
    scannedZoneList.append(zone)
sndZone = scannedZoneList[-1]
sndCent = zoneDic[sndZone][0]

# Draw circle
tLayer.startEditing()
tFeature = QgsFeature(tProvider.fields())
tFeature.setGeometry(QgsGeometry.fromPolyline(createCircle(fstCent.vertexAt(0), fstCent.distance(sndCent))))
tFeature.setAttribute(0, fstZone)
tFeature.setAttribute(1, scannedZoneList)
tFeature.setAttribute(2, 3)
tProvider.addFeatures([tFeature])

# Draw Tic
TIC_DIST = 1000
for zone in scannedZoneList:
    cent = zoneDic[zone][0]
    pnt = cent.vertexAt(0)
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()-TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()+TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 3)
    tProvider.addFeatures([tFeature])
    geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()+TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()-TIC_DIST, pnt.y()+TIC_DIST)])
    tFeature.setGeometry(geom)
    tFeature.setAttribute(0, fstZone)
    tFeature.setAttribute(1, zone)
    tFeature.setAttribute(2, 3)
    tProvider.addFeatures([tFeature])

tLayer.commitChanges()
tLayer.updateExtents()
iface.mapCanvas().refresh()

# Update Map
tLayer.triggerRepaint()
iface.mapCanvas().refresh()
QgsMapLayerRegistry.instance().addMapLayer(tLayer)

################################
# Hypothesis Testing

for iSim in range(NUM_SIMULATION):
    # Make Monte-Carlo event
    randList = np.random.rand(sum_c)*N
    randCaseDict = {}
    popTotal = 0
    for zone in zoneList:
        popTotal += zoneDic[zone][1]
        index = np.where(randList <= popTotal)
        c = len(randList[index])
        randCaseDict[zone] = c
        randList = np.delete(randList, index)

    if len(randList) > 0:
        zone = zoneList[-1]
        c = len(randList)
        randCaseDict[zone] = c

    # LR: Likelihood Ratio
    LR_sim_list = []
    for zone in zoneList:
        n = zoneDic[zone][1]
        try:
            c = randCaseDict[zone]
        except IndexError:
            c = 0
        if c == 0:
            LR = 0
            LR_sim_list.append([zone, LR])
            continue
        n = float(n) # Population of Zone
        c = float(c) # Case of Zone
        log_LR = ( c*log(c/n) + (n-c)*log(1.0-(c/n)) + (C-c)*log((C-c)/(N-n)) + ((N-n)-(C-c))*log(1-(C-c)/(N-n)) ) \
                 - ( C*log(C/N) + (N-C)*log(1-C/N) )
        LR = math.e ** log_LR
        LR_sim_list.append([zone, LR])

    # Search First aggregated zone
    LR_sim_list.sort(key=getKey, reverse=True)
    fstZone = LR_sim_list[0][0]
    fst_sim_LR.append(LR_sim_list[0][1])

    fstCent = zoneDic[fstZone][0]
    distList = []
    for zone in zoneList:
        iCent = zoneDic[zone][0]
        if zone == fstZone:
            continue
        dist = fstCent.distance(iCent)
        distList.append([zone, dist])

    # order by distance
    distList.sort(key=getKey)

    # search maximum range of popTotal < N/2
    scannedZoneList = [fstZone]
    popTotal = zoneDic[fstZone][1]
    for info in distList:
        if popTotal >= (N/2):
            break
        zone = info[0]
        n = zoneDic[zone][1]
        popTotal += n
        scannedZoneList.append(zone)
    sndZone = scannedZoneList[-1]
    sndCent = zoneDic[sndZone][0]

    # Search Second aggregated zone
    sndLR_list = []
    for LR in LR_sim_list:
        zone = LR[0]
        if scannedZoneList.count(zone) == 0:
            sndLR_list.append([zone, LR])
    sndLR_list.sort(key=getKey)

    sub_n = 0
    fstZone = sndLR_list[0][0]
    snd_sim_LR.append(sndLR_list[0][1])

    fstCent = zoneDic[fstZone][0]
    distList = []
    for LR in sndLR_list:
        zone = LR[0]
        n = zoneDic[zone][1]
        sub_n += n
        if zone == fstZone:
            continue
        iCent = zoneDic[zone][0]
        dist = fstCent.distance(iCent)
        distList.append([zone, dist])

    # order by distance
    distList.sort(key=getKey)

    # search maximum range of popTotal < N/2
    scannedZoneList = [fstZone]
    popTotal = zoneDic[fstZone][1]
    for info in distList:
        if popTotal >= (sub_n/2):
            break
        zone = info[0]
        n = zoneDic[zone][1]
        popTotal += n
        scannedZoneList.append(zone)
    sndZone = scannedZoneList[-1]
    sndCent = zoneDic[sndZone][0]

    # Search Third aggregated zone
    trdLR_list = []
    for LR in sndLR_list:
        zone = LR[0]
        if scannedZoneList.count(zone) == 0:
            trdLR_list.append([zone, LR])
    trdLR_list.sort(key=getKey)

    sub_n = 0
    fstZone = trdLR_list[0][0]
    trd_sim_LR.append(trdLR_list[0][1])

    fstCent = zoneDic[fstZone][0]
    distList = []
    for LR in trdLR_list:
        zone = LR[0]
        n = zoneDic[zone][1]
        sub_n += n
        if zone == fstZone:
            continue
        iCent = zoneDic[zone][0]
        dist = fstCent.distance(iCent)
        distList.append([zone, dist])

    # order by distance
    distList.sort(key=getKey)

    # search maximum range of popTotal < N/2
    scannedZoneList = [fstZone]
    popTotal = zoneDic[fstZone][1]
    for info in distList:
        if popTotal >= (sub_n/2):
            break
        zone = info[0]
        n = zoneDic[zone][1]
        popTotal += n
        scannedZoneList.append(zone)
    sndZone = scannedZoneList[-1]
    sndCent = zoneDic[sndZone][0]

#########################
# Calculate p-value
fst_sim_LR.sort()
snd_sim_LR.sort()
trd_sim_LR.sort()

fst_pos = bisect_right(fst_sim_LR, obsFstLR)
fst_p = (1.0 - (float(fst_pos) / float(NUM_SIMULATION+1))) * 100.0

snd_pos = bisect_right(snd_sim_LR, obsSndLR)
snd_p = (1.0 - (float(snd_pos) / float(NUM_SIMULATION+1))) * 100.0

trd_pos = bisect_right(trd_sim_LR, obsTrdLR)
trd_p = (1.0 - (float(trd_pos) / float(NUM_SIMULATION+1))) * 100.0

resString = ("1st p-value:%.1f, 2nd p-value:%.1f, 3rd p-value:%.1f" % (fst_p, snd_p, trd_p))
print (resString)
iface.messageBar().pushMessage(":", resString)
