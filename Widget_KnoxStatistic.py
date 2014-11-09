# -*- coding: utf-8 -*-
from gui.ui_form_knox_statistic import Ui_Form_Parameter as Ui_Form
from Utility import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math
import numpy as np
import time
from bisect import bisect_right

class Widget_KnoxStatistic(QWidget, Ui_Form):
    title = "Knox Statistic"
    objectName = "objKnoxStatistic"

    # 전역변수 설정
    __crrLayerName = None
    __crrTimeColumn = None

    TIME_COLUMN = "DATE"
    NUM_SIMULATION = 999
    RANDOM_SEED = int(time.time())
    BASE_DS = None
    BASE_DT = None

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
        self.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.__onCmbLayerChanged)
        self.connect(self.btnRun, SIGNAL("clicked()"), self.__onRun)

    # UI 동작 정의
    # QGIS의 레이어가 변경된 때
    def __onCanvasLayersChanged(self):
        self.updateGuiLayerList()

    # 위젯의 가시성 변화 시
    def __signal_DocWidget_visibilityChanged(self, visible):
        #self.__resetMaker()
        pass

    def getLayerFromName(self, layerName):
        retLayer = None
        for layer in self.__canvas.layers():
            # 벡터가 아닌 레이어 무시
            if layer.type() != QgsMapLayer.VectorLayer:
                continue
            if (layer.name() == layerName):
                retLayer = layer
        return retLayer

    # 레이어 선택 콤보 변경시
    def __onCmbLayerChanged(self, index):
        layerName = self.cmbLayer.currentText()
        if (layerName != self.__crrLayerName):
            self.__crrLayerName = layerName
            self.__fillLayerColumn(layerName)

    # 선택된 레이어의 컬럼 정보 채우기
    def __fillLayerColumn(self, layerName):
        tgtLayer = self.getLayerFromName(layerName)
        if (not tgtLayer):
            self.cmbTimeColumn.clear()
        else:
            provider = tgtLayer.dataProvider()
            if provider:
                fields = provider.fields()
                fieldNameList = []
                i = 0; idxTimeColumn = 0
                for field in fields:
                    # Time 형식 데이터만 필터링
                    if field.typeName() != "Date":
                        continue

                    fieldName = field.name()
                    fieldNameList.append(fieldName)
                    if fieldName == self.__crrTimeColumn:
                        idxTimeColumn = i
                    i += 1
                self.cmbTimeColumn.clear()
                if len(fieldNameList) == 0:
                    #alert(u"선택된 레이어에 Time 형식의 컬럼이 없습니다.")
                    return
                self.cmbTimeColumn.addItems(fieldNameList)
                self.cmbTimeColumn.setCurrentIndex(idxTimeColumn)


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

        # 시간컬럼 이름 확보
        timeColumnName = self.cmbTimeColumn.currentText();

        if (not timeColumnName) or (timeColumnName == ""):
            alert(u"시간값이 들어 있는 컬럼을 선택하셔야 합니다.")
            return

        timeColumn = srcLayer.dataProvider().fields().field(timeColumnName)
        if not timeColumn:
            alert(u"선택된 컬럼이 없습니다.")
            return

        if timeColumn.typeName() != "Date":
            alert(u"선택된 컬럼이 시간 형식이 아닙니다.")
            alert(timeColumn.typeName())
            return

        try:
            self.BASE_DS = float(self.edtDistBound.text())
        except:
            self.edtDistBound.setText("")
            self.BASE_DS = None

        try:
            self.BASE_DT = long(self.edtTimeBound.text())
        except:
            self.edtTimeBound.setText("")
            self.BASE_DT = None

        try:
            self.NUM_SIMULATION = long(self.edtNumSimul.text())
        except:
            alert(u"Number of monte carlo simulation이 잘못되었습니다.")
            self.edtNumSimul.setText("{0}".format(self.NUM_SIMULATION))
            return

        if self.__runKnoxStatistic(srcLayer, timeColumnName):
            alert(u"Spatial Statistic 분석 완료")
        else:
            alert(u"Spatial Statistic 분석 실패")

    # 실제 수행
    def __runKnoxStatistic(self, srcLayer, timeColumnName):

        try:
            # Data 모으기
            oIdList, centroidList, timeList = self.__collectData(srcLayer, timeColumnName)

            if len(centroidList) == 0:
                raise Exception("레이어에 객체가 없습니다.")

            # 결과 표시용 레이어 만들기
            flagBoundPoint = self.chkBoundPoint.checkState() & Qt.Checked
            flagConvexHull = self.chkConvexHull.checkState() & Qt.Checked

            pointLayer = None
            if flagBoundPoint:
                pointLayer = self.__createPointLayer(srcLayer)

            convexLayer = None
            if flagConvexHull:
                convexLayer = self.__createConvexLayer(srcLayer)

            # ConvexHull 계산
            self.__calcConvexHull(centroidList, convexLayer, flagConvexHull)

            # detect date, dist range
            maxDs = None
            maxDt = None
            for i, iCent, iDate in zip(range(len(centroidList)), centroidList, timeList):
                for j, jCent, jDate in zip(range(len(centroidList)), centroidList, timeList):
                    if i == j:
                        continue
                    ds = iCent.distance(jCent)
                    dt = abs(iDate.daysTo(jDate))

                    if maxDs is None or ds > maxDs:
                        maxDs = ds
                    if maxDt is None or dt > maxDt:
                        maxDt = dt

            # ds, dt setting
            if self.BASE_DS is None:
                base_ds = maxDs / 20.0
                self.edtDistBound.setText("%.2f" % base_ds)
            else:
                base_ds = self.BASE_DS
            if self.BASE_DT is None:
                base_dt = int(math.ceil(maxDt / 20.0))
                self.edtTimeBound.setText("%.2f" % base_dt)
            else:
                base_dt = self.BASE_DT

            self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.progressBar.setMaximum(len(centroidList))
            self.lbl_log.setText("calculating N(ST)...")

            self.progressBar.setVisible(True)
            self.lbl_log.setVisible(True)

            # calculate N(ST)
            N_ST = None
            N_sim = []


            N_ST_double = 0
            knoxCentroidList = []
            for i, iCent, iDate in zip(range(len(centroidList)), centroidList, timeList):
                self.progressBar.setValue(i)
                forceGuiUpdate()

                for j, jCent, jDate in zip(range(len(centroidList)), centroidList, timeList):
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
            self.txtResult.setPlainText("N(ST): %d" % N_ST)

            N_sim.append(N_ST)


            # Draw result
            if flagBoundPoint:
                pointLayer.startEditing()
                tProvider = pointLayer.dataProvider()
                for centroid in knoxCentroidList:
                    tFeature = QgsFeature(tProvider.fields())
                    tFeature.setGeometry(QgsGeometry.fromPoint(centroid.vertexAt(0)))
                    tFeature.setAttribute(0, 1) # Group
                    tProvider.addFeatures([tFeature])
                pointLayer.commitChanges()
                pointLayer.updateExtents()
                self.__canvas.refresh()


            # 몬테카를로 시뮬레이션 통해 값 검증
            self.__monteCarloKFunction(self.NUM_SIMULATION, centroidList, timeList, base_ds, base_dt, N_sim)

            # sort results
            N_sim.sort()

            # calculate p-value
            pos = bisect_right(N_sim, N_ST)
            #print ("pos: %d" % pos)
            p = (1.0 - (float(pos) / float(self.NUM_SIMULATION+1))) * 100.0

            resString = ("Knox Test p-value: %.2f%%" % p)
            self.txtResult.appendPlainText(resString)

        except Exception as e:
            alert(e.message)
            return False

        return True

    def __monteCarloKFunction(self, numSim, centroidList, timeList, base_ds, base_dt, N_sim):
        randomSeed = int(time.time())
        np.random.seed(randomSeed)

        self.progressBar.setMaximum(numSim)

        for iSim in range(numSim):
            self.progressBar.setValue(iSim)
            self.lbl_log.setText(u"Monte Carlo Simulation({0}/{1})...".format(iSim, numSim))

            # date shuffle
            simDateList = np.random.permutation(timeList)
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
            # self.txtResult.appendPlainText("Sim[%d]_N(ST): %d" % (iSim, N_ST_double/2))

        self.lbl_log.hide()
        self.progressBar.hide()


    # Centroid 모으기
    def __collectData(self, srcLayer, timeColumnName):
        # ID 리스트 확보
        ids = srcLayer.allFeatureIds()

        # 진행상황 표시
        self.lbl_log.setText(u"지역 정보 모으는 중...")
        self.lbl_log.setVisible(True)
        self.progressBar.setMaximum(len(ids))
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.lbl_log.setVisible(True)
        self.progressBar.setVisible(True)

        # 정보 수집
        centroidList = []
        timeList = []
        for i, iID in enumerate(ids):
            self.progressBar.setValue(i)
            forceGuiUpdate()

            iFeature = srcLayer.getFeatures(QgsFeatureRequest(iID)).next()
            iGeom = iFeature.geometry().centroid()
            dateObj = iFeature[timeColumnName]

            # 시간이 Null이면 무시
            if dateObj.isNull():
                continue

            timeList.append(dateObj)
            centroidList.append(iGeom)

        self.lbl_log.setVisible(False)
        self.progressBar.setVisible(False)

        return ids, centroidList, timeList

    # Create Point Layer
    def __createPointLayer(self, orgLayer):
        resultLayerName = "Knox_Point_"+orgLayer.name()

        # 결과 레이어 이미 있는지 확인
        tLayer = None
        layers = self.__canvas.layers()
        for testLayer in layers:
            name = testLayer.name()
            if name != resultLayerName:
                continue
            if testLayer.type() != QgsMapLayer.VectorLayer:
                continue
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
            tLayerOption = "{0}?crs={1}&index=yes".format("Point", crs.authid())
            tLayer = QgsVectorLayer(tLayerOption, resultLayerName, "memory")
            tProvider = tLayer.dataProvider()
            tLayer.startEditing()
            tProvider.addAttributes([
                         QgsField("Group", QVariant.String)
            ])

            # Apply symbol
            symbol = QgsSymbolV2.defaultSymbol(QGis.Point)
            symbol.setColor(QColor(255,0,0))
            category1 = QgsRendererCategoryV2(1, symbol, "Scanned Points")
            categories = [category1]
            renderer = QgsCategorizedSymbolRendererV2("Group", categories)
            tLayer.setRendererV2(renderer)

            tLayer.commitChanges()
            QgsMapLayerRegistry.instance().addMapLayer(tLayer)
            self.__canvas.refresh()

        return tLayer


    # Create Convex Layer
    def __createConvexLayer(self, orgLayer):
        resultLayerName = "Knox_Convex_"+orgLayer.name()

        # 결과 레이어 이미 있는지 확인
        tLayer = None
        layers = self.__canvas.layers()
        for testLayer in layers:
            name = testLayer.name()
            if name != resultLayerName:
                continue
            if testLayer.type() != QgsMapLayer.VectorLayer:
                continue
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

