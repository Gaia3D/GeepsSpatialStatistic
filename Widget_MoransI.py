# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Openlayers Overview  - A QGIS plugin to show map in browser(google maps and others)
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
from pysal import W, Moran, Moran_Local
import numpy as np
from qgis.core import *
from Utlity import *
from gui.ui_form_morans_i import Ui_Form_Parameter as Ui_Form
import matplotlib.pyplot as plt
from xlwt import Workbook


class Widget_MoransI(QWidget, Ui_Form):
    result = {} # TODO: Remove
    sourceRegions = {}
    globalResults = {}
    localResults = {}

    __crrLayerName = None
    __crrIdColumn = None
    __crrTgtColumn = None
    __crrMode = None
    __makerArray = []

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

    def __del__(self):
        self.disconnectGlobalSignal()

    def __forceGuiUpdate(self):
        QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def disconnectGlobalSignal(self):
        # 위젯이 소멸될 때 전역 이벤트 리스터 연결제거
        self.disconnect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.disconnect(self.__canvas, SIGNAL("renderComplete (QPainter *)"), self.__onRenderComplete)
        self.disconnect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)

    # 각 부분 UI 들의 동작을 부착
    def __connectAction(self):
        self.connect(self.__canvas, SIGNAL("layersChanged()"), self.__onCanvasLayersChanged)
        self.connect(self.__canvas, SIGNAL("renderComplete (QPainter *)"), self.__onRenderComplete)
        self.connect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"), self.__signal_DocWidget_visibilityChanged)
        self.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.__onCmbLayerChanged)
        #self.connect(self.cmbIdColumn, SIGNAL("currentIndexChanged(int)"), self.__onIdColumnChanged)
        #self.connect(self.cmbTgtColumn, SIGNAL("currentIndexChanged(int)"), self.__onTgtColumnChanged)
        self.connect(self.rdoSingle, SIGNAL("clicked()"), self.__onRdoSingleSelected)
        self.connect(self.rdoMultiple, SIGNAL("clicked()"), self.__onRdoMultipleSelected)
        self.connect(self.btnRun, SIGNAL("clicked()"), self.__onRun)
        self.connect(self.btnSaveMap, SIGNAL("clicked()"), self.__onSaveMap)
        self.connect(self.btnSaveResult, SIGNAL("clicked()"), self.__onSaveResult)
        self.connect(self.tblLocalSummary, SIGNAL("cellClicked(int, int)"), self.__onLocalSummaryChanged)

    # UI 동작 정의
    def __onCanvasLayersChanged(self):
        self.updateGuiLayerList()

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

    def __onRenderComplete(self, painter):
        self.__drawMaker(painter)

    def __signal_DocWidget_visibilityChanged(self, visible):
        self.__resetMaker()

    def __onCmbLayerChanged(self, index):
        layerName = self.cmbLayer.currentText()
        if (layerName != self.__crrLayerName):
            self.__crrLayerName = layerName
            self.__fillLayerColumn(layerName)

    def getLayerFromName(self, layerName):
        retLayer = None
        for layer in self.__canvas.layers():
            # TODO: VectorLayer 인지 확인 필요
            if (layer.name() == layerName):
                retLayer = layer
        return retLayer

    def __fillLayerColumn(self, layerName):
        tgtLayer = self.getLayerFromName(layerName)
        if (not tgtLayer):
            self.cmbIdColumn.clear()
            self.cmbTgtColumn.clear()
        else:
            fields = tgtLayer.dataProvider().fields()
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

    def __onRdoSingleSelected(self):
        if (not self.rdoSingle.isChecked()):
            return

        self.lbl_s_1.setEnabled(True)
        self.edtSearchDistance.setEnabled(True)

        self.lbl_m_1.setEnabled(False)
        self.edtCritcalZValue.setEnabled(False)
        self.gb_multiple.setEnabled(False)

        self.__crrMode = "single"

    def __onRdoMultipleSelected(self):
        if (not self.rdoMultiple.isChecked()):
            return

        self.lbl_s_1.setEnabled(False)
        self.edtSearchDistance.setEnabled(False)

        self.lbl_m_1.setEnabled(True)
        self.edtCritcalZValue.setEnabled(True)
        self.gb_multiple.setEnabled(True)

        self.__crrMode = "multiple"

    def __onLocalSummaryChanged(self, row, column):
        #alert("%d:%d" % (row, column))
        if (not self.result): return
        id = self.result["idList"][row]
        if (id == None): return

        # 선택 지역 객체 선택
        layer = self.getLayerFromName(self.__crrLayerName)
        layer.removeSelection()
        layer.select(id)

        # 선택 지역으로 줌
        self.__canvas.zoomToSelected(layer)
        self.__canvas.zoomOut()

        # 인접으로 판단된 지역 표시
        centroidDict = self.result["centroidDict"]
        centroid = centroidDict[id]
        neighbors = self.result["neighbors"]
        nearIDs = neighbors[id]
        searchDistance = self.result["searchDistance"]

        self.__resetMaker()
        centerPoint = centroid.vertexAt(0)
        for nearID in nearIDs:
            nearPoint = centroidDict[nearID].vertexAt(0)
            line = QGraphicsLineItem(centerPoint.x(), centerPoint.y(), nearPoint.x(), nearPoint.y())
            line.setPen(QPen(QColor(100,100,100), 1, Qt.DotLine))
            self.__addMaker(line)

        # 거리 원 표시
        circle = QGraphicsEllipseItem(centerPoint.x()-searchDistance, centerPoint.y()-searchDistance,
                                      searchDistance*2, searchDistance*2)
        circle.setPen(QPen(QColor(200,0,0), 2, Qt.DashLine))
        self.__addMaker(circle)

        self.__canvas.refresh()


    ### Maker 처리
    def __resetMaker(self):
        if self.__makerArray:
            del self.__makerArray
        self.__makerArray = []

    def __addMaker(self, qGraphicsItem):
        self.__makerArray.append(qGraphicsItem)

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


    ### Moran's I 실행
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

        # 단일 거리 Moran's I인 경우
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

            self.runSingleMoran(self.__crrLayerName, searchDistance, self.__crrIdColumn, self.__crrTgtColumn)

        # 다중 거리 Moran's I인 경우
        elif (self.__crrMode == "multiple"):
            try:
                criticalZValue = float(self.edtCritcalZValue.text())
            except ValueError:
                alert(u"유의기준 Z값(Critical Z-Value)을 입력하셔야 합니다.")
                return

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

            self.runMultipleMoran()

        else:
            alert("invalid mode")
            return

    def runSingleMoran(self, layerName, searchDistance, idColumn, valueColumn):
        layer = self.getLayerFromName(layerName)
        if (not layer): return

        self.tblGlobalSummary.setRowCount(0)
        self.tblLocalSummary.setRowCount(0)

        # Layer 정보 확보
        layerType = layer.geometryType();
        layerTypeName = ""
        if layerType == QGis.Point:
            layerTypeName = "Point"
        elif layerType == QGis.Line:
            layerTypeName = "Line"
        elif layerType == QGis.Polygon:
            layerTypeName = "Polygon"
        else:
            layerTypeName = "Unknown"
        crs = layer.crs()

        # 객체 Centroid 수집
        ids = layer.allFeatureIds()

        # ID 리스트 확보
        ids = layer.allFeatureIds()

        # 진행상황 표시
        self.progressBar.setVisible(True)
        self.lbl_log.setVisible(True)
        self.lbl_log.setText(u"Weight Matrix 계산중...")
        self.progressBar.setMaximum(len(ids))
        self.progressBar.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        # Centroid 수집
        iPrg = 0;
        self.lbl_log.setText(u"중심점 추출중...")
        self.sourceRegions = {}
        centroidDict = {} # TODO: Remove
        for iID in ids:
            iPrg += 1
            self.progressBar.setValue(iPrg)
            self.__forceGuiUpdate()

            iFeature = layer.getFeatures(QgsFeatureRequest(iID)).next()
            iGeom = iFeature.geometry().centroid()
            centroidDict[iID] = iGeom  # TODO: Remove
            tName = "%s" % iFeature[idColumn]
            try:
                value = float(iFeature[valueColumn])
            except TypeError:
                value = 0.0
            self.sourceRegions[iID] = {"name": tName, "centroid": iGeom, "value": value}

        # Weight 계산
        neighbors  = {}
        weights = {}
        dataList = []
        idList = []
        iPrg = 0;
        self.lbl_log.setText(u"각 지역간 인접성 계산 중...")
        for iID in ids:
            #iGeom = centroidDict[iID]
            iGeom = self.sourceRegions[iID]["centroid"]
            iRowNeighbors = []
            iRowWeights = []

            iPrg += 1
            self.progressBar.setValue(iPrg)
            self.__forceGuiUpdate()

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

        # Moran's I 계산
        self.lbl_log.setText(u"Moran's I 계산중...")
        self.__forceGuiUpdate()
        mi = Moran(y, w, two_tailed=False)
        lm = Moran_Local(y, w, transformation="r")

        self.globalResults[searchDistance] = mi
        self.localResults[searchDistance] = lm

        # 분석 결과를 UI에 채우기
        self.__resetMaker()
        tDist = QTableWidgetItem("%.0f" % searchDistance)
        tDist.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        tI = QTableWidgetItem("%.4f" % mi.I)
        tI.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        tE = QTableWidgetItem("%.4f" % mi.EI)
        tE.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        tV = QTableWidgetItem("%.4f" % mi.VI_norm)
        tV.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        tZ = QTableWidgetItem("%.4f" % mi.z_norm)
        tZ.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
        tP = QTableWidgetItem("%.2f%%" % (mi.p_norm*100.0))
        tP.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)

        self.tblGlobalSummary.setRowCount(1)
        self.tblGlobalSummary.setItem(0, 0, tDist)
        self.tblGlobalSummary.setItem(0, 1, tI)
        self.tblGlobalSummary.setItem(0, 2, tE)
        self.tblGlobalSummary.setItem(0, 3, tV)
        self.tblGlobalSummary.setItem(0, 4, tZ)
        self.tblGlobalSummary.setItem(0, 5, tP)

        self.tblLocalSummary.setRowCount(len(idList))
        for i in range(len(idList)):
            id = idList[i]
            oFeature = layer.getFeatures(QgsFeatureRequest(id)).next()
            tName = QTableWidgetItem("%s" % oFeature[idColumn])
            tName.setTextAlignment(Qt.AlignCenter)
            tY = QTableWidgetItem("%f" % y[i])
            tY.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tI = QTableWidgetItem("%.4f" % lm.Is[i])
            tI.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tZ = QTableWidgetItem("%.4f" % lm.z_sim[i])
            tZ.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
            tP = QTableWidgetItem("%.2f%%" % (lm.p_z_sim[i]*100.0))
            tP.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)

            self.tblLocalSummary.setItem(i, 0, tName)
            self.tblLocalSummary.setItem(i, 1, tY)
            self.tblLocalSummary.setItem(i, 2, tI)
            self.tblLocalSummary.setItem(i, 3, tZ)
            self.tblLocalSummary.setItem(i, 4, tP)

        # Moran Scatter Plot
        #plot(lm.z_sim, lm.Is, 'ro')
        #show()
        plt.scatter(lm.z_sim, lm.Is)
        plt.show()

        # 내부 변수에 결과 저장
        self.result["idList"] = idList
        self.result["centroidDict"] = centroidDict
        self.result["neighbors"] = neighbors
        self.result["local_I"] = lm.Is
        self.result["searchDistance"] = searchDistance

        # Progress 제거
        self.progressBar.setVisible(False)
        self.lbl_log.setVisible(False)

        self.lbl_log.setText(u"Moran's I 지수 계산 완료")
        self.__forceGuiUpdate()
        alert(u"Moran's I 지수 계산 완료")
        return True

    def runMultipleMoran(self):
        return True

    ### 분석결과 저장
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
        self.__canvas.saveAsImage(mapImageFile)

        if os.path.isfile(mapImageFile):
            alert(u"지도화면이 저장되었습니다.")
        else:
            alert(u"지도저장이 실패하였습니다.", QMessageBox.Warning)

    def __onSaveResult(self):
        # 생성된 결과가 있는지 확인

        dlg = QFileDialog(self)
        dlg.setWindowTitle("Save Result As")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("Microsoft Excel (*.xls)")
        dlg.setDefaultSuffix("xls")
        if (not dlg.exec_()):
            return
        files = dlg.selectedFiles()
        resultFile = files[0]

        if self.saveResultToExcel(resultFile) == True:
            alert(u"분석결과가 저장되었습니다.")
        else:
            alert(u"분석결과 저장이 실패하였습니다.", QMessageBox.Warning)

    def saveResultToExcel(self, resultFile):
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

            # Global Moran 기록
            book = Workbook("UTF-8")
            globalSheet = book.add_sheet("Global Moran's I")
            for i in range(len(globalHeader)):
                globalSheet.write(0, i, globalHeader[i])

            for i, distance in enumerate(self.globalResults):
                mi = self.globalResults[distance]
                globalSheet.write(i+1, 0, "%.0f" % distance)
                globalSheet.write(i+1, 1, "%.4f" % mi.I)
                globalSheet.write(i+1, 2, "%.4f" % mi.EI)
                globalSheet.write(i+1, 3, "%.4f" % mi.VI_norm)
                globalSheet.write(i+1, 4, "%.4f" % mi.z_norm)
                globalSheet.write(i+1, 5, "%.2f%%" % (mi.p_norm*100.0))

            # Local Moran 기록
            for i, distance in enumerate(self.localResults):
                lm = self.localResults[distance]
                localSheet = book.add_sheet(u"Local I (%d)" % distance)
                for col in range(len(localHeader)):
                    localSheet.write(0, col, localHeader[col])

                (w, ids) = lm.w.full()
                for j, id in enumerate(ids):
                    region = self.sourceRegions[id]
                    if not region:
                        continue
                    localSheet.write(j+1, 0, region["name"])
                    localSheet.write(j+1, 1, region["value"])
                    localSheet.write(j+1, 2, "%.4f" % lm.Is[j])
                    localSheet.write(j+1, 3, "%.4f" % lm.z_sim[j])
                    localSheet.write(j+1, 4, "%.2f%%" % (lm.p_z_sim[j]*100.0))

            # 최종 저장
            book.save(resultFile)
        except Exception:
            return False

        if os.path.isfile(resultFile):
            return True
        else:
            return False