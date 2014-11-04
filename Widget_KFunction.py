# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import numpy as np
from qgis.core import *
from Utility import *
from gui.ui_form_k_function import Ui_Form_Parameter as Ui_Form
import time
import math
from bisect import bisect_right
import matplotlib.pyplot as plt

# K Value normalize function
k2l = lambda k, h: (k/math.pi)**0.5 - h

class Widget_KFunction(QWidget, Ui_Form):
    title = "K-Function"
    objectName = "objKFunction"

    # 분석결과 저장
    sourceRegions = {}

    # 전역변수 설정
    __crrLayerName = None

    NUM_SIMULATION = 99
    FROM_H = 10
    TO_H = 20
    BY_H = 1
    RANDOM_SEED = 0
    K_h = 0

    xList = []
    L_obs = []
    L_05 = []
    L_50 = []
    L_95 = []

    K_obs = []
    K_05 = []
    K_50 = []
    K_95 = []

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
        self.connect(self.btnShowGraph, SIGNAL("clicked()"), self.__onShowGraph)

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

        try:
            self.FROM_H = long(self.edtFromH.text())
        except:
            alert(u"From H 값이 잘못되었습니다.")
            self.edtFromH.setText("{0}".format(self.FROM_H))
            return

        try:
            self.TO_H = long(self.edtToH.text())
        except:
            alert(u"To H 값이 잘못되었습니다.")
            self.edtToH.setText("{0}".format(self.TO_H))
            return

        try:
            self.BY_H = long(self.edtByH.text())
        except:
            alert(u"By H 값이 잘못되었습니다.")
            self.edtByH.setText("{0}".format(self.By_H))
            return

        if self.FROM_H >= self.TO_H:
            alert(u"From H는 To H 값보다 작아야 합니다.")
            return

        if self.BY_H >= (self.TO_H-self.FROM_H):
            alert(u"By H가 To H와 From H의 차보다 작아야 합니다.")
            return

        if self.FROM_H <=0 or self.TO_H<=0 or self.BY_H<=0:
            alert(u"H 값은 모두 0보다 커야 합니다.")
            return

        try:
            self.NUM_SIMULATION = long(self.edtNumSimul.text())
        except:
            alert(u"Number of monte carlo simulation이 잘못되었습니다.")
            self.edtNumSimul.setText("{0}".format(self.NUM_SIMULATION))
            return


        if self.__runNearestNeighbor(srcLayer):
            alert(u"K-function 분석 완료")
        else:
            alert(u"K-function 분석 실패")

    ### 내부 유틸 함수
    # TODO: 실제 K-function 수행
    def __runNearestNeighbor(self, srcLayer):

        try:
            # Centroid 모으기
            oIdList, centroidList = self.__collectCentroid(srcLayer)

            if len(centroidList) == 0:
                raise Exception("레이어에 객체가 없습니다.")

            # 결과 표시용 레이어 만들기
            flagConvexHull = self.chkConvexHull.checkState() & Qt.Checked

            resultLayer = None
            if flagConvexHull:
                resultLayer = self.__createResultLayer(srcLayer)

            # ConvexHull 계산
            convexHull = self.__calcConvexHull(centroidList, resultLayer, flagConvexHull)

            # Extent
            extent = srcLayer.extent()

            # 몬테카를로 시뮬레이션 통해 값 검증
            self.__monteCarloKFunction(self.NUM_SIMULATION, self.TO_H, self.FROM_H, self.BY_H, extent, centroidList, convexHull)

        except Exception as e:
            alert(e.message)
            return False

        return True

    def __monteCarloKFunction(self, numSim, toH, fromH, byH, extent, centroidList, convexHull):
        randomSeed = int(time.time())
        np.random.seed(randomSeed)

        # Extent
        ext_w = extent.width()
        ext_h = extent.height()
        ext_ox = extent.xMinimum()
        ext_oy = extent.yMinimum()

        # density
        N = len(centroidList)
        R = convexHull.area()

        lamda = N / R  # force typo of lambda

        totNumCalc, res = divmod(toH - fromH, byH)
        totNumCalc += 1

        self.xList = []
        self.L_obs = []
        self.L_05 = []
        self.L_50 = []
        self.L_95 = []

        self.K_obs = []
        self.K_05 = []
        self.K_50 = []
        self.K_95 = []

        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.progressBar.setVisible(True)
        self.lbl_log.setVisible(True)

        self.txtResult.clear()

        crrCalc = 0
        h = fromH
        while (h <= toH):
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
            self.K_obs.append(K_h)
            self.L_obs.append(L_h)

            self.txtResult.appendPlainText("\nK(%.1f): %f, E[]: %f, L(h):%f" % (h, K_h, E, L_h))

            K_sim.append(K_h)

            #######
            # Monte-Carlo Simulation

            # Progress 생성
            crrCalc += 1

            self.lbl_log.setText(u"Monte-Carlo Simulation of K(%.1f)(%d/%d)..." % (h, crrCalc, totNumCalc))
            self.progressBar.setMaximum(numSim)

            for iSim in range(numSim):
                self.progressBar.setValue(iSim)
                forceGuiUpdate()

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

            #######
            # sort results
            K_sim.sort()

            index_05 = int((numSim+1)*0.05)
            index_50 = int((numSim+1)*0.50)
            index_95 = int((numSim+1)*0.95)

            self.K_05.append(K_sim[index_05])
            self.K_50.append(K_sim[index_50])
            self.K_95.append(K_sim[index_95])

            self.L_05.append(k2l(K_sim[index_05], h))
            self.L_50.append(k2l(K_sim[index_50], h))
            self.L_95.append(k2l(K_sim[index_95], h))

            # calculate p-value
            pos = bisect_right(K_sim, K_h)
            p = (1.0 - (float(pos) / float(numSim+1))) * 100.0

            self.txtResult.appendPlainText(u"K ==> 05%%:%f, 50%%:%f, 95%%:%f, Obs:%f, p: %.5f%%"
                   % (K_sim[index_05], K_sim[index_50], K_sim[index_95], K_h, p)
            )

            h += byH
            self.xList.append(h)

        self.lbl_log.hide()
        self.progressBar.hide()

        self.__onShowGraph()


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
        resultLayerName = "KFunc_"+orgLayer.name()

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
            symbol.setColor(QColor(0,255,0))
            category2 = QgsRendererCategoryV2("ConvexHull", symbol, "ConvexHull")

            categories = [category2]
            renderer = QgsCategorizedSymbolRendererV2("Group", categories)
            tLayer.setRendererV2(renderer)

            tLayer.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(tLayer)
            self.__canvas.refresh()

        return tLayer


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

        return convexHull

    def __onShowGraph(self):
        plt.close()

        if len(self.xList) == 0 or len(self.L_05) == 0 or len(self.L_50) == 0 or len(self.L_95) == 0:
            alert(u"먼저 [RUN]을 눌러 분석을 수행해야 합니다.")
            return

        plt.plot(self.xList, self.L_05, "b", linestyle="--")
        plt.plot(self.xList, self.L_50, "b", linestyle=":")
        plt.plot(self.xList, self.L_95, "b")

        plt.plot(self.xList, self.L_obs, "r")
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