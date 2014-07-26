# coding=utf-8
"""
/***************************************************************************
Name                 : Local Moran
Description          : Local Moran's I Statistic - Spatial Autocorrelation
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

from pysal import W, Moran_Local
import numpy as np
import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import matplotlib.pyplot as plt


# 전역변수 설정
NAME_FIELD = "SGG"
VALUE_FIELD = u"LQ"

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

# Progress 제거
iface.messageBar().clearWidgets()

# 통계 대상 값 수집
y = np.array(dataList)


#######################
# 거리의 역수 기준으로 Local Moran's I 구하기

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
        # 거리 계산
        dist = iCent.distance(jCent)
        if dist <= 0:
            continue
        # weight 를 거리의 역수로 부여
        iRowNeighbors.append(jID)
        iRowWeights.append(1.0 / dist)
    # iID 지역에 대한 인접 지역 및 가중치 기록
    neighbors[iID] = iRowNeighbors
    weights[iID] = iRowWeights

# 거리의 역수를 기준으로 Weight Matrix 계산
w = W(neighbors, weights)

# Local Moran's I 계산
lm = Moran_Local(y, w)


###########################
# Moran scatter chart 그리기

# 이미 그래프 창이 있더라도 닫기
plt.close()
# 값 그리기
plt.scatter(lm.z, lm.Is)
# 4분면선
plt.axvline(0, color="k")
plt.axhline(0, color="k")
# 축 정보
plt.xlabel("z[y(i)]")
plt.ylabel("Local I[i]")
# 제목
plt.title("Moran Scatter Chart")
# 그래프 띄우기
plt.show()


###########################
# 지도에 z 값을 기준으로 색으로 표현

# Create Result Layer
tLayerOption = "{0}?crs={1}&index=yes".format("Polygon", crs.authid())
tLayer = QgsVectorLayer(tLayerOption, "Moran_"+layerName, "memory")
tProvider = tLayer.dataProvider()
tLayer.startEditing()
tProvider.addAttributes([QgsField("id", QVariant.Int),
                         QgsField("y", QVariant.Double),
                         QgsField("z", QVariant.Double),
                         QgsField("symbol", QVariant.Int)
])

# Apply symbol
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(255,0,0))
category1 = QgsRendererCategoryV2(1, symbol, "Very High")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(255,128,0))
category2 = QgsRendererCategoryV2(2, symbol, "High")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(245,196,128))
category3 = QgsRendererCategoryV2(3, symbol, "Moderate(high)")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(254,226,194))
category4 = QgsRendererCategoryV2(4, symbol, "Random(high)")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(193,191,254))
category5 = QgsRendererCategoryV2(5, symbol, "Random(low)")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(128,128,255))
category6 = QgsRendererCategoryV2(6, symbol, "Moderate(low)")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(0,0,255))
category7 = QgsRendererCategoryV2(7, symbol, "Low")
symbol = QgsSymbolV2.defaultSymbol(QGis.Polygon)
symbol.setColor(QColor(0,0,196))
category8 = QgsRendererCategoryV2(8, symbol, "Very Low")

categories = [category1, category2, category3, category4, category5, category6, category7, category8]
renderer = QgsCategorizedSymbolRendererV2("symbol", categories)
tLayer.setRendererV2(renderer)

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"Local Moran's I 결과 표시중...")
progress = QProgressBar()
progress.setMaximum(len(oIDs))
progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# 결과 레이어에 표시
w, ids = lm.w.full()
for id, y, z in zip(ids, lm.y, lm.z_sim):
    iFeature = oLayer.getFeatures(QgsFeatureRequest(id)).next()
    iGeom = iFeature.geometry()

    tFeature = QgsFeature(tProvider.fields())
    tFeature.setGeometry(iGeom)
    tFeature.setAttribute(0, id)
    tFeature.setAttribute(1, float(y))
    tFeature.setAttribute(2, float(z))
    if z >= 2.57:
        tFeature.setAttribute(3, 1)
    elif z >= 1.96:
        tFeature.setAttribute(3, 2)
    elif z >= 1.64:
        tFeature.setAttribute(3, 3)
    elif z >= 0:
        tFeature.setAttribute(3, 4)
    elif z >= -1.64:
        tFeature.setAttribute(3, 5)
    elif z >= -1.96:
        tFeature.setAttribute(3, 6)
    elif z >= -2.75:
        tFeature.setAttribute(3, 7)
    else:
        tFeature.setAttribute(3, 8)
    tProvider.addFeatures([tFeature])

# 메모리 레이어에 기록
tLayer.commitChanges()
tLayer.updateExtents()

QgsMapLayerRegistry.instance().addMapLayer(tLayer)
iface.mapCanvas().refresh()
