# -*- coding: utf-8 -*-
import qgis
from qgis.core import *
from qgis.gui import QgsMessageBar
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import *
from Utility import *
import math

class Process_NearestNeighbor:
    prefix = "Nearest_"
    gErrorMsg = ""
    R = None
    Z_r = None

    def __init__(self, iface):
        self.iface = iface

    def __del__(self):
        pass

    def run(self, layerName = None):
        try:
            oLayer = qgis.utils.iface.activeLayer()
            if not oLayer:
                gErrorMsg = u"레이어를 먼저 선택해야 합니다."
                raise UserWarning # 종료

            layerName = oLayer.name()
            layerType = oLayer.geometryType();
            crs = oLayer.crs()

#            if layerType != QGis.Point:
#                gErrorMsg =  u"Point 형태의 레이어만 분석 가능합니다."
#                raise UserWarning # 종료

            # ID 리스트 확보
            oIDs = oLayer.allFeatureIds()

            # Progress 생성
            progressMessageBar = self.iface.messageBar().createMessage(u"자료 정보 수집중...")
            progress = QProgressBar()
            progress.setMaximum(len(oIDs))
            progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            progressMessageBar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)

            # centroid 모으기
            centroidList = []
            for i, oID in enumerate(oIDs):
                progress.setValue(i)

                iFeature = oLayer.getFeatures(QgsFeatureRequest(oID)).next()
                iGeom = iFeature.geometry().centroid()
                centroidList.append(iGeom)

            # Progress 제거
            self.iface.messageBar().clearWidgets()

            # Memory Layer 생성
            #  "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", or "MultiPolygon".
            tLayerOption = "{0}?crs={1}&index=yes".format("LineString", crs.authid())
            tLayer = QgsVectorLayer(tLayerOption, self.prefix+layerName, "memory")
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
            r_var = (4-math.pi)/(4*math.pi*ro*N)#0.26 / ((N*ro)**0.5)
            r_obs = sumNearDist / N
            self.R = r_obs / r_exp
            #Z_r = (r_obs - r_exp) / (r_var**0.5)
            self.Z_r = 3.826*(r_obs - r_exp) * (ro*N)**0.5

            alert("R: %f, Z_r: %f" % (self.R, self.Z_r))
            print("R: %f, Z_r: %f" % (self.R, self.Z_r))

        except KeyError, e:
            alert(str(e) + u" 필드를 찾지 못함", QMessageBox.Warning)

        # 오류 메시지 표시
        except UserWarning:
            alert(gErrorMsg, QMessageBox.Warning)
