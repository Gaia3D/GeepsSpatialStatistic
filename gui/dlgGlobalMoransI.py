# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import *

from GeepsSpStats.gui.ui_global_morans_i import Ui_Dialog

# ui 파일에서 생산되는 클래스를 ui 변경시에도 별도수정 없이 수 있도록 다시 랩핑
# TODO: 여러 대화상자에서 Ui_Dialog를 모두 사용해도 되는지 검증 필요
class Dlg_GlobalMoransI(QtGui.QDialog, Ui_Dialog):
    weightMethod = None

    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.iface = iface

        # Weight 방법
        self.txtResult.setText(self.weightMethod)
        if (not self.weightMethod):
            self.weightMethod = "idw"
        self.setWeightMethod()

        # 이벤트 부착
        self.connectAction()

    # 각 부분 UI 들의 동작을 부착
    def connectAction(self):
        result = QObject.connect(self.btnClose, SIGNAL("clicked()"), self.onClose)
        result = QObject.connect(self.cmbLayer, SIGNAL("currentIndexChanged(int)"), self.onChangeLayer)
        result = QObject.connect(self.rdoIdw, SIGNAL("valueChanged()"), self.onChangeRadio)
        result = QObject.connect(self.rdoInDist, SIGNAL("valueChanged()"), self.onChangeRadio)
        result = QObject.connect(self.rdoContact, SIGNAL("valueChanged()"), self.onChangeRadio)

    def fillLayerList(self, layers):
        self.cmbLayer.clear()
        self.cmbLayer.addItems(layers)
        self.onChangeLayer(-1)

    def setWeightMethod(self):
        if self.weightMethod == "idw":
            self.rdoIdw.setChecked(True)
        elif self.weightMethod == "indest":
            self.rdoInDist.setChecked(True)
        elif self.weightMethod == "contact":
            self.rdoContact.setChecked(True)
        else:
            self.weightMethod = "idw"
            self.rdoIdw.setChecked(True)

    def onClose(self):
        self.close()

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
                self.cmbIdColumn.addItem(field.name())

    def onChangeRadio(self):
        if self.rdoIdw.isChecked():
            self.weightMethod = "idw"
        elif self.rdoInDist.isChecked():
            self.weightMethod = "indest"
        elif self.rdoContact.isChecked():
            self.weightMethod = "contact"
        else:
            self.weightMethod = None