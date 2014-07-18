# coding=utf-8
# Sample Data: juvenile.shp
if not iface:
    iface = qgis.gui.QgisInterface()

import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *


oLayer = qgis.utils.iface.activeLayer()
if not oLayer:
    gErrorMsg = u"레이어를 먼저 선택해야 합니다."
    raise UserWarning # 종료

layerName = oLayer.name()
layerType = oLayer.geometryType();
crs = oLayer.crs()

if layerType != QGis.Point:
    gErrorMsg =  u"Point 형태의 레이어만 분석 가능합니다."
    raise UserWarning # 종료

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

# Memory Layer 생성
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
qgis.utils.iface.mapCanvas().refresh()

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

iface.messageBar().pushMessage("Complete", "R: %f, Z_r: %f" % (R, Z_r))
print("R: %f, Z_r: %f" % (R, Z_r))
