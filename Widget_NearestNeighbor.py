# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import numpy as np
from qgis.core import *
from Utility import *
from gui.ui_form_nearest_neighbor import Ui_Form_Parameter as Ui_Form


class Widget_NearestNeighbor(QWidget, Ui_Form):
    title = "Nearest Neighbor Statistic"
    objectName = "objNearestNeighbor"

    # 분석결과 저장
    sourceRegions = {}

    # 현재 선택 저장
    __crrLayerName = None
    __srcLayer = None
    __crrIdColumn = None
    __crrTgtColumn = None
    __resultLayer = None

    ### 생성자 및 소멸자
    #생성자
    def __init__(self, iface, dockwidget):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)
        self.progressBar.setVisible(False)
        self.lbl_log.setVisible(False)

        self.__iface = iface
        self.__canvas = iface.mapCanvas()
        self.__dockwidget = dockwidget
        self.__connectAction()

    # 소멸자
    def __del__(self):
        self.disconnectGlobalSignal()

    ### 외부용 함수
    # 위젯이 소멸될 때 전역 이벤트 리스터 연결제거
    def disconnectGlobalSignal(self):
        self.disconnect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)

    # QGIS 레이어 리스트 갱신을 UI에
    def updateGuiLayerList(self):
        layers = self.__canvas.layers()
        layerNameList = []
        bCrrLayerFound = False
        iCrrLayer = 0
        for layer in layers:
            # 벡터가 아닌 레이어 무시
            if layer.type() != QgsMapLayer.VectorLayer:
                continue

            layerName = layer.name()
            layerNameList.append(layerName)
            if (layerName == self.__crrLayerName):
                self.__crrLayerName = layerName
                bCrrLayerFound = True
            if (not bCrrLayerFound):
                iCrrLayer += 1

        self.cmbLayer.clear()
        self.cmbLayer.addItems(layerNameList)


    ### UI 동작처리
    # UI에 이벤트 핸들러 부착
    def __connectAction(self):
        self.connect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.connect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)
        self.connect(self.btnRun, SIGNAL("clicked()"), self.__onRun)

    # UI 동작 정의
    # QGIS의 레이어가 변경된 때
    def __onCanvasLayersChanged(self):
        self.updateGuiLayerList()

    # 위젯의 가시성 변화 시
    def __signal_DocWidget_visibilityChanged(self, visible):
        #self.__resetMaker()
        pass

    # Run 버튼 클릭시: 실행에 필요한 조건이 다 입력되었는지 확인
    def __onRun(self):
        ### 입력 데이터 검사
        # 선택된 레이어 이름 확보
        layerName = self.cmbLayer.currentText()

        if (not layerName) or (layerName == ""):
            alert(u"분석할 레이어를 선택하셔야 합니다.")
            return

        # 존재하는 레이어인지 확인
        srcLayer = None
        for layer in self.__canvas.layers():
            if (layer.name() == layerName) and (layer.type() == QgsMapLayer.VectorLayer):
                srcLayer = layer
                break

        if not srcLayer:
            alert(u"선택된 레이어가 없습니다.")
            return

        if self.__runNearestNeighbor(srcLayer):
            alert(u"Nearest Neighbor Statistic 분석 완료")
        else:
            alert(u"Nearest Neighbor Statistic 분석 실패")

    ### 내부 유틸 함수
    # TODO: 실제 Nearest Neighbor Statistic 수행
    def __runNearestNeighbor(self, srcLayer):

        try:
            # Centroid 모으기
            oIdList, centroidList = self.__collectCentroid(srcLayer)

            if len(centroidList) == 0:
                raise Exception("레이어에 객체가 없습니다.")

            # 결과 표시용 레이어 만들기
            flagConvexHull = self.chkConvexHull.checkState() & Qt.Checked
            flagNearestLine = self.chkNearestLine.checkState() & Qt.Checked

            resultLayer = None
            if flagConvexHull or flagNearestLine:
                resultLayer = self.__createResultLayer(srcLayer)

            # 최근린점 찾기
            sumNearDist = self.__calcNearest(oIdList, centroidList, resultLayer, flagNearestLine)

            # ConvexHull 계산
            convexArea = self.__calcConvexHull(centroidList, resultLayer, flagConvexHull)

            # 통계량 계산
            extent = srcLayer.extent()
            A = convexArea
            N = len(oIdList)
            ro = N / A
            r_exp = 1 / (2*(ro**0.5))
            #r_var = 0.26 / ((N*ro)**0.5)
            r_var = (4-3.14)/(4*3.14*ro*N)#0.26 / ((N*ro)**0.5)
            r_obs = sumNearDist / N
            R = r_obs / r_exp
            #Z_r = (r_obs - r_exp) / (r_var**0.5)
            Z_r = 3.826*(r_obs - r_exp) * (ro*N)**0.5

            self.__displayResult(A, N, ro, r_exp, r_var, r_obs, R, Z_r)

        except Exception as e:
            alert(e.message)
            return False

        return True


    # Centroid 모으기
    def __collectCentroid(self, srcLayer):
        # ID 리스트 확보
        ids = srcLayer.allFeatureIds()

        # 진행상황 표시
        self.lbl_log.setText(u"지역 정보 모으는 중...")
        self.lbl_log.setVisible(True)
        self.progressBar.setMaximum(len(ids))
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.lbl_log.setVisible(True)
        self.progressBar.setVisible(True)

        # Centroid 수집
        centroidList = []
        for i, iID in enumerate(ids):
            self.progressBar.setValue(i)
            forceGuiUpdate()

            iFeature = srcLayer.getFeatures(QgsFeatureRequest(iID)).next()
            iGeom = iFeature.geometry().centroid()
            centroidList.append(iGeom)

        self.lbl_log.setVisible(False)
        self.progressBar.setVisible(False)

        return ids, centroidList


    # Create Result Layer
    def __createResultLayer(self, orgLayer):
        resultLayerName = "Nearest_"+orgLayer.name()

        # 결과 레이어 이미 있는지 확인
        tLayer = None
        layers = self.__canvas.layers()
        for testLayer in layers:
            name = testLayer.name()
            if name != resultLayerName:
                continue
            if testLayer.type() != QgsMapLayer.VectorLayer:
                continue
            # TODO: 메모리 레이어인지 검증
            #testLayer.dataProvider()
            tLayer = testLayer

            # 기존 결과 레이어 객체 모두 지우기
            caps = tLayer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.DeleteFeatures:
                ids = tLayer.allFeatureIds()
                res = tLayer.dataProvider().deleteFeatures(ids)
            break

        if not tLayer:
            crs = orgLayer.crs()
            tLayerOption = "{0}?crs={1}&index=yes".format("LineString", crs.authid())
            tLayer = QgsVectorLayer(tLayerOption, resultLayerName, "memory")
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

            tLayer.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(tLayer)
            self.__canvas.refresh()

        return tLayer


    # 최근린점 찾기/연결선 그리기
    def __calcNearest(self, oIdList, centroidList, resultLayer, flagNearestLine):
        sumNearDist = 0.0

        # 진행상황 표시
        self.lbl_log.setText(u"연결성 계산 중...")
        self.lbl_log.setVisible(True)
        self.progressBar.setMaximum(len(oIdList))
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.lbl_log.setVisible(True)
        self.progressBar.setVisible(True)

        i = 0
        for iID, iGeom in zip(oIdList, centroidList):
            self.progressBar.setValue(i)
            forceGuiUpdate()
            i += 1

            minDist = None
            nearID = None
            nearGeom = None
            for jID, jGeom in zip(oIdList, centroidList):
                if iID == jID:
                    continue
                dist = iGeom.distance(jGeom)
                if minDist is None or dist < minDist:
                    minDist = dist
                    nearID = jID
                    nearGeom = jGeom
            if not nearGeom is None:
                sumNearDist += minDist
                if resultLayer and flagNearestLine:
                    resultLayer.startEditing()
                    tProvider = resultLayer.dataProvider()

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

                    resultLayer.commitChanges()
                    resultLayer.updateExtents()

                    # 지도화면 갱신
                    self.__canvas.refresh()

        self.lbl_log.setVisible(False)
        self.progressBar.setVisible(False)

        return sumNearDist


    # Convex Hull
    def __calcConvexHull(self, centroidList, resultLayer, flagConvexHull):
        multiPoint = [centroid.vertexAt(0) for centroid in centroidList]
        multiPointGeom = QgsGeometry.fromMultiPoint(multiPoint)
        convexHull = multiPointGeom.convexHull()

        if resultLayer and flagConvexHull:
            resultLayer.startEditing()
            tProvider = resultLayer.dataProvider()

            tFeature = QgsFeature(tProvider.fields())
            tFeature.setGeometry(QgsGeometry.fromPolyline(convexHull.asPolygon()[0]))
            tFeature.setAttribute(3, "ConvexHull")
            tProvider.addFeatures([tFeature])

            # 메모리 레이어에 기록
            resultLayer.commitChanges()
            resultLayer.updateExtents()

            QgsMapLayerRegistry.instance().addMapLayer(resultLayer)

            # 메모리 레이어에 기록
            resultLayer.commitChanges()
            resultLayer.updateExtents()

            # 지도화면 갱신
            self.__canvas.refresh()

        return convexHull.area()

    # TODO: 결과표시
    def __displayResult(self, A, N, ro, r_exp, r_var, r_obs, R, Z_r):
        resString = u"[결과요약]\n"
        resString += u"- R:\t{0}\n".format(R)
        resString += u"- Z_r:\t{0}\n".format(Z_r)
        resString += u"\n[기초정보]\n"
        resString += u"- A:\t{0}\n".format(A)
        resString += u"- N:\t{0}\n".format(N)
        resString += u"- ro:\t{0}\n".format(ro)
        resString += u"- r_exp:\t{0}\n".format(r_exp)
        resString += u"- r_var:\t{0}\n".format(r_var)
        resString += u"- r_obs:\t{0}\n".format(r_obs)

        self.txtResult.setPlainText(resString)