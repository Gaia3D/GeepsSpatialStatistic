# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_k_function.ui'
#
# Created: Tue Nov 04 23:02:46 2014
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
        self.btnRun.setGeometry(QtCore.QRect(2, 104, 111, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.btnRun.setFont(font)
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(4, 149, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.progressBar = QtGui.QProgressBar(Form_Parameter)
        self.progressBar.setGeometry(QtCore.QRect(120, 103, 241, 16))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.lbl_log = QtGui.QLabel(Form_Parameter)
        self.lbl_log.setGeometry(QtCore.QRect(120, 119, 241, 20))
        self.lbl_log.setObjectName(_fromUtf8("lbl_log"))
        self.line = QtGui.QFrame(Form_Parameter)
        self.line.setGeometry(QtCore.QRect(0, 130, 361, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.txtResult = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtResult.setGeometry(QtCore.QRect(4, 166, 361, 381))
        self.txtResult.setReadOnly(True)
        self.txtResult.setObjectName(_fromUtf8("txtResult"))
        self.edtNumSimul = QtGui.QLineEdit(Form_Parameter)
        self.edtNumSimul.setGeometry(QtCore.QRect(223, 50, 141, 20))
        self.edtNumSimul.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.edtNumSimul.setObjectName(_fromUtf8("edtNumSimul"))
        self.label_2 = QtGui.QLabel(Form_Parameter)
        self.label_2.setGeometry(QtCore.QRect(4, 53, 211, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btnShowGraph = QtGui.QPushButton(Form_Parameter)
        self.btnShowGraph.setGeometry(QtCore.QRect(284, 140, 81, 23))
        self.btnShowGraph.setObjectName(_fromUtf8("btnShowGraph"))
        self.chkConvexHull = QtGui.QCheckBox(Form_Parameter)
        self.chkConvexHull.setGeometry(QtCore.QRect(5, 80, 151, 16))
        self.chkConvexHull.setChecked(True)
        self.chkConvexHull.setObjectName(_fromUtf8("chkConvexHull"))
        self.label_3 = QtGui.QLabel(Form_Parameter)
        self.label_3.setGeometry(QtCore.QRect(5, 34, 56, 12))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Form_Parameter)
        self.label_4.setGeometry(QtCore.QRect(126, 34, 56, 12))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(Form_Parameter)
        self.label_5.setGeometry(QtCore.QRect(260, 34, 56, 12))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.edtFromH = QtGui.QLineEdit(Form_Parameter)
        self.edtFromH.setGeometry(QtCore.QRect(56, 30, 51, 20))
        self.edtFromH.setObjectName(_fromUtf8("edtFromH"))
        self.edtToH = QtGui.QLineEdit(Form_Parameter)
        self.edtToH.setGeometry(QtCore.QRect(176, 30, 51, 20))
        self.edtToH.setObjectName(_fromUtf8("edtToH"))
        self.edtByH = QtGui.QLineEdit(Form_Parameter)
        self.edtByH.setGeometry(QtCore.QRect(313, 30, 51, 20))
        self.edtByH.setObjectName(_fromUtf8("edtByH"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "K-function", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.label_9.setText(_translate("Form_Parameter", "Result:", None))
        self.lbl_log.setText(_translate("Form_Parameter", "Log Message", None))
        self.edtNumSimul.setText(_translate("Form_Parameter", "99", None))
        self.label_2.setText(_translate("Form_Parameter", "Number of monte carlo simulation:", None))
        self.btnShowGraph.setText(_translate("Form_Parameter", "Show Graph", None))
        self.chkConvexHull.setText(_translate("Form_Parameter", "Draw Convex Hull", None))
        self.label_3.setText(_translate("Form_Parameter", "From H:", None))
        self.label_4.setText(_translate("Form_Parameter", "To H:", None))
        self.label_5.setText(_translate("Form_Parameter", "By H:", None))
        self.edtFromH.setText(_translate("Form_Parameter", "10", None))
        self.edtToH.setText(_translate("Form_Parameter", "20", None))
        self.edtByH.setText(_translate("Form_Parameter", "1", None))

