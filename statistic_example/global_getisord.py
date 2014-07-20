# coding=utf-8
"""
/***************************************************************************
Name                 : Global GetisOrd
Description          : Global Getis-Ord's G Statistic - Spatial Clustering
Date                 : 2014.07.19
copyright            : (C) 2014 by BJ Jang of Gaia3D.com
email                : jangbi882@gmail.com
Sample Data          : 인구분포.shp
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

from pysal import W, G
import numpy as np
import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *
import matplotlib.pyplot as plt


# 전역변수 설정
FROM_DIST = 2500
TO_DIST = 25000
BY_DIST = 2500
NAME_FIELD = "SGG"
VALUE_FIELD = u"노인비율"
CRITICAL_Z = 1.96

##########################
# 레이어에서 정보 추출

# 레이어 선택
oLayer = iface.activeLayer()
if not oLayer:
    raise UserWarning(u"레이어를 먼저 선택해야 합니다.")  # 종료

layerName = oLayer.name()
layerType = oLayer.geometryType()
crs = oLayer.crs()

# ID 리스트 확보
oIDs = oLayer.allFeatureIds()

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"레이어 정보 수집중...")
progress = QProgressBar()
progress.setMaximum(len(oIDs))
progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# centroid,value(y),name 모으기
centroidList = []
dataList = []
nameList = []
for i, oID in enumerate(oIDs):
    progress.setValue(i)

    iFeature = oLayer.getFeatures(QgsFeatureRequest(oID)).next()
    iGeom = iFeature.geometry().centroid()
    centroidList.append(iGeom)
    data = iFeature[VALUE_FIELD]
    dataList.append(data)
    name = iFeature[NAME_FIELD]
    nameList.append(name)

# 통계 대상 값 수집
y = np.array(dataList)


#######################
# FROM_DIST에서 TO_DIST까지 BY_DIST 씩 거리 증가하며 Getis-Ord's G 구하기

# 전체 몇 번 돌아가야 하는지 계산
totalCnt, mod = divmod((TO_DIST-FROM_DIST), BY_DIST)
totalCnt += 1
progress.setMaximum(totalCnt)

# 거리를 늘려가며 반복하며 Getis-Ord's G 계산
ggResults = {}
for i, testDist in enumerate(range(FROM_DIST, (TO_DIST+BY_DIST), BY_DIST)):
    progress.setValue(i)

    # Weight Matrix 계산 위한 정보 수집
    neighbors = {}
    weights = {}
    for iID, iCent in zip(oIDs, centroidList):
        iRowNeighbors = []
        iRowWeights = []
        for jID, jCent in zip(oIDs, centroidList):
            # 동일 지역인 경우 제외
            if iID == jID:
                continue
            # 기준거리 이내인 경우 인접한 것으로 기록
            dist = iCent.distance(jCent)
            if dist <= testDist:
                iRowNeighbors.append(jID)
                iRowWeights.append(1)
        # iID 지역에 대한 인접 지역 및 가중치 기록
        neighbors[iID] = iRowNeighbors
        weights[iID] = iRowWeights

    # 인접지역과 가중치를 기준으로 현재 testDist의 Weight Matrix 계산
    w = W(neighbors, weights)
    w.transform = "B"

    # 현재 testDist의 Moran's I 계산
    gg = G(y, w)

    # 결과 저장
    ggResults[testDist] = gg

# Progress 제거
iface.messageBar().clearWidgets()


###########################
# 거리에 따른 z 값 변화 그래프

# 그래프를 위한 값 모으기
distList = ggResults.keys()
distList.sort()
zList = []
for dist in distList:
    zList.append(ggResults[dist].z_norm)

# 이미 그래프 창이 있더라도 닫기
plt.close()

# 값 그리기
plt.plot(distList, zList, "b")
# 축 정보
plt.xlabel("Distance = d")
plt.ylabel("Z[d]")
# 유효값 기준선
plt.plot([distList[0], distList[-1]], [CRITICAL_Z, CRITICAL_Z], "r")
plt.text(distList[-1], CRITICAL_Z, " Critical\n Z-Value\n %.3f" % CRITICAL_Z, color="r")
# 제목
plt.title("G[d]s over a range of search distance")
# 그래프 띄우기
plt.show()
