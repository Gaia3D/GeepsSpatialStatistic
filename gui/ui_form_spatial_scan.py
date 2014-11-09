# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_spatial_scan.ui'
#
# Created: Fri Nov 07 23:01:06 2014
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
        self.cmbLayer.setGeometry(QtCore.QRect(144, 2, 221, 22))
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.label_3 = QtGui.QLabel(Form_Parameter)
        self.label_3.setGeometry(QtCore.QRect(4, 55, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cmbCaseColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbCaseColumn.setGeometry(QtCore.QRect(144, 52, 221, 22))
        self.cmbCaseColumn.setObjectName(_fromUtf8("cmbCaseColumn"))
        self.btnRun = QtGui.QPushButton(Form_Parameter)
        self.btnRun.setGeometry(QtCore.QRect(2, 151, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.btnRun.setFont(font)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.cmbPopColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbPopColumn.setGeometry(QtCore.QRect(144, 27, 221, 22))
        self.cmbPopColumn.setObjectName(_fromUtf8("cmbPopColumn"))
        self.label_4 = QtGui.QLabel(Form_Parameter)
        self.label_4.setGeometry(QtCore.QRect(4, 30, 131, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.progressBar = QtGui.QProgressBar(Form_Parameter)
        self.progressBar.setGeometry(QtCore.QRect(120, 150, 241, 16))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.lbl_log = QtGui.QLabel(Form_Parameter)
        self.lbl_log.setGeometry(QtCore.QRect(120, 166, 241, 20))
        self.lbl_log.setObjectName(_fromUtf8("lbl_log"))
        self.line = QtGui.QFrame(Form_Parameter)
        self.line.setGeometry(QtCore.QRect(0, 177, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_5 = QtGui.QLabel(Form_Parameter)
        self.label_5.setGeometry(QtCore.QRect(5, 97, 211, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.edtNumSimul = QtGui.QLineEdit(Form_Parameter)
        self.edtNumSimul.setGeometry(QtCore.QRect(224, 94, 141, 20))
        self.edtNumSimul.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.edtNumSimul.setObjectName(_fromUtf8("edtNumSimul"))
        self.chkZoneTick = QtGui.QCheckBox(Form_Parameter)
        self.chkZoneTick.setGeometry(QtCore.QRect(210, 120, 151, 16))
        self.chkZoneTick.setChecked(True)
        self.chkZoneTick.setObjectName(_fromUtf8("chkZoneTick"))
        self.chkZoneCircle = QtGui.QCheckBox(Form_Parameter)
        self.chkZoneCircle.setGeometry(QtCore.QRect(10, 120, 151, 16))
        self.chkZoneCircle.setChecked(True)
        self.chkZoneCircle.setObjectName(_fromUtf8("chkZoneCircle"))
        self.txtResult = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtResult.setGeometry(QtCore.QRect(5, 206, 361, 341))
        self.txtResult.setReadOnly(True)
        self.txtResult.setObjectName(_fromUtf8("txtResult"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(5, 190, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "Spatial Scan", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.label_3.setText(_translate("Form_Parameter", "Case Column:", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.label_4.setText(_translate("Form_Parameter", "Population Column:", None))
        self.lbl_log.setText(_translate("Form_Parameter", "Log Message", None))
        self.label_5.setText(_translate("Form_Parameter", "Number of monte carlo simulation:", None))
        self.edtNumSimul.setText(_translate("Form_Parameter", "999", None))
        self.chkZoneTick.setText(_translate("Form_Parameter", "Draw zone tick", None))
        self.chkZoneCircle.setText(_translate("Form_Parameter", "Draw zone circle", None))
        self.label_9.setText(_translate("Form_Parameter", "Result:", None))

