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
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis import core, gui, utils

try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

from gui.ui_form_morans_i import Ui_Form_Parameter as Ui_Form

class OpenLayersOverviewWidget(QWidget,Ui_Form):
    def __init__(self, iface, dockwidget):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)
        self.__canvas = iface.mapCanvas()
        self.__dockwidget = dockwidget
        self.__init()

    def __init(self):
        self.connectAction()

    def __del__(self):
        # Disconnect Canvas
        # Canvas
        self.disconnect(self.__canvas, SIGNAL("extentsChanged()"),
                     self.__signal_canvas_extentsChanged)
        # Doc WidgetparentWidget
        self.disconnect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"),
                     self.__signal_DocWidget_visibilityChanged)
                
    # 각 부분 UI 들의 동작을 부착
    def connectAction(self):
        result = QObject.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.onChangeLayer)

    def fillLayerList(self, layers):
        self.cmbLayer.clear()
        self.cmbLayer.addItems(layers)
        self.onChangeLayer(-1)

    def onChangeLayer(self, index):
        layerName = self.cmbLayer.currentText()
        self.txtResult.setText(layerName)
        self.getLayerColumn(layerName)

    def getLayerColumn(self, layerName):
        tgtLayer = None
        canvas = self.iface.mapCanvas()
        for layer in canvas.layers():
            # TODO: VectorLayer 인지 확인 필요
            if (layer.name() == layerName):
                tgtLayer = layer
        if (not layer):
            pass
        else:
            self.cmbTgtColumn.clear()
            self.cmbIdColumn.clear()
            fields = tgtLayer.dataProvider().fields()
            for field in fields:
                self.cmbTgtColumn.addItem(field.name())
