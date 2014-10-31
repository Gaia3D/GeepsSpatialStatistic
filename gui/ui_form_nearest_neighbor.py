# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_nearest_neighbor.ui'
#
# Created: Fri Oct 31 18:40:11 2014
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
        self.btnRun = QtGui.QPushButton(Form_Parameter)
        self.btnRun.setGeometry(QtCore.QRect(2, 85, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.btnRun.setFont(font)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(4, 130, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.progressBar = QtGui.QProgressBar(Form_Parameter)
        self.progressBar.setGeometry(QtCore.QRect(120, 84, 241, 16))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.lbl_log = QtGui.QLabel(Form_Parameter)
        self.lbl_log.setGeometry(QtCore.QRect(120, 100, 241, 20))
        self.lbl_log.setObjectName(_fromUtf8("lbl_log"))
        self.line = QtGui.QFrame(Form_Parameter)
        self.line.setGeometry(QtCore.QRect(0, 111, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.chkConvexHull = QtGui.QCheckBox(Form_Parameter)
        self.chkConvexHull.setGeometry(QtCore.QRect(10, 30, 151, 16))
        self.chkConvexHull.setChecked(True)
        self.chkConvexHull.setObjectName(_fromUtf8("chkConvexHull"))
        self.chkNearestLine = QtGui.QCheckBox(Form_Parameter)
        self.chkNearestLine.setGeometry(QtCore.QRect(10, 50, 141, 16))
        self.chkNearestLine.setChecked(True)
        self.chkNearestLine.setObjectName(_fromUtf8("chkNearestLine"))
        self.txtResult = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtResult.setGeometry(QtCore.QRect(4, 146, 361, 401))
        self.txtResult.setReadOnly(True)
        self.txtResult.setObjectName(_fromUtf8("txtResult"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "Nearest Neighbor Statistic", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.label_9.setText(_translate("Form_Parameter", "Result:", None))
        self.lbl_log.setText(_translate("Form_Parameter", "Log Message", None))
        self.chkConvexHull.setText(_translate("Form_Parameter", "Draw Convex Hull", None))
        self.chkNearestLine.setText(_translate("Form_Parameter", "Draw Nearest Line", None))

