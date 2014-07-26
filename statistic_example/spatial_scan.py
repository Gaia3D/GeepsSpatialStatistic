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

POPULATION_COLUMN = "CONTROL"
CASE_COLUMN = "CASE"
NUM_SIMULATION = 999
LAYER_PREFIX = "Scan_"

MIN_RADIUS = 6000
TIC_DIST = 1000


# lambda function for sort by second item
getSecond = lambda item: item[1]

# 지역정보 저장 클래스
class ZoneInfo():
    cent = None
    n = None
    c = None
    def __init__(self, cent, n, c):
        self.cent = cent
        self.n = n
        self.c = c

# Likelihood Ratio Calculation function
def calcLR(N, C, n, c):
    if c == 0:
        LR = 0
        return LR

    N = float(N)
    C = float(C)
    n = float(n) # Population of Zone
    c = float(c) # Case of Zone
#    LR = (((c/n)**c) * ((1.0-(c/n))**(n-c)) * (((C-c)/(N-n))**(C-c)) * ((1-((C-c)/(N-n)))**((N-n)-(C-c)))) \
#         / (((C/N)**C) * ((1-(C/N))**(N-C)))
    # ((C/N)**C) 값의 너무 작아져 실수표현시 항상 0.0 이되어 문제 --> log로 극복
    log_LR = ( c*log(c/n) + (n-c)*log(1.0-(c/n)) + (C-c)*log((C-c)/(N-n)) + ((N-n)-(C-c))*log(1-(C-c)/(N-n)) ) \
             - ( C*log(C/N) + (N-C)*log(1-C/N) )
    LR = math.e ** log_LR
    return LR

# 주어진 지역에 대해 LR이 가장 큰 지역과 주변이 합쳐져서 가장 LR이 큰 지역관련 정보 계산
def scan(zoneDic, zoneList):
    # return value
    resZoneID = None
    resZoneCent = None
    resRadius = None
    resLR = None
    resNearZone_list = []

    # zoneList에 있는 지역의 모집단수(N)과 케이스수(C) 확보
    N = 0
    C = 0
    for zone in zoneList:
        N += zoneDic[zone].n
        C += zoneDic[zone].c

    # 가장 LR이 큰 지역 찾기
    LR_list = [[zone, calcLR(N, C, zoneDic[zone].n, zoneDic[zone].c)] for zone in zoneList]
    LR_list.sort(key=getSecond, reverse=True)
    resZoneID = LR_list[0][0]
    resLR = LR_list[0][1]
    resZoneCent = zoneDic[resZoneID].cent

    # 찾은 지역으로 부터 거리순 소팅
    dist_list = []
    for zone in zoneList:
        iCent = zoneDic[zone].cent
        if zone == resZoneID:
            continue
        dist = resZoneCent.distance(iCent)
        dist_list.append([zone, dist])
    dist_list.sort(key=getSecond)

    # 절반이 될 때까지 합치며 진행한 중에 가장 LR이 큰 지역 찾기
    sub_n = zoneDic[resZoneID].n
    sub_c = zoneDic[resZoneID].c
    resNearZone_list = [resZoneID]
    tempLR_list = [[resZoneID, resLR]]
    for info in dist_list:
        if sub_n >= (N/2.0):
            break
        zone = info[0]
        resNearZone_list.append(zone)
        sub_n += zoneDic[zone].n
        sub_c += zoneDic[zone].c
        tempLR = calcLR(N, C, sub_n, sub_c)
        tempLR_list.append([zone, tempLR])
    tempLR_list.sort(key=getSecond, reverse=True)
    edgeZone = tempLR_list[0][0]
    edgeCent = zoneDic[edgeZone].cent

    # 합쳐진 지역의 LR을 반환
    resLR = tempLR_list[0][1]

    # 합쳐진 지역에 대한 정보 추출
    if resZoneID == edgeZone:
        resRadius = MIN_RADIUS
    else:
        resRadius = resZoneCent.distance(edgeCent)
    ii = resNearZone_list.index(edgeZone)
    resNearZone_list = resNearZone_list[ : ii+1]

    # 최종 결과 반환
    return (resZoneID, resZoneCent, resRadius, resLR, resNearZone_list)

# 중심과 반경으로 원 그리기
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

def drawResult(grade, zoneID, zoneCent, radius, nearZone_list):
    # make near zone list string
    nearZone_str = ""
    for zone in nearZone_list:
        if nearZone_str != "":
            nearZone_str += ","
        nearZone_str += str(zone)

    # Draw circle
    tFeature = QgsFeature(tProvider.fields())
    tFeature.setGeometry(QgsGeometry.fromPolyline(createCircle(zoneCent.vertexAt(0), radius)))
    tFeature.setAttribute(0, zoneID)
    tFeature.setAttribute(1, nearZone_str)
    tFeature.setAttribute(2, grade)
    tProvider.addFeatures([tFeature])

    # Draw Tic
    for zone in nearZone_list:
        cent = zoneDic[zone].cent
        pnt = cent.vertexAt(0)
        geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()-TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()+TIC_DIST, pnt.y()+TIC_DIST)])
        tFeature.setGeometry(geom)
        tFeature.setAttribute(0, zoneID)
        tFeature.setAttribute(1, zone)
        tFeature.setAttribute(2, grade)
        tProvider.addFeatures([tFeature])
        geom = QgsGeometry.fromPolyline([QgsPoint(pnt.x()+TIC_DIST, pnt.y()-TIC_DIST), QgsPoint(pnt.x()-TIC_DIST, pnt.y()+TIC_DIST)])
        tFeature.setGeometry(geom)
        tFeature.setAttribute(0, zoneID)
        tFeature.setAttribute(1, zone)
        tFeature.setAttribute(2, grade)
        tProvider.addFeatures([tFeature])


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
orgZone_list = oLayer.allFeatureIds()

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"Data information collecting...")
progress = QProgressBar()
progress.setMaximum(len(orgZone_list))
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# centroid, population,case 모으기
sum_n = 0 # sum of populations
sum_c = 0 # sum of cases
for i, zone in enumerate(orgZone_list):
    progress.setValue(i)

    iFeature = oLayer.getFeatures(QgsFeatureRequest(zone)).next()
    iCent = iFeature.geometry().centroid()
    n = iFeature[POPULATION_COLUMN]
    c = iFeature[CASE_COLUMN]
    zoneDic[zone] = ZoneInfo(iCent, n, c)
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
symbol.setColor(QColor(0,0,255))
category2 = QgsRendererCategoryV2(2, symbol, "2nd Scanned")

symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(0,255,0))
category3 = QgsRendererCategoryV2(3, symbol, "3rd Scanned")

categories = [category1, category2, category3]
renderer = QgsCategorizedSymbolRendererV2("Grade", categories)
tLayer.setRendererV2(renderer)


#########################
# 첫 지역 산출
fstZone, fstCent, fstRadius, fstLR, fstNearZone_list = scan(zoneDic, orgZone_list)
drawResult(1, fstZone, fstCent, fstRadius, fstNearZone_list)

#################################
# 두번째 지역 산출

# 처음 찾아진 지역을 제외한 지역 리스트 구축
sndZone_list = []
for zone in orgZone_list:
    if fstNearZone_list.count(zone) == 0:
        sndZone_list.append(zone)

# 지역 산출
sndZone, sndCent, sndRadius, sndLR, sndNearZone_list = scan(zoneDic, sndZone_list)
drawResult(2, sndZone, sndCent, sndRadius, sndNearZone_list)

#################################
# 세번째 지역 산출

# 두번째 찾아진 지역을 제외한 지역 리스트 구축
trdZone_list = []
for zone in sndZone_list:
    if sndNearZone_list.count(zone) == 0:
        trdZone_list.append(zone)

# 지역 산출
trdZone, trdCent, trdRadius, trdLR, trdNearZone_list = scan(zoneDic, trdZone_list)
drawResult(3, trdZone, trdCent, trdRadius, trdNearZone_list)

# Update Map
tLayer.commitChanges()
tLayer.triggerRepaint()
iface.mapCanvas().refresh()
QgsMapLayerRegistry.instance().addMapLayer(tLayer)


################################
# Hypothesis Testing

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"Monte-Carlo Simulating...")
progress = QProgressBar()
progress.setMaximum(NUM_SIMULATION)
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

fst_sim_LR = [fstLR]
snd_sim_LR = [sndLR]
trd_sim_LR = [trdLR]
for iSim in range(NUM_SIMULATION):
    progress.setValue(iSim)

    # Make Monte-Carlo event by zone's n rate
    randList = np.random.rand(sum_c)*sum_n
    sim_zoneDic = zoneDic.copy()
    popTotal = 0
    for zone in orgZone_list:
        popTotal += zoneDic[zone].n
        index = np.where(randList <= popTotal)
        c = len(randList[index])
        sim_zoneDic[zone].c = c
        randList = np.delete(randList, index)

    # 혹시 남은 지역이 있는 경우 마지막 지역으로
    if len(randList) > 0:
        zone = orgZone_list[-1]
        c = len(randList)
        sim_zoneDic[zone].c = c


    # 첫 지역 산출
    sim_fstZone, sim_fstCent, sim_fstRadius, sim_fstLR, sim_fstNearZone_list = scan(sim_zoneDic, orgZone_list)
    fst_sim_LR.append(sim_fstLR)

    # 처음 찾아진 지역을 제외한 지역 리스트 구축
    sndZone_list = []
    for zone in orgZone_list:
        if sim_fstNearZone_list.count(zone) == 0:
            sndZone_list.append(zone)

    # 두번째 지역 산출
    sim_sndZone, sim_sndCent, sim_sndRadius, sim_sndLR, sim_sndNearZone_list = scan(sim_zoneDic, sndZone_list)
    snd_sim_LR.append(sim_sndLR)

    # 두번째 찾아진 지역을 제외한 지역 리스트 구축
    trdZone_list = []
    for zone in sndZone_list:
        if sim_sndNearZone_list.count(zone) == 0:
            trdZone_list.append(zone)

    # 세번째 지역 산출
    sim_trdZone, sim_trdCent, sim_trdRadius, sim_trdLR, sim_trdNearZone_list = scan(sim_zoneDic, trdZone_list)
    trd_sim_LR.append(sim_trdLR)


#########################
# Calculate p-value
fst_sim_LR.sort()
snd_sim_LR.sort()
trd_sim_LR.sort()

fst_pos = bisect_right(fst_sim_LR, fstLR)
fst_p = (1.0 - (float(fst_pos) / float(NUM_SIMULATION+1)))

snd_pos = bisect_right(snd_sim_LR, sndLR)
snd_p = (1.0 - (float(snd_pos) / float(NUM_SIMULATION+1)))

trd_pos = bisect_right(trd_sim_LR, trdLR)
trd_p = (1.0 - (float(trd_pos) / float(NUM_SIMULATION+1)))

resString = ("1st p-value:%.3f, 2nd p-value:%.3f, 3rd p-value:%.3f" % (fst_p, snd_p, trd_p))
print (resString)
iface.messageBar().pushMessage("[Spatial Scan Result] ", resString)
