# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_morans_i.ui'
#
# Created: Sun Jul 13 16:48:55 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form_Parameter(object):
    def setupUi(self, Form_Parameter):
        Form_Parameter.setObjectName(_fromUtf8("Form_Parameter"))
        Form_Parameter.resize(368, 548)
        self.label = QtGui.QLabel(Form_Parameter)
        self.label.setGeometry(QtCore.QRect(4, 5, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.cmbLayer = QtGui.QComboBox(Form_Parameter)
        self.cmbLayer.setGeometry(QtCore.QRect(84, 2, 281, 22))
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.label_3 = QtGui.QLabel(Form_Parameter)
        self.label_3.setGeometry(QtCore.QRect(187, 30, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cmbTgtColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbTgtColumn.setGeometry(QtCore.QRect(274, 27, 91, 22))
        self.cmbTgtColumn.setObjectName(_fromUtf8("cmbTgtColumn"))
        self.rdoSingle = QtGui.QRadioButton(Form_Parameter)
        self.rdoSingle.setGeometry(QtCore.QRect(4, 64, 141, 16))
        self.rdoSingle.setObjectName(_fromUtf8("rdoSingle"))
        self.rdoMultiple = QtGui.QRadioButton(Form_Parameter)
        self.rdoMultiple.setGeometry(QtCore.QRect(4, 90, 151, 16))
        self.rdoMultiple.setObjectName(_fromUtf8("rdoMultiple"))
        self.lbl_s_1 = QtGui.QLabel(Form_Parameter)
        self.lbl_s_1.setGeometry(QtCore.QRect(164, 64, 101, 16))
        self.lbl_s_1.setObjectName(_fromUtf8("lbl_s_1"))
        self.edtSearchDistance = QtGui.QLineEdit(Form_Parameter)
        self.edtSearchDistance.setGeometry(QtCore.QRect(274, 61, 91, 20))
        self.edtSearchDistance.setObjectName(_fromUtf8("edtSearchDistance"))
        self.lbl_m_1 = QtGui.QLabel(Form_Parameter)
        self.lbl_m_1.setEnabled(False)
        self.lbl_m_1.setGeometry(QtCore.QRect(164, 90, 101, 16))
        self.lbl_m_1.setObjectName(_fromUtf8("lbl_m_1"))
        self.edtCritcalZValue = QtGui.QLineEdit(Form_Parameter)
        self.edtCritcalZValue.setGeometry(QtCore.QRect(274, 87, 91, 20))
        self.edtCritcalZValue.setObjectName(_fromUtf8("edtCritcalZValue"))
        self.gb_multiple = QtGui.QGroupBox(Form_Parameter)
        self.gb_multiple.setEnabled(False)
        self.gb_multiple.setGeometry(QtCore.QRect(4, 110, 361, 41))
        self.gb_multiple.setObjectName(_fromUtf8("gb_multiple"))
        self.label_6 = QtGui.QLabel(self.gb_multiple)
        self.label_6.setGeometry(QtCore.QRect(10, 17, 41, 16))
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.edtFrom = QtGui.QLineEdit(self.gb_multiple)
        self.edtFrom.setGeometry(QtCore.QRect(58, 15, 71, 20))
        self.edtFrom.setObjectName(_fromUtf8("edtFrom"))
        self.edtTo = QtGui.QLineEdit(self.gb_multiple)
        self.edtTo.setGeometry(QtCore.QRect(167, 15, 71, 20))
        self.edtTo.setObjectName(_fromUtf8("edtTo"))
        self.label_7 = QtGui.QLabel(self.gb_multiple)
        self.label_7.setGeometry(QtCore.QRect(127, 17, 31, 16))
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.gb_multiple)
        self.label_8.setGeometry(QtCore.QRect(241, 17, 31, 16))
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.edtBy = QtGui.QLineEdit(self.gb_multiple)
        self.edtBy.setGeometry(QtCore.QRect(281, 15, 71, 20))
        self.edtBy.setObjectName(_fromUtf8("edtBy"))
        self.btnRun = QtGui.QPushButton(Form_Parameter)
        self.btnRun.setGeometry(QtCore.QRect(2, 154, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.btnRun.setFont(font)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.btnSaveResult = QtGui.QPushButton(Form_Parameter)
        self.btnSaveResult.setGeometry(QtCore.QRect(284, 206, 81, 23))
        self.btnSaveResult.setObjectName(_fromUtf8("btnSaveResult"))
        self.btnSaveMap = QtGui.QPushButton(Form_Parameter)
        self.btnSaveMap.setGeometry(QtCore.QRect(202, 206, 81, 23))
        self.btnSaveMap.setFlat(False)
        self.btnSaveMap.setObjectName(_fromUtf8("btnSaveMap"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(4, 214, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(Form_Parameter)
        self.label_10.setGeometry(QtCore.QRect(4, 348, 111, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.tblGlobalSummary = QtGui.QTableWidget(Form_Parameter)
        self.tblGlobalSummary.setGeometry(QtCore.QRect(4, 230, 361, 111))
        self.tblGlobalSummary.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblGlobalSummary.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblGlobalSummary.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblGlobalSummary.setCornerButtonEnabled(False)
        self.tblGlobalSummary.setRowCount(0)
        self.tblGlobalSummary.setColumnCount(6)
        self.tblGlobalSummary.setObjectName(_fromUtf8("tblGlobalSummary"))
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tblGlobalSummary.setHorizontalHeaderItem(5, item)
        self.tblGlobalSummary.horizontalHeader().setVisible(True)
        self.tblGlobalSummary.horizontalHeader().setDefaultSectionSize(57)
        self.tblGlobalSummary.verticalHeader().setVisible(False)
        self.tblGlobalSummary.verticalHeader().setDefaultSectionSize(20)
        self.tblLocalSummary = QtGui.QTableWidget(Form_Parameter)
        self.tblLocalSummary.setEnabled(True)
        self.tblLocalSummary.setGeometry(QtCore.QRect(4, 364, 361, 181))
        self.tblLocalSummary.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblLocalSummary.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblLocalSummary.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblLocalSummary.setRowCount(0)
        self.tblLocalSummary.setColumnCount(5)
        self.tblLocalSummary.setObjectName(_fromUtf8("tblLocalSummary"))
        item = QtGui.QTableWidgetItem()
        self.tblLocalSummary.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tblLocalSummary.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tblLocalSummary.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tblLocalSummary.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tblLocalSummary.setHorizontalHeaderItem(4, item)
        self.tblLocalSummary.horizontalHeader().setVisible(True)
        self.tblLocalSummary.horizontalHeader().setDefaultSectionSize(68)
        self.tblLocalSummary.horizontalHeader().setMinimumSectionSize(20)
        self.tblLocalSummary.verticalHeader().setVisible(False)
        self.tblLocalSummary.verticalHeader().setDefaultSectionSize(20)
        self.cmbIdColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbIdColumn.setGeometry(QtCore.QRect(84, 27, 91, 22))
        self.cmbIdColumn.setObjectName(_fromUtf8("cmbIdColumn"))
        self.label_4 = QtGui.QLabel(Form_Parameter)
        self.label_4.setGeometry(QtCore.QRect(4, 30, 81, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.progressBar = QtGui.QProgressBar(Form_Parameter)
        self.progressBar.setGeometry(QtCore.QRect(120, 164, 241, 16))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.lbl_log = QtGui.QLabel(Form_Parameter)
        self.lbl_log.setGeometry(QtCore.QRect(5, 188, 361, 16))
        self.lbl_log.setObjectName(_fromUtf8("lbl_log"))
        self.line = QtGui.QFrame(Form_Parameter)
        self.line.setGeometry(QtCore.QRect(0, 180, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_2 = QtGui.QLabel(Form_Parameter)
        self.label_2.setGeometry(QtCore.QRect(100, 348, 61, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lbl_distance = QtGui.QLabel(Form_Parameter)
        self.lbl_distance.setGeometry(QtCore.QRect(160, 348, 51, 16))
        self.lbl_distance.setObjectName(_fromUtf8("lbl_distance"))
        self.btnScatterPlot = QtGui.QPushButton(Form_Parameter)
        self.btnScatterPlot.setGeometry(QtCore.QRect(284, 342, 81, 23))
        self.btnScatterPlot.setObjectName(_fromUtf8("btnScatterPlot"))
        self.btnZDistPlot = QtGui.QPushButton(Form_Parameter)
        self.btnZDistPlot.setGeometry(QtCore.QRect(110, 206, 75, 23))
        self.btnZDistPlot.setObjectName(_fromUtf8("btnZDistPlot"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "Moran\'s I Statistic", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.label_3.setText(_translate("Form_Parameter", "Data Column:", None))
        self.rdoSingle.setText(_translate("Form_Parameter", "Moran\'s I : Single", None))
        self.rdoMultiple.setText(_translate("Form_Parameter", "Moran\'s I : Multiple", None))
        self.lbl_s_1.setText(_translate("Form_Parameter", "Search Distance:", None))
        self.edtSearchDistance.setText(_translate("Form_Parameter", "100000", None))
        self.lbl_m_1.setText(_translate("Form_Parameter", "Critical Z-Value:", None))
        self.edtCritcalZValue.setText(_translate("Form_Parameter", "1.96", None))
        self.gb_multiple.setTitle(_translate("Form_Parameter", "Distance Range", None))
        self.label_6.setText(_translate("Form_Parameter", "From:", None))
        self.edtFrom.setText(_translate("Form_Parameter", "50000", None))
        self.edtTo.setText(_translate("Form_Parameter", "150000", None))
        self.label_7.setText(_translate("Form_Parameter", "To:", None))
        self.label_8.setText(_translate("Form_Parameter", "By:", None))
        self.edtBy.setText(_translate("Form_Parameter", "10000", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.btnSaveResult.setText(_translate("Form_Parameter", "Save Result", None))
        self.btnSaveMap.setText(_translate("Form_Parameter", "Save Map", None))
        self.label_9.setText(_translate("Form_Parameter", "Global Summary:", None))
        self.label_10.setText(_translate("Form_Parameter", "Local Summary:", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(0)
        item.setText(_translate("Form_Parameter", "Distance", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(1)
        item.setText(_translate("Form_Parameter", "I(d)", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(2)
        item.setText(_translate("Form_Parameter", "E[]", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(3)
        item.setText(_translate("Form_Parameter", "V[]", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(4)
        item.setText(_translate("Form_Parameter", "Z[]", None))
        item = self.tblGlobalSummary.horizontalHeaderItem(5)
        item.setText(_translate("Form_Parameter", "P[]", None))
        item = self.tblLocalSummary.horizontalHeaderItem(0)
        item.setText(_translate("Form_Parameter", "ID", None))
        item = self.tblLocalSummary.horizontalHeaderItem(1)
        item.setText(_translate("Form_Parameter", "Value", None))
        item = self.tblLocalSummary.horizontalHeaderItem(2)
        item.setText(_translate("Form_Parameter", "I(d)", None))
        item = self.tblLocalSummary.horizontalHeaderItem(3)
        item.setText(_translate("Form_Parameter", "Z[]", None))
        item = self.tblLocalSummary.horizontalHeaderItem(4)
        item.setText(_translate("Form_Parameter", "P[]", None))
        self.label_4.setText(_translate("Form_Parameter", "ID Column:", None))
        self.lbl_log.setText(_translate("Form_Parameter", "Log Message", None))
        self.label_2.setText(_translate("Form_Parameter", "Distance=", None))
        self.lbl_distance.setText(_translate("Form_Parameter", "10000", None))
        self.btnScatterPlot.setText(_translate("Form_Parameter", "scatter-plot", None))
        self.btnZDistPlot.setText(_translate("Form_Parameter", "Z-dist plot", None))

