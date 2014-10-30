# coding=utf-8
"""
/***************************************************************************
Name                 : Nearest Neighbor Statistic
Description          : Nearest Neighbor Statistic - Spatial Clustering
Date                 : 2014.07.19
copyright            : (C) 2014 by BJ Jang of Gaia3D.com
email                : jangbi882@gmail.com
Sample Data          : Juvenile_Offenders_in_Cardiff.shp
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
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import *
from PyQt4.QtCore import *


#########################
# Collect source data
oLayer = iface.activeLayer()
if not oLayer:
    gErrorMsg = u"레이어를 먼저 선택해야 합니다."
    raise UserWarning # 종료

layerName = oLayer.name()
layerType = oLayer.geometryType();
crs = oLayer.crs()

# ID 리스트 확보
oIDs = oLayer.allFeatureIds()

# Progress 생성
progressMessageBar = iface.messageBar().createMessage(u"공간상관관계 계산중...")
progress = QProgressBar()
progress.setMaximum(len(oIDs))
progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
progressMessageBar.layout().addWidget(progress)
iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

# centroid 모으기
centroidList = []
for i, oID in enumerate(oIDs):
    progress.setValue(i)

    iFeature = oLayer.getFeatures(QgsFeatureRequest(oID)).next()
    iGeom = iFeature.geometry().centroid()
    centroidList.append(iGeom)

# Progress 제거
iface.messageBar().clearWidgets()

############################
# Create Result Layer
#  "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", or "MultiPolygon".
tLayerOption = "{0}?crs={1}&index=yes".format("LineString", crs.authid())
tLayer = QgsVectorLayer(tLayerOption, "Nearest_"+layerName, "memory")
tProvider = tLayer.dataProvider()
tLayer.startEditing()
tProvider.addAttributes([QgsField("iID", QVariant.Int),
                         QgsField("jID", QVariant.Int),
                         QgsField("Dist", QVariant.Double),
                         QgsField("Group", QVariant.String)
])

# Apply symbol
symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(255,0,0))
category1 = QgsRendererCategoryV2("Connection", symbol, "Connection")

symbol = QgsSymbolV2.defaultSymbol(QGis.Line)
symbol.setColor(QColor(0,255,0))
category2 = QgsRendererCategoryV2("ConvexHull", symbol, "ConvexHull")

categories = [category1, category2]
renderer = QgsCategorizedSymbolRendererV2("Group", categories)
tLayer.setRendererV2(renderer)


#########################
# 최근린점 찾기
sumNearDist = 0.0
for iID, iGeom in zip(oIDs, centroidList):
    minDist = None
    nearID = None
    nearGeom = None
    for jID, jGeom in zip(oIDs, centroidList):
        if iID == jID:
            continue
        dist = iGeom.distance(jGeom)
        if minDist is None or dist < minDist:
            minDist = dist
            nearID = jID
            nearGeom = jGeom
    if not nearGeom is None:
        polyline = []
        polyline.append(iGeom.vertexAt(0))
        polyline.append(nearGeom.vertexAt(0))
        tFeature = QgsFeature(tProvider.fields())
        tFeature.setGeometry(QgsGeometry.fromPolyline(polyline))
        tFeature.setAttribute(0, iID)
        tFeature.setAttribute(1, nearID)
        tFeature.setAttribute(2, minDist)
        tFeature.setAttribute(3, "Connection")
        tProvider.addFeatures([tFeature])

        sumNearDist += minDist

########################
# ConvexHull
multiPoint = [centroid.vertexAt(0) for centroid in centroidList]
multiPointGeom = QgsGeometry.fromMultiPoint(multiPoint)
convexHull = multiPointGeom.convexHull()

tFeature = QgsFeature(tProvider.fields())
tFeature.setGeometry(QgsGeometry.fromPolyline(convexHull.asPolygon()[0]))
tFeature.setAttribute(3, "ConvexHull")
tProvider.addFeatures([tFeature])

# 메모리 레이어에 기록
tLayer.commitChanges()
tLayer.updateExtents()

QgsMapLayerRegistry.instance().addMapLayer(tLayer)
iface.mapCanvas().refresh()

##########################
# 통계량 계산
extent = tLayer.extent()
# 면적은 Convexhull로
A = convexHull.area()
N = len(oIDs)
ro = N / A
r_exp = 1 / (2*(ro**0.5))
#r_var = 0.26 / ((N*ro)**0.5)
r_var = (4-3.14)/(4*3.14*ro*N)#0.26 / ((N*ro)**0.5)
r_obs = sumNearDist / N
R = r_obs / r_exp
#Z_r = (r_obs - r_exp) / (r_var**0.5)
Z_r = 3.826*(r_obs - r_exp) * (ro*N)**0.5

resString = ("R: %f, Z_r: %f" % (R, Z_r))
print (resString)
iface.messageBar().pushMessage("[Result] ", resString)
