# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
from pysal import W, G, G_Local
import numpy as np
from qgis.core import *
from Utility import *
from gui.ui_form_getisord_g import Ui_Form_Parameter as Ui_Form
import matplotlib.pyplot as plt
from xlwt import Workbook


class Widget_GetisOrdsG(QWidget, Ui_Form):
    title = "Getis-Ord's G Statistic"
    objectName = "objWidgetGetisord"

    # 분석결과 저장
    sourceRegions = {}
    globalResults = {}
    localResults = {}
    localNeighbors = {}

    # 현재 선택 저장
    __crrLayerName = None
    __crrIdColumn = None
    __crrTgtColumn = None
    __crrMode = None
    __crrDistance = None
    __criticalZ = None
    __makerArray = []

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
        if (self.__crrMode == "multiple"):
            self.rdoMultiple.setChecked(True)
            self.__onRdoMultipleSelected()
        else:
            self.rdoSingle.setChecked(True)
            self.__onRdoSingleSelected()

    # 소멸자
    def __del__(self):
        self.disconnectGlobalSignal()

    ### 외부용 함수
    # 위젯이 소멸될 때 전역 이벤트 리스터 연결제거
    def disconnectGlobalSignal(self):
        self.disconnect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.disconnect(self.__canvas, SIGNAL("renderComplete (QPainter *)"), self.__onRenderComplete)
        self.disconnect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)

    # QGIS 레이어 리스트 갱신을 UI에
    def updateGuiLayerList(self):
        layers = self.__canvas.layers()
        layerNameList = []
        bCrrLayerFound = False
        iCrrLayer = 0
        for layer in layers:
            layerName = layer.name()
            layerNameList.append(layerName)
            if (layerName == self.__crrLayerName):
                self.__crrLayerName = layerName
                bCrrLayerFound = True
            if (not bCrrLayerFound):
                iCrrLayer += 1

        self.cmbLayer.clear()
        self.cmbLayer.addItems(layerNameList)

        if (bCrrLayerFound):
            self.cmbLayer.setCurrentIndex(iCrrLayer)
            self.__crrLayerName = layerNameList[iCrrLayer]
        else:
            self.__onCmbLayerChanged(-1)
            if (not layers or len(layers)==0):
                self.__crrLayerName = None
            else:
                self.__crrLayerName = layerNameList[0]

    ### UI 동작처리
    # UI에 이벤트 핸들러 부착
    def __connectAction(self):
        self.connect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.connect(self.__canvas, SIGNAL("renderComplete (QPainter *)"), self.__onRenderComplete)
        self.connect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)
        self.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.__onCmbLayerChanged)
        self.connect(self.rdoSingle, SIGNAL("clicked()"), self.__onRdoSingleSelected)
        self.connect(self.rdoMultiple, SIGNAL("clicked()"), self.__onRdoMultipleSelected)
        self.connect(self.btnRun, SIGNAL("clicked()"), self.__onRun)
        self.connect(self.btnSaveMap, SIGNAL("clicked()"), self.__onSaveMap)
        self.connect(self.btnSaveResult, SIGNAL("clicked()"), self.__onSaveResult)
        self.connect(self.btnZDistPlot, SIGNAL("clicked()"), self.__onZDistPlot)
        #self.connect(self.btnScatterPlot, SIGNAL("clicked()"), self.__onScatterPlot)
        self.connect(self.tblGlobalSummary, SIGNAL("cellClicked(int, int)"), self.__onGlobalSummaryChanged)
        self.connect(self.tblLocalSummary, SIGNAL("cellClicked(int, int)"), self.__onLocalSummaryChanged)

    # UI 동작 정의
    # QGIS의 레이어가 변경된 때
    def __onCanvasLayersChanged(self):
        self.updateGuiLayerList()

    # 지도 그리기가 끝난 때
    def __onRenderComplete(self, painter):
        self.__drawMaker(painter)

    # 위젯의 가시성 변화 시
    def __signal_DocWidget_visibilityChanged(self, visible):
        self.__resetMaker()

    # 레이어 선택 콤보 변경시
    def __onCmbLayerChanged(self, index):
        layerName = self.cmbLayer.currentText()
        if (layerName != self.__crrLayerName):
            self.__crrLayerName = layerName
            self.__fillLayerColumn(layerName)

    # Single 모드 선택시
    def __onRdoSingleSelected(self):
        if (not self.rdoSingle.isChecked()):
            return

        self.lbl_s_1.setEnabled(True)
        self.edtSearchDistance.setEnabled(True)

        self.gb_multiple.setEnabled(False)

        self.__crrMode = "single"

    # Multiple 모드 선택시
    def __onRdoMultipleSelected(self):
        if (not self.rdoMultiple.isChecked()):
            return

        self.lbl_s_1.setEnabled(False)
        self.edtSearchDistance.setEnabled(False)

        self.gb_multiple.setEnabled(True)

        self.__crrMode = "multiple"

    # Global Summary의 행 선택시
    def __onGlobalSummaryChanged(self, row, column):
        keys = self.globalResults.keys()
        keys.sort()
        for i, distance in enumerate(keys):
            if (i == row):
                break
        self.__crrDistance = distance
        self.__displayLocalResultToUi(distance)

    # Local Summary의 행 선택시
    def __onLocalSummaryChanged(self, row, column):
        self.__displayRegionMaker(row)

    # Run 버튼 클릭시: 실행에 필요한 조건이 다 입력되었는지 확인
    def __onRun(self):
        ### 입력 데이터 검사
        # Layer
        if (not self.__crrLayerName):
            alert(u"분석할 레이어를 선택하셔야 합니다.")
            return

        self.__crrIdColumn = self.cmbIdColumn.currentText()
        self.__crrTgtColumn = self.cmbTgtColumn.currentText()

        # Mode
        if not self.__crrMode:
            alert(u"invalid mode")
            return

        # 단일 거리 Getis-Ord's G 인 경우
        if (self.__crrMode == "single"):
            try:
                searchDistance = float(self.edtSearchDistance.text())
            except ValueError:
                alert(u"검색 거리를 입력하셔야 합니다.")
                return
            if (searchDistance <= 0):
                alert(u"검색 거리는 0보다 커야 합니다.")
                return
            if (self.__crrIdColumn == self.__crrTgtColumn):
                rc = alert(u"ID 와 Data 컬럼이 같습니다.\n계속하시겠습니까?", QMessageBox.Question)
                if (rc != QMessageBox.Yes):
                    return

            if self.runSingleGetisOrd(self.__crrLayerName, searchDistance, self.__crrIdColumn, self.__crrTgtColumn):
                alert(u"Getis-Ord's G 지수 계산 완료")
            else:
                alert(u"Getis-Ord's G 지수 계산 실패", QMessageBox.Warning)


        # 다중 거리 Getis-Ord's G인 경우
        elif (self.__crrMode == "multiple"):
            try:
                fromValue = float(self.edtFrom.text())
            except ValueError:
                alert(u"검색 거리 From을 숫자로 입력하셔야 합니다.")
                return
            if (fromValue <= 0):
                alert(u"검색 거리 From은 0보다 커야 합니다.")
                return

            try:
                toValue = float(self.edtTo.text())
            except ValueError:
                alert(u"검색 거리 To를 숫자로 입력하셔야 합니다.")
                return
            if (toValue <= 0):
                alert(u"검색 거리 To는 0보다 커야 합니다.")
                return

            try:
                byValue = float(self.edtBy.text())
            except ValueError:
                alert(u"검색 거리 By를 숫자로 입력하셔야 합니다.")
                return
            if (byValue <= 0):
                alert(u"검색 거리 By는 0보다 커야 합니다.")
                return

            if (fromValue >= toValue):
                alert(u"Distance Range의 From은 To 보다 작아야 합니다.")
                return
            if ((toValue-fromValue) < byValue):
                alert(u"Distance Range의 By는 (From-To)보다 작거나 같아야 합니다.")
                return

            if self.runMultipleGetisOrd(self.__crrLayerName, fromValue, toValue, byValue, self.__crrIdColumn, self.__crrTgtColumn):
                alert(u"Getis-Ord's G 지수 계산 완료")
            else:
                alert(u"Getis-Ord's G 지수 계산 실패", QMessageBox.Warning)

        else:
            alert("invalid mode")
            return

    # 지도화면 저장 버튼 클릭
    def __onSaveMap(self):
        dlg = QFileDialog(self)
        dlg.setWindowTitle("Save Map As")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("PNG (*.png)")
        dlg.setDefaultSuffix("png")
        if (not dlg.exec_()):
            return
        files = dlg.selectedFiles()
        mapImageFile = files[0]
        self.__saveMapToImage(mapImageFile)

        if self.__saveMapToImage(mapImageFile):
            alert(u"지도화면이 저장되었습니다.")
        else:
            alert(u"지도저장이 실패하였습니다.", QMessageBox.Warning)

    # 액셀로 저장 버튼 클릭
    def __onSaveResult(self):
        if self.tblGlobalSummary.rowCount() <= 0:
            alert(u"먼저 [RUN]을 눌러 분석을 수행해 주십시오.")
            return

        dlg = QFileDialog(self)
        dlg.setWindowTitle("Save Result As")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("Microsoft Excel (*.xls)")
        dlg.setDefaultSuffix("xls")
        if (not dlg.exec_()):
            return
        files = dlg.selectedFiles()
        resultFile = files[0]

        if self.__saveResultToExcel(resultFile):
            alert(u"분석결과가 저장되었습니다.")
        else:
            alert(u"분석결과 저장이 실패하였습니다.", QMessageBox.Warning)

    # Z-Dist Plot 버튼 클릭
    def __onZDistPlot(self):
        if self.tblGlobalSummary.rowCount() <= 0:
            alert(u"먼저 [RUN]을 눌러 분석을 수행해 주십시오.")
            return

        if self.tblGlobalSummary.rowCount() == 1:
            alert(u"Getis-Ord's G : Multiple 모드로 동작시에만 Z-dist plot이 가능합니다..")
            return

        try:
            self.__criticalZ = float(self.edtCritcalZValue.text())
        except TypeError:
            self.__criticalZ = None

        self.__drawZDistPlot()

    # Scatter Plot 버튼 클릭
    def __onScatterPlot(self):
        if self.tblLocalSummary.rowCount() <= 0:
            alert(u"먼저 [RUN]을 눌러 분석을 수행해 주십시오.")
            return

        lm = self.localResults[self.__crrDistance]
        row = self.tblLocalSummary.currentRow()
        if row < 0:
            name = None
            value = None
            local_i = None
        else:
            name = self.tblLocalSummary.item(row, 0).text()
            value = float(self.tblLocalSummary.item(row, 1).text())
            local_i = float(self.tblLocalSummary.item(row, 2).text())
        self.__drawMoranScatterPlot(lm, name, value, local_i)

    ### Maker 처리
    # Local Summary의 선택 행에 해당하는 마커 생성
    def __displayRegionMaker(self, row):
        distance = self.__crrDistance
        lm = self.localResults[distance]
        (w, ids) = lm.w.full()
        id = ids[row]

        # 선택 지역 객체 선택
        layer = self.getLayerFromName(self.__crrLayerName)
        layer.removeSelection()
        layer.select(id)

        # 선택 지역으로 줌
        self.__canvas.zoomToSelected(layer)
        self.__canvas.zoomOut()

        # 인접으로 판단된 지역 표시
        centroid = self.sourceRegions[id]["centroid"]
        neighbors = self.localNeighbors[distance]
        nearIDs = neighbors[id]

        self.__resetMaker()
        centerPoint = centroid.vertexAt(0)
        for nearID in nearIDs:
            nearPoint = self.sourceRegions[nearID]["centroid"].vertexAt(0)
            line = QGraphicsLineItem(centerPoint.x(), centerPoint.y(), nearPoint.x(), nearPoint.y())
            line.setPen(QPen(QColor(100,100,100), 1, Qt.DotLine))
            self.__addMaker(line)

        # 거리 원 표시
        circle = QGraphicsEllipseItem(centerPoint.x()-distance, centerPoint.y()-distance,
                                      distance*2, distance*2)
        circle.setPen(QPen(QColor(200,0,0), 2, Qt.DashLine))
        self.__addMaker(circle)

        self.__canvas.refresh()

    # 마커 모두 지우기
    def __resetMaker(self):
        if self.__makerArray:
            del self.__makerArray
        self.__makerArray = []

    # 마커 추가
    def __addMaker(self, qGraphicsItem):
        self.__makerArray.append(qGraphicsItem)

    # 마커를 지도 화면에 표시
    def __drawMaker(self, painter):
        if not painter: return
        if not Qt: return
        if not self.__makerArray: return
        if len(self.__makerArray) <= 0: return

        # Matrix 계산
        mapToPixel = self.__canvas.getCoordinateTransform()
        pntTL = mapToPixel.toMapCoordinates(0, 0)
        pntLR = mapToPixel.toMapCoordinates(1000, 1000)
        pntOrg = mapToPixel.transform(0, 0)
        scaleX = 1000.0 / (pntLR.x() - pntTL.x())
        scaleY = -scaleX
        trX = pntOrg.x()
        trY = pntOrg.y()
        transform = QTransform(scaleX, 0, 0, scaleY, trX, trY)

        for maker in self.__makerArray:
            if type(maker) is QGraphicsLineItem:
                painter.setPen(maker.pen())
                painter.drawLine(transform.map(maker.line()))
            elif type(maker) is QGraphicsEllipseItem:
                painter.setPen(maker.pen())
                painter.setBrush(maker.brush())
                tmpLine = QLineF(transform.map(maker.rect().topLeft()),
                              transform.map(maker.rect().bottomRight()))
                painter.drawEllipse(QRectF(tmpLine.x1(), tmpLine.y1(), tmpLine.dx(), tmpLine.dy()))
            elif type(maker) is QGraphicsRectItem:
                painter.setPen(maker.pen())
                painter.setBrush(maker.brush())
                rect = QRectF(transform.map(maker.rect().topLeft()),
                              transform.map(maker.rect().bottomRight()))
                painter.drawRect(rect)

    ### 내부 유틸 함수
    #
    def getLayerFromName(self, layerName):
        retLayer = None
        for layer in self.__canvas.layers():
            # TODO: VectorLayer 인지 확인 필요
            if (layer.name() == layerName):
                retLayer = layer
        return retLayer

    # 선택된 레이어의 컬럼 정보 채우기
    def __fillLayerColumn(self, layerName):
        tgtLayer = self.getLayerFromName(layerName)
        if (not tgtLayer):
            self.cmbIdColumn.clear()
            self.cmbTgtColumn.clear()
        else:
            provider = tgtLayer.dataProvider()
            if provider:
                fields = provider.fields()
                fieldNameList = []
                i = 0; idxIdColumn = 0; idxTgtColumn = 0
                for field in fields:
                    fieldName = field.name()
                    fieldNameList.append(fieldName)
                    if fieldName == self.__crrIdColumn:
                        idxIdColumn = i
                    if fieldName == self.__crrTgtColumn:
                        idxTgtColumn = i
                    i += 1
                self.cmbIdColumn.clear()
                self.cmbTgtColumn.clear()
                self.cmbIdColumn.addItems(fieldNameList)
                self.cmbTgtColumn.addItems(fieldNameList)
                self.cmbIdColumn.setCurrentIndex(idxIdColumn)
                self.cmbTgtColumn.setCurrentIndex(idxTgtColumn)

    # 통계처리 지역의 정보를 추출
    def __collectRegionInfo(self, layer, idColumn, valueColumn):
        # ID 리스트 확보
        ids = layer.allFeatureIds()

        # 진행상황 표시
        self.progressBar.setMaximum(len(ids))
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        # Centroid 수집
        iPrg = 0
        self.sourceRegions = {}
        for iID in ids:
            iPrg += 1
            self.progressBar.setValue(iPrg)
            forceGuiUpdate()

            iFeature = layer.getFeatures(QgsFeatureRequest(iID)).next()
            iGeom = iFeature.geometry().centroid()
            tName = "%s" % iFeature[idColumn]
            try:
                value = float(iFeature[valueColumn])
            except TypeError:
                value = 0.0
            self.sourceRegions[iID] = {"name": tName, "centroid": iGeom, "value": value}
        return ids

    # 기준 거리에 따른 Weight Matrix 계산
    def __calcWeight(self, layer, ids, searchDistance, valueColumn):
        # Weight 계산
        neighbors  = {}
        weights = {}
        dataList = []
        idList = []
        iPrg = 0
        for iID in ids:
            #iGeom = centroidDict[iID]
            iGeom = self.sourceRegions[iID]["centroid"]
            iRowNeighbors = []
            iRowWeights = []

            iPrg += 1
            self.progressBar.setValue(iPrg)
            forceGuiUpdate()

            for jID in ids:
                #jGeom = centroidDict[jID]
                jGeom = self.sourceRegions[jID]["centroid"]

                if iID == jID: # 같은 지역인 경우
                    pass
                else:
                    dist = iGeom.distance(jGeom)
                    if dist != 0.0 and dist <= searchDistance:
                        iRowNeighbors.append(jID)
                        iRowWeights.append(1)
            if (len(iRowNeighbors) > 0):
                neighbors[iID] = iRowNeighbors
                weights[iID] = iRowWeights
                iFeature = layer.getFeatures(QgsFeatureRequest(iID)).next()
                try:
                    val = float(iFeature[valueColumn])
                except TypeError:
                    val = 0.0
                dataList.append(val)
                idList.append(iID)

        w = W(neighbors, weights)
        y = np.array(dataList)
        self.localNeighbors[searchDistance] = neighbors

        return w, y

    # 기준거리 변화에 따른 Z(d) 변화 그래프
    def __drawZDistPlot(self):
        distList = self.globalResults.keys()
        distList.sort()
        zList = []
        for dist in distList:
            zList.append(self.globalResults[dist].z_norm)

        plt.plot(distList, zList, "b")
        plt.xlabel("Distance = d")
        plt.ylabel("Z[G(d)]")
        if not self.__criticalZ is None:
            plt.plot([distList[0],distList[-1]], [self.__criticalZ, self.__criticalZ], "r")
            plt.text(distList[-1], self.__criticalZ, "Critical Z-Value\n %.3f" % self.__criticalZ, color="r")
        plt.title("Z[G(d)]s over a range of search distance")
        plt.show()

    # 원 값과 Local I 값을 그래프로
    def __drawMoranScatterPlot(self, lg, name=None, value=0, local_i=0):
        plt.scatter(lg.y, lg.Gs)
        plt.xlabel("Value[i]")
        plt.ylabel("Local G[i]")
        plt.scatter([value], [local_i], color="r", marker="s")
        if not name is None:
            plt.text(value, local_i, "  " + name, color="r", fontweight="bold")
        plt.title("Moran Scatter Chart of distance %d" % self.__crrDistance)
        plt.show()

    ########################
    ### Getis-Ord's G 계산 수행
    # 한개의 거리 기준으로 Getis-Ord's G수행
    def runSingleGetisOrd(self, layerName, searchDistance, idColumn, valueColumn):
        self.__resetMaker();
        try:
            layer = self.getLayerFromName(layerName)
            if (not layer): return

            self.tblGlobalSummary.setRowCount(0)
            self.tblLocalSummary.setRowCount(0)

            self.progressBar.setVisible(True)
            self.lbl_log.setVisible(True)

            # 레이어에서 중심점, 지역명, ID 추출
            self.lbl_log.setText(u"중심점 추출중...")
            forceGuiUpdate()
            ids = self.__collectRegionInfo(layer, idColumn, valueColumn)

            # 결과 저장변수 초기화
            self.globalResults = {}
            self.localResults = {}
            self.__resetMaker()

            # 지역간 가중치를 담은 Weight 생성
            self.lbl_log.setText(u"각 지역간 인접성 계산 중...")
            forceGuiUpdate()
            w, y = self.__calcWeight(layer, ids, searchDistance, valueColumn)

            # Getis-Ord's G 계산
            self.lbl_log.setText(u"Getis-Ord's G 계산중...")
            forceGuiUpdate()
            gg = G(y, w)
            lg = G_Local(y, w)

            # 결과를 맴버변수에 저장
            self.globalResults[searchDistance] = gg
            self.localResults[searchDistance] = lg

            # 분석 결과를 UI에 채우기
            self.__crrDistance = searchDistance
            self.__displayGlobalResultToUi()
            self.__displayLocalResultToUi(searchDistance)

            # Progress 제거
            self.progressBar.setVisible(False)
            self.lbl_log.setVisible(False)

            self.lbl_log.setText(u"Getis-Ord's G 지수 계산 완료")
            forceGuiUpdate()

            return True
        except Exception:
            return False

    # 연속 거리 기준으로 Getis-Ord's G 수행
    def runMultipleGetisOrd(self, layerName, fromValue, toValue, byValue, idColumn, valueColumn):
        self.__resetMaker();
        try:
            layer = self.getLayerFromName(layerName)
            if (not layer): return

            self.tblGlobalSummary.setRowCount(0)
            self.tblLocalSummary.setRowCount(0)

            self.progressBar.setVisible(True)
            self.lbl_log.setVisible(True)

            # 레이어에서 중심점, 지역명, ID 추출
            self.lbl_log.setText(u"중심점 추출중...")
            forceGuiUpdate()
            ids = self.__collectRegionInfo(layer, idColumn, valueColumn)

            # 결과 저장변수 초기화
            self.globalResults = {}
            self.localResults = {}
            self.__resetMaker()

            searchDistance = fromValue
            iCnt = 1
            iTotalCnt, mod = divmod((toValue-fromValue), byValue)
            iTotalCnt += 1

            while True:
                # 지역간 가중치를 담은 Weight 생성
                self.lbl_log.setText(u"각 지역간 인접성 계산 중(%d/%d)..." % (iCnt, iTotalCnt))
                forceGuiUpdate()
                w, y = self.__calcWeight(layer, ids, searchDistance, valueColumn)

                # Getis-Ord's G 계산
                self.lbl_log.setText(u"Getis-Ord's G (%.1f)계산중..." % searchDistance)
                forceGuiUpdate()
                gg = G(y, w)
                lg = G_Local(y, w)

                # 결과를 맴버변수에 저장
                self.globalResults[searchDistance] = gg
                self.localResults[searchDistance] = lg

                searchDistance += byValue
                if (searchDistance > toValue): break

                iCnt += 1

            # 분석 결과를 UI에 채우기
            self.__displayGlobalResultToUi()
            self.__crrDistance = fromValue
            self.__displayLocalResultToUi(fromValue)

            # 단계에 따른 그래프
            pass

            # Progress 제거
            self.progressBar.setVisible(False)
            self.lbl_log.setVisible(False)

            self.lbl_log.setText(u"Getis-Ord's G (%.1f) 계산 완료" % searchDistance)
            forceGuiUpdate()

            return True
        except Exception:
            return False

    #########################
    ### 분석결과 표현
    # UI에 표현
    def __displayGlobalResultToUi(self):
        keys = self.globalResults.keys()
        keys.sort()

        self.tblGlobalSummary.setRowCount(len(keys))
        for i, searchDistance in enumerate(keys):
            gg = self.globalResults[searchDistance]
            tDist = QTableWidgetItem("%.0f" % searchDistance)
            tDist.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tG = QTableWidgetItem("%.4f" % gg.G)
            tG.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tE = QTableWidgetItem("%.4f" % gg.EG)
            tE.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tV = QTableWidgetItem("%.4f" % gg.VG)
            tV.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tZ = QTableWidgetItem("%.4f" % gg.z_norm)
            tZ.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tP = QTableWidgetItem("%.2f%%" % (gg.p_norm*100.0))
            tP.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)

            self.tblGlobalSummary.setItem(i, 0, tDist)
            self.tblGlobalSummary.setItem(i, 1, tG)
            self.tblGlobalSummary.setItem(i, 2, tE)
            self.tblGlobalSummary.setItem(i, 3, tV)
            self.tblGlobalSummary.setItem(i, 4, tZ)
            self.tblGlobalSummary.setItem(i, 5, tP)

    def __displayLocalResultToUi(self, searchDistance):
        lg = self.localResults[searchDistance]
        (w, idList) = lg.w.full()
        self.lbl_distance.setText("%.1f" % searchDistance)
        forceGuiUpdate()

        self.tblLocalSummary.setRowCount(len(idList))
        for i, id in enumerate(idList):
            region = self.sourceRegions[id]
            tName = QTableWidgetItem("%s" % region["name"])
            tName.setTextAlignment(Qt.AlignCenter)
            tY = QTableWidgetItem("%f" % region["value"])
            tY.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tG = QTableWidgetItem("%.4f" % lg.Gs[i])
            tG.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tZ = QTableWidgetItem("%.4f" % lg.z_sim[i])
            tZ.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tP = QTableWidgetItem("%.2f%%" % (lg.p_z_sim[i]*100.0))
            tP.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)

            self.tblLocalSummary.setItem(i, 0, tName)
            self.tblLocalSummary.setItem(i, 1, tY)
            self.tblLocalSummary.setItem(i, 2, tG)
            self.tblLocalSummary.setItem(i, 3, tZ)
            self.tblLocalSummary.setItem(i, 4, tP)

    # 지도 화면을 이미지로 저장
    def __saveMapToImage(self, mapImageFile):
        try:
            self.__canvas.saveAsImage(mapImageFile)
        except Exception:
            return False

        if os.path.isfile(mapImageFile):
            return True
        else:
            return False

    # 액셀 파일로 저장
    def __saveResultToExcel(self, resultFile):
        try:
            # 테이블 헤더 정보 수집
            globalHeader = []
            numGlobalColumn = self.tblGlobalSummary.columnCount()
            for i in range(numGlobalColumn):
                headerText = self.tblGlobalSummary.horizontalHeaderItem(i).text()
                globalHeader.append(headerText)

            localHeader = []
            numLocalColumn = self.tblLocalSummary.columnCount()
            for i in range(numLocalColumn):
                headerText = self.tblLocalSummary.horizontalHeaderItem(i).text()
                localHeader.append(headerText)

            # Global G 기록
            book = Workbook("UTF-8")
            globalSheet = book.add_sheet("Global Getis-Ord's G")
            for i in range(len(globalHeader)):
                globalSheet.write(0, i, globalHeader[i])

            for i, distance in enumerate(self.globalResults):
                gg = self.globalResults[distance]
                globalSheet.write(i+1, 0, "%.0f" % distance)
                globalSheet.write(i+1, 1, "%.4f" % gg.G)
                globalSheet.write(i+1, 2, "%.4f" % gg.EG)
                globalSheet.write(i+1, 3, "%.4f" % gg.VG_norm)
                globalSheet.write(i+1, 4, "%.4f" % gg.z_norm)
                globalSheet.write(i+1, 5, "%.2f%%" % (gg.p_norm*100.0))

            # Local G 기록
            for i, distance in enumerate(self.localResults):
                lg = self.localResults[distance]
                localSheet = book.add_sheet(u"Local G (%d)" % distance)
                for col in range(len(localHeader)):
                    localSheet.write(0, col, localHeader[col])

                (w, ids) = lg.w.full()
                for j, id in enumerate(ids):
                    region = self.sourceRegions[id]
                    if not region:
                        continue
                    localSheet.write(j+1, 0, region["name"])
                    localSheet.write(j+1, 1, region["value"])
                    localSheet.write(j+1, 2, "%.4f" % lg.Gs[j])
                    localSheet.write(j+1, 3, "%.4f" % lg.z_sim[j])
                    localSheet.write(j+1, 4, "%.2f%%" % (lg.p_z_sim[j]*100.0))

            # 최종 저장
            book.save(resultFile)
        except Exception:
            return False

        if os.path.isfile(resultFile):
            return True
        else:
            return False