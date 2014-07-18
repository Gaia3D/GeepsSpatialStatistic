# coding=utf-8
# Sample Data: burkitt.shp
if not iface:
    iface = qgis.gui.QgisInterface()

import qgis
from qgis.core import *
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *
import math
import numpy as np
import time
from bisect import bisect_right

# 전역변수 설정
TIME_COLUMN = "DATE"
NUM_SIMULATION = 999
RANDOM_SEED = int(time.time())
BASE_DS = None
BASE_DT = None

N_ST = None
N_sim = []

# 소스 레이어 선택
oLayer = qgis.utils.iface.activeLayer()
if not oLayer:
    gErrorMsg = u"레이어를 먼저 선택해야 합니다."
    raise UserWarning # 종료

# TODO: DATE 컬럼이 시간 형식인지 확인

layerName = oLayer.name()
layerType = oLayer.geometryType();
crs = oLayer.crs()

# ID 리스트 확보
oIDs = oLayer.allFeatureIds()

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"자료 정보 수집중...")
progress = QProgressBar()
progress.setMaximum(len(oIDs))
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# centroid, date 모으기
centroidList = []
dateList = []
for i, oID in enumerate(oIDs):
    progress.setValue(i)

    iFeature = oLayer.getFeatures(QgsFeatureRequest(oID)).next()
    iGeom = iFeature.geometry().centroid()
    centroidList.append(iGeom)

    dateObj = iFeature[TIME_COLUMN]
    dateList.append(dateObj)

# detect date, dist range
maxDs = None
maxDt = None
for i, iCent, iDate in zip(range(len(centroidList)), centroidList, dateList):
    for j, jCent, jDate in zip(range(len(centroidList)), centroidList, dateList):
        if i == j:
            continue
        ds = iCent.distance(jCent)
        dt = abs(iDate.daysTo(jDate))

        if maxDs is None or ds > maxDs:
            maxDs = ds
        if maxDt is None or dt > maxDt:
            maxDt = dt

# ds, dt setting
if BASE_DS is None:
    base_ds = maxDs / 20.0
else:
    base_ds = BASE_DS
if BASE_DT is None:
    base_dt = int(math.ceil(maxDt / 20.0))
else:
    base_dt = BASE_DT

# calculate N(ST)
N_ST_double = 0
knoxCentroidList = []
for i, iCent, iDate in zip(range(len(centroidList)), centroidList, dateList):
    for j, jCent, jDate in zip(range(len(centroidList)), centroidList, dateList):
        if i == j:
            continue
        ds = iCent.distance(jCent)
        dt = abs(iDate.daysTo(jDate))

        if ds <= base_ds:
            S_ij = 1
        else:
            S_ij = 0
        if dt <= base_dt:
            T_ij = 1
        else:
            T_ij = 0
        if S_ij*T_ij == 1:
            knoxCentroidList.append(jCent)
        N_ST_double += S_ij * T_ij

N_ST = int(N_ST_double / 2)
print ("N(ST): %d" % N_ST)

N_sim.append(N_ST)

# Progress 제거
iface.messageBar().clearWidgets()

#########################
# Result Layer

# Memory Layer 생성
#  "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", or "MultiPolygon".
tLayerOption = "{0}?crs={1}&index=yes".format("Point", crs.authid())
tLayer = QgsVectorLayer(tLayerOption, "Knox_"+layerName, "memory")
tProvider = tLayer.dataProvider()
tLayer.startEditing()

for centroid in knoxCentroidList:
    tFeature = QgsFeature(tProvider.fields())
    tFeature.setGeometry(QgsGeometry.fromPoint(centroid.vertexAt(0)))
    tProvider.addFeatures([tFeature])
tLayer.commitChanges()
tLayer.updateExtents()
QgsMapLayerRegistry.instance().addMapLayer(tLayer)
qgis.utils.iface.mapCanvas().refresh()


#######
# Monte-Carlo Simulation

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"Monte-Carlo Simulation...")
progress = QProgressBar()
progress.setMaximum(NUM_SIMULATION)
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

np.random.seed(RANDOM_SEED)
for iSim in range(NUM_SIMULATION):
    progress.setValue(iSim)

    # date shuffle
    simDateList = np.random.permutation(dateList)
    simCentList = np.array(centroidList)
    QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    # calculate N(ST)
    N_ST_double = 0
    for i, iCent, iDate in zip(range(len(centroidList)), simCentList, simDateList):
        for j, jCent, jDate in zip(range(len(centroidList)), simCentList, simDateList):
            if i == j:
                continue
            ds = iCent.distance(jCent)
            dt = abs(iDate.daysTo(jDate))

            if ds <= base_ds:
                S_ij = 1
            else:
                S_ij = 0
            if dt <= base_dt:
                T_ij = 1
            else:
                T_ij = 0
            N_ST_double += S_ij * T_ij
    N_sim.append(int(N_ST_double/2))
    #print ("Sim_N(ST): %d" % (N_ST_double/2))

#######
# sort results
N_sim.sort()
print(N_sim)

# calculate p-value
pos = bisect_right(N_sim, N_ST)
print ("pos: %d" % pos)
p = (1.0 - (float(pos) / float(NUM_SIMULATION+1))) * 100.0
print ("p: %.5f%%" % p)

# Progress 제거
iface.messageBar().clearWidgets()

