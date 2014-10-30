# coding=utf-8
"""
/***************************************************************************
Name                 : K-function
Description          : K-function - Spatial Clustering
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
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *
import math
import numpy as np
import time
from bisect import bisect_right
import matplotlib.pyplot as plt


# K Value normalize
k2l = lambda k, h: (k/math.pi)**0.5 - h

# 전역변수 설정
NUM_SIMULATION = 99
FROM_H = 10
TO_H = 20
BY_H = 1
RANDOM_SEED = int(time.time())
K_h = 0

np.random.seed(RANDOM_SEED)


#################################
# 소스 레이어 선택
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
progressMessageBar = iface.messageBar().createMessage(u"자료 정보 수집중...")
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
# calculate Area and density

# ConvexHull
multiPoint = [centroid.vertexAt(0) for centroid in centroidList]
multiPointGeom = QgsGeometry.fromMultiPoint(multiPoint)
convexHull = multiPointGeom.convexHull()

# Extent
extent = oLayer.extent()
ext_w = extent.width()
ext_h = extent.height()
ext_ox = extent.xMinimum()
ext_oy = extent.yMinimum()

# density
N = len(centroidList)
R = convexHull.area()
lamda = N / R  # force typo of lambda


##########################
# Multiple K-function
totNumCalc, res = divmod(TO_H - FROM_H, BY_H)
totNumCalc += 1

xList = []
L_obs = []
L_05 = []
L_50 = []
L_95 = []

K_obs = []
K_05 = []
K_50 = []
K_95 = []

crrCalc = 0
h = FROM_H
while (h <= TO_H):
    # calculate K(h)
    K_sim = []
    sum_Ih = 0
    for i, iCent in enumerate(centroidList):
        for j, jCent in enumerate(centroidList):
            if i == j:
                continue
            ds = iCent.distance(jCent)

            if ds <= h:
                sum_Ih += 1
    K_h = (1/lamda) * (sum_Ih/N)
    E = math.pi*(h**2)
    L_h = k2l(K_h, h)
    K_obs.append(K_h)
    L_obs.append(L_h)
    print ("K(%.1f): %f, E[]: %f, L(h):%f" % (h, K_h, E, L_h))

    K_sim.append(K_h)

    #######
    # Monte-Carlo Simulation

    # Progress 생성
    crrCalc += 1
    progressMessageBar = iface.messageBar().createMessage(
        u"Monte-Carlo Simulation of K(%.1f)(%d/%d)..."
        % (h, crrCalc, totNumCalc)
    )
    progress = QProgressBar()
    progress.setMaximum(NUM_SIMULATION)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, iface.messageBar().INFO)

    for iSim in range(NUM_SIMULATION):
        progress.setValue(iSim)

        # make random points
        simXList = np.random.rand(N)*ext_w + ext_ox
        simYList = np.random.rand(N)*ext_h + ext_oy

        samplePoint = []
        ii = 0
        while len(samplePoint) < N:
            ii += 1
            randPoint = [QgsPoint(x, y) for x, y in zip(simXList, simYList)]
            for i, point in enumerate(randPoint):
                if convexHull.contains(point):
                    samplePoint.append(point)
                if len(samplePoint) >= N:
                    break

        # for TEST: draw sim points
        if False: # h == FROM_H:
            # Memory Layer 생성
            #  "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", or "MultiPolygon".
            tLayerOption = "{0}?crs={1}&index=yes".format("Point", crs.authid())
            tLayer = QgsVectorLayer(tLayerOption, ("k%d_"%(iSim+1))+layerName, "memory")
            tProvider = tLayer.dataProvider()
            tLayer.startEditing()

            for pnt in samplePoint:
                tFeature = QgsFeature(tProvider.fields())
                tFeature.setGeometry(QgsGeometry.fromPoint(pnt))
                tProvider.addFeatures([tFeature])
            tLayer.commitChanges()
            tLayer.updateExtents()
            QgsMapLayerRegistry.instance().addMapLayer(tLayer)
            iface.mapCanvas().refresh()

        # calculate K(h)
        sum_Ih = 0
        for i, iPnt in enumerate(samplePoint):
            for j, jPnt in enumerate(samplePoint):
                if i == j:
                    continue
                ds = ((iPnt.x()-jPnt.x())**2 + (iPnt.y()-jPnt.y())**2)**0.5

                if ds <= h:
                    sum_Ih += 1
        K_h_sim = (1/lamda) * (sum_Ih/N)
        K_sim.append(K_h_sim)

    # Progress 제거
    iface.messageBar().clearWidgets()

    #######
    # sort results
    K_sim.sort()

    index_05 = int((NUM_SIMULATION+1)*0.05)
    index_50 = int((NUM_SIMULATION+1)*0.50)
    index_95 = int((NUM_SIMULATION+1)*0.95)

    K_05.append(K_sim[index_05])
    K_50.append(K_sim[index_50])
    K_95.append(K_sim[index_95])

    L_05.append(k2l(K_sim[index_05], h))
    L_50.append(k2l(K_sim[index_50], h))
    L_95.append(k2l(K_sim[index_95], h))

    # calculate p-value
    pos = bisect_right(K_sim, K_h)
    p = (1.0 - (float(pos) / float(NUM_SIMULATION+1))) * 100.0

    print ("K ==> 05%%:%f, 50%%:%f, 95%%:%f, Obs:%f, p: %.5f%%"
           % (K_sim[index_05], K_sim[index_50], K_sim[index_95], K_h, p)
    )

    h += BY_H
    xList.append(h)

################
# Graph
plt.close()

plt.plot(xList, L_05, "b", linestyle="--")
plt.plot(xList, L_50, "b", linestyle=":")
plt.plot(xList, L_95, "b")

plt.plot(xList, L_obs, "r")
plt.xlabel("h")
plt.ylabel("L(h)")
'''
plt.plot(xList, K_05, "b", linestyle="--")
plt.plot(xList, K_50, "b", linestyle=":")
plt.plot(xList, K_95, "b")

plt.plot(xList, K_obs, "r")
plt.xlabel("h")
plt.ylabel("K(h)")
'''
plt.show()
