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

from pysal import W, Moran
import numpy as np
import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *

# 전역변수 설정
NEIGHBOR_DIST = 100
VALUE_FIELD = "X"
NAME_FIELD =  "Y"
SIG_LEVEL = 0.1
WEIGHT_MODE = "QUEEN" #DIST, QUEEN, ROOK

print u"[Moran's I 테스트] 인접판단기준: %f" % NEIGHBOR_DIST

layer = qgis.utils.iface.activeLayer()
if not layer:
    gErrorMsg = u"레이어를 먼저 선택해야 합니다."
    raise UserWarning # 종료

layerName = layer.name()
layerType = layer.geometryType();
crs = layer.crs()

# ID 리스트 확보
IDs = layer.allFeatureIds()

# Weight
neighbors  = {}
weights = {}

# Data
dataList = []

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"공간상관관계 계산중...")
progress = QProgressBar()
progress.setMaximum(len(IDs))
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

for i, iID in enumerate(IDs):
    iFeature = layer.getFeatures(QgsFeatureRequest(iID)).next()
    iGeom = iFeature.geometry()
    iRowNeighbors = []
    iRowWeights = []

    progress.setValue(i)

    for jID in IDs:
        jFeature = layer.getFeatures(QgsFeatureRequest(jID)).next()
        jGeom = jFeature.geometry()

        if iID == jID: # 같은 지역인 경우
            dist = 0.0
        else:
            if WEIGHT_MODE == "DIST":
                dist = iGeom.distance(jGeom)
                if dist != 0.0 and dist <= NEIGHBOR_DIST:
                    iRowNeighbors.append(jID)
                    iRowWeights.append(1)
                    #iRowWeights.append(1.0/dist)

            elif WEIGHT_MODE == "QUEEN":
                if iGeom.touches(jGeom):
                    iRowNeighbors.append(jID)
                    iRowWeights.append(1)

            elif WEIGHT_MODE == "ROOK":
                pass # 방법을 모르겠다!!!
            else:
                gErrorMsg = u"잘못된 WEIGHT_MODE: "+WEIGHT_MODE
                raise UserWarning

    neighbors[iID] = iRowNeighbors
    weights[iID] = iRowWeights
    val = iFeature[VALUE_FIELD]
    dataList.append(val)

# Progress 제거
iface.messageBar().clearWidgets()

w = W(neighbors, weights)
print w.full()

y = np.array(dataList)
#print y

# Moran's I 계산
mi = Moran(y, w)

# 결과 출력
moran_i_res = u"Moran's I: {0:.2f}, z_norm: {1:.2f}, p_norm: {2:.5f}".format(mi.I, mi.z_norm, mi.p_norm)
