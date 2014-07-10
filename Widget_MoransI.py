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

from gui.ui_form_morans_i import Ui_Form_Parameter as Ui_Form

def alert(message, mode=QMessageBox.Information):
    mbx = QMessageBox()
    mbx.setText(message)
    mbx.setIcon(QMessageBox.Information)
    if mode == QMessageBox.Question:
        mbx.setIcon(QMessageBox.Question)
        mbx.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    rc = mbx.exec_()
    return rc

class Widget_MoransI(QWidget,Ui_Form):
    __crrLayerName = None
    __crrIdColumn = None
    __crrTgtColumn = None
    crrMode = None
    result = {}

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
        if (self.crrMode == "multiple"):
            self.rdoMultiple.setChecked(True)
            self.onRdoMultipleSelected()
        else:
            self.rdoSingle.setChecked(True)
            self.onRdoSingleSelected()

    def __del__(self):
        # Disconnect Canvas
        # Canvas
        self.disconnect(self.__canvas, SIGNAL("layersChanged()"),
                     self.onCanvasLayersChanged)
        # Doc WidgetparentWidget
        self.disconnect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"),
                     self.__signal_DocWidget_visibilityChanged)
                
    # 각 부분 UI 들의 동작을 부착
    def __connectAction(self):
        QObject.connect(self.__canvas, SIGNAL("layersChanged()"), self.onCanvasLayersChanged)
        QObject.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.onCmbLayerChanged)
        QObject.connect(self.cmbIdColumn, SIGNAL("currentIndexChanged(int)"), self.onIdColumnChanged)
        QObject.connect(self.cmbTgtColumn, SIGNAL("currentIndexChanged(int)"), self.onTgtColumnChanged)
        QObject.connect(self.rdoSingle, SIGNAL("clicked()"), self.onRdoSingleSelected)
        QObject.connect(self.rdoMultiple, SIGNAL("clicked()"), self.onRdoMultipleSelected)
        QObject.connect(self.btnRun, SIGNAL("clicked()"), self.onRun)
        QObject.connect(self.btnSaveMap, SIGNAL("clicked()"), self.onSaveMap)
        QObject.connect(self.btnSaveChart, SIGNAL("clicked()"), self.onSaveChart)
        QObject.connect(self.btnSaveResult, SIGNAL("clicked()"), self.onSaveResult)

    def onCanvasLayersChanged(self):
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
            self.onCmbLayerChanged(-1)
            if (not layers or len(layers)==0):
                self.__crrLayerName = None
            else:
                self.__crrLayerName = layerNameList[0]

    def onCmbLayerChanged(self, index):
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

    def onIdColumnChanged(self, index):
        columnName = self.cmbIdColumn.currentText()

    def onTgtColumnChanged(self, index):
        columnName = self.cmbTgtColumn.currentText()

    def onRdoSingleSelected(self):
        if (not self.rdoSingle.isChecked()):
            return

        self.lbl_s_1.setEnabled(True)
        self.edtSearchDistance.setEnabled(True)

        self.lbl_m_1.setEnabled(False)
        self.edtCritcalZValue.setEnabled(False)
        self.gb_multiple.setEnabled(False)

        self.crrMode = "single"

    def onRdoMultipleSelected(self):
        if (not self.rdoMultiple.isChecked()):
            return

        self.lbl_s_1.setEnabled(False)
        self.edtSearchDistance.setEnabled(False)

        self.lbl_m_1.setEnabled(True)
        self.edtCritcalZValue.setEnabled(True)
        self.gb_multiple.setEnabled(True)

        self.crrMode = "multiple"


    ### Moran's I 실행
    def onRun(self):
        ### 입력 데이터 검사
        # Layer
        if (not self.__crrLayerName):
            alert("분석할 레이어를 선택하셔야 합니다.")
            return

        self.__crrIdColumn = self.cmbIdColumn.currentText()
        self.__crrTgtColumn = self.cmbTgtColumn.currentText()

        # Mode
        if not self.crrMode:
            alert("invalid mode")
            return

        # 단일 거리 Moran's I인 경우
        if (self.crrMode == "single"):
            try:
                searchDistance = float(self.edtSearchDistance.text())
            except ValueError:
                alert("Search Distance must be entered")
                return
            if (searchDistance <= 0):
                alert("Search Distance must grater than 0")
                return
            if (self.__crrIdColumn == self.__crrTgtColumn):
                rc = alert(u"ID 와 Data 컬럼이 같습니다.\n계속하시겠습니까?", QMessageBox.Question)
                if (rc != QMessageBox.Yes):
                    return

            self.runSingleMoran(self.__crrLayerName, searchDistance, self.__crrIdColumn, self.__crrTgtColumn)

        # 다중 거리 Moran's I인 경우
        elif (self.crrMode == "multiple"):
            try:
                criticalZValue = float(self.edtCritcalZValue.text())
            except ValueError:
                alert("Search Distance must be entered")
                return

            try:
                fromValue = float(self.edtFrom.text())
            except ValueError:
                alert("Distance Range From must be entered")
                return
            if (fromValue <= 0):
                alert("Distance Range From must grater than 0")
                return

            try:
                toValue = float(self.edtTo.text())
            except ValueError:
                alert("Distance Range To must be entered")
                return
            if (toValue <= 0):
                alert("Distance Range To must grater than 0")
                return

            try:
                byValue = float(self.edtBy.text())
            except ValueError:
                alert("Distance Range By must be entered")
                return
            if (byValue <= 0):
                alert("Distance Range By must grater than 0")
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
        centroidDict = {}
        for iID in ids:
            iPrg += 1
            self.progressBar.setValue(iPrg)
            # UI 갱신을 위해 강제로 이벤트 처리하게 함
            QgsApplication.processEvents()

            iFeature = layer.getFeatures(QgsFeatureRequest(iID)).next()
            iGeom = iFeature.geometry().centroid()
            centroidDict[iID] = iGeom

        # Weight 계산
        neighbors  = {}
        weights = {}
        dataList = []
        idList = []
        iPrg = 0;
        self.lbl_log.setText(u"각 지역간 인접성 계산 중...")
        for iID in ids:
            iGeom = centroidDict[iID]
            iRowNeighbors = []
            iRowWeights = []

            iPrg += 1
            self.progressBar.setValue(iPrg)
            # UI 갱신을 위해 강제로 이벤트 처리하게 함
            QgsApplication.processEvents()

            for jID in ids:
                jGeom = centroidDict[jID]

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
        mi = Moran(y, w, two_tailed=False)
        lm = Moran_Local(y, w, transformation="r")

        # 분석 결과를 UI에 채우기
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

        self.result["idList"] = idList
        self.result["centroidDict"] = centroidDict
        self.result["neighbors"] = neighbors
        self.result["local_I"] = lm.Is

        # Progress 제거
        self.progressBar.setVisible(False)
        self.lbl_log.setVisible(False)

        alert(u"Moran's I 지수 계산 완료")
        return True

    def runMultipleMoran(self):
        return True

    ### 분석결과 저장
    def onSaveMap(self):
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

    def onSaveChart(self):
        # 생성된 차트가 있는지 확인


        dlg = QFileDialog(self)
        dlg.setWindowTitle("Save Chart As")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("PNG (*.png)")
        dlg.setDefaultSuffix("png")
        if (not dlg.exec_()):
            return
        files = dlg.selectedFiles()
        graphImageFile = files[0]
        #self.__canvas.saveAsImage(graphImageFile)

        if os.path.isfile(graphImageFile):
            alert(u"그래프가 저장되었습니다.")
        else:
            alert(u"그래프 저장이 실패하였습니다.", QMessageBox.Warning)

    def onSaveResult(self):
        # 생성된 결과가 있는지 확인

        dlg = QFileDialog(self)
        dlg.setWindowTitle("Save Result As")
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("Plane Text (*.txt)")
        dlg.setDefaultSuffix("txt")
        if (not dlg.exec_()):
            return
        files = dlg.selectedFiles()
        resultFile = files[0]
        #self.__canvas.saveAsImage(resultFile)

        if os.path.isfile(resultFile):
            alert(u"분석결과가 저장되었습니다.")
        else:
            alert(u"분셕결과 저장이 실패하였습니다.", QMessageBox.Warning)

