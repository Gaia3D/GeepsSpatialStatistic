# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_knox_statistic.ui'
#
# Created: Fri Nov 07 20:28:18 2014
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
        self.label.setGeometry(QtCore.QRect(5, 5, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.cmbLayer = QtGui.QComboBox(Form_Parameter)
        self.cmbLayer.setGeometry(QtCore.QRect(94, 2, 271, 22))
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.cmbTimeColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbTimeColumn.setGeometry(QtCore.QRect(94, 26, 271, 22))
        self.cmbTimeColumn.setObjectName(_fromUtf8("cmbTimeColumn"))
        self.label_4 = QtGui.QLabel(Form_Parameter)
        self.label_4.setGeometry(QtCore.QRect(4, 29, 91, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(6, 180, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.progressBar = QtGui.QProgressBar(Form_Parameter)
        self.progressBar.setGeometry(QtCore.QRect(122, 139, 241, 16))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.edtNumSimul = QtGui.QLineEdit(Form_Parameter)
        self.edtNumSimul.setGeometry(QtCore.QRect(225, 77, 141, 20))
        self.edtNumSimul.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.edtNumSimul.setObjectName(_fromUtf8("edtNumSimul"))
        self.chkConvexHull = QtGui.QCheckBox(Form_Parameter)
        self.chkConvexHull.setGeometry(QtCore.QRect(210, 110, 151, 16))
        self.chkConvexHull.setChecked(True)
        self.chkConvexHull.setObjectName(_fromUtf8("chkConvexHull"))
        self.line = QtGui.QFrame(Form_Parameter)
        self.line.setGeometry(QtCore.QRect(2, 166, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.txtResult = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtResult.setGeometry(QtCore.QRect(6, 196, 361, 351))
        self.txtResult.setReadOnly(True)
        self.txtResult.setObjectName(_fromUtf8("txtResult"))
        self.lbl_log = QtGui.QLabel(Form_Parameter)
        self.lbl_log.setGeometry(QtCore.QRect(122, 155, 241, 20))
        self.lbl_log.setObjectName(_fromUtf8("lbl_log"))
        self.label_2 = QtGui.QLabel(Form_Parameter)
        self.label_2.setGeometry(QtCore.QRect(6, 80, 211, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btnRun = QtGui.QPushButton(Form_Parameter)
        self.btnRun.setGeometry(QtCore.QRect(4, 140, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.btnRun.setFont(font)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.chkBoundPoint = QtGui.QCheckBox(Form_Parameter)
        self.chkBoundPoint.setGeometry(QtCore.QRect(10, 110, 151, 16))
        self.chkBoundPoint.setChecked(True)
        self.chkBoundPoint.setObjectName(_fromUtf8("chkBoundPoint"))
        self.edtTimeBound = QtGui.QLineEdit(Form_Parameter)
        self.edtTimeBound.setGeometry(QtCore.QRect(294, 50, 71, 20))
        self.edtTimeBound.setText(_fromUtf8(""))
        self.edtTimeBound.setObjectName(_fromUtf8("edtTimeBound"))
        self.edtDistBound = QtGui.QLineEdit(Form_Parameter)
        self.edtDistBound.setGeometry(QtCore.QRect(120, 50, 71, 20))
        self.edtDistBound.setText(_fromUtf8(""))
        self.edtDistBound.setObjectName(_fromUtf8("edtDistBound"))
        self.label_5 = QtGui.QLabel(Form_Parameter)
        self.label_5.setGeometry(QtCore.QRect(210, 52, 81, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_3 = QtGui.QLabel(Form_Parameter)
        self.label_3.setGeometry(QtCore.QRect(6, 52, 101, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "Knox Statistic", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.label_4.setText(_translate("Form_Parameter", "Time Column:", None))
        self.label_9.setText(_translate("Form_Parameter", "Result:", None))
        self.edtNumSimul.setText(_translate("Form_Parameter", "999", None))
        self.chkConvexHull.setText(_translate("Form_Parameter", "Draw Convex Hull", None))
        self.lbl_log.setText(_translate("Form_Parameter", "Log Message", None))
        self.label_2.setText(_translate("Form_Parameter", "Number of monte carlo simulation:", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.chkBoundPoint.setText(_translate("Form_Parameter", "Draw in bound Points", None))
        self.label_5.setText(_translate("Form_Parameter", "Time Bound:", None))
        self.label_3.setText(_translate("Form_Parameter", "Distance Bound:", None))

