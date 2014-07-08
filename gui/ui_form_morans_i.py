# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_form_morans_i.ui'
#
# Created: Tue Jul 08 14:38:42 2014
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
        Form_Parameter.resize(400, 540)
        self.label = QtGui.QLabel(Form_Parameter)
        self.label.setGeometry(QtCore.QRect(10, 13, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.cmbLayer = QtGui.QComboBox(Form_Parameter)
        self.cmbLayer.setGeometry(QtCore.QRect(100, 10, 291, 22))
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.label_3 = QtGui.QLabel(Form_Parameter)
        self.label_3.setGeometry(QtCore.QRect(10, 43, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cmbTgtColumn = QtGui.QComboBox(Form_Parameter)
        self.cmbTgtColumn.setGeometry(QtCore.QRect(100, 40, 291, 22))
        self.cmbTgtColumn.setObjectName(_fromUtf8("cmbTgtColumn"))
        self.rdoSingle = QtGui.QRadioButton(Form_Parameter)
        self.rdoSingle.setGeometry(QtCore.QRect(10, 70, 141, 16))
        self.rdoSingle.setObjectName(_fromUtf8("rdoSingle"))
        self.rdoMultiple = QtGui.QRadioButton(Form_Parameter)
        self.rdoMultiple.setGeometry(QtCore.QRect(10, 100, 151, 16))
        self.rdoMultiple.setObjectName(_fromUtf8("rdoMultiple"))
        self.label_4 = QtGui.QLabel(Form_Parameter)
        self.label_4.setGeometry(QtCore.QRect(170, 70, 101, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.edtSearchDistance = QtGui.QLineEdit(Form_Parameter)
        self.edtSearchDistance.setGeometry(QtCore.QRect(280, 67, 113, 20))
        self.edtSearchDistance.setObjectName(_fromUtf8("edtSearchDistance"))
        self.label_5 = QtGui.QLabel(Form_Parameter)
        self.label_5.setGeometry(QtCore.QRect(170, 100, 101, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.edtCritcalZValue = QtGui.QLineEdit(Form_Parameter)
        self.edtCritcalZValue.setGeometry(QtCore.QRect(280, 97, 113, 20))
        self.edtCritcalZValue.setObjectName(_fromUtf8("edtCritcalZValue"))
        self.groupBox = QtGui.QGroupBox(Form_Parameter)
        self.groupBox.setGeometry(QtCore.QRect(10, 120, 381, 41))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(10, 16, 41, 16))
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.edtFrom = QtGui.QLineEdit(self.groupBox)
        self.edtFrom.setGeometry(QtCore.QRect(58, 15, 71, 20))
        self.edtFrom.setObjectName(_fromUtf8("edtFrom"))
        self.edtTo = QtGui.QLineEdit(self.groupBox)
        self.edtTo.setGeometry(QtCore.QRect(170, 15, 71, 20))
        self.edtTo.setText(_fromUtf8(""))
        self.edtTo.setObjectName(_fromUtf8("edtTo"))
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(130, 16, 31, 16))
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(260, 16, 31, 16))
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.edtBy = QtGui.QLineEdit(self.groupBox)
        self.edtBy.setGeometry(QtCore.QRect(300, 15, 71, 20))
        self.edtBy.setText(_fromUtf8(""))
        self.edtBy.setObjectName(_fromUtf8("edtBy"))
        self.btnRun = QtGui.QPushButton(Form_Parameter)
        self.btnRun.setGeometry(QtCore.QRect(10, 170, 121, 23))
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.btnSaveChart = QtGui.QPushButton(Form_Parameter)
        self.btnSaveChart.setGeometry(QtCore.QRect(230, 170, 81, 23))
        self.btnSaveChart.setObjectName(_fromUtf8("btnSaveChart"))
        self.btnSaveResult = QtGui.QPushButton(Form_Parameter)
        self.btnSaveResult.setGeometry(QtCore.QRect(310, 170, 81, 23))
        self.btnSaveResult.setObjectName(_fromUtf8("btnSaveResult"))
        self.btnSaveMap = QtGui.QPushButton(Form_Parameter)
        self.btnSaveMap.setGeometry(QtCore.QRect(150, 170, 81, 23))
        self.btnSaveMap.setFlat(False)
        self.btnSaveMap.setObjectName(_fromUtf8("btnSaveMap"))
        self.label_9 = QtGui.QLabel(Form_Parameter)
        self.label_9.setGeometry(QtCore.QRect(10, 200, 131, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.txtGlobalSummary = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtGlobalSummary.setGeometry(QtCore.QRect(10, 216, 381, 111))
        self.txtGlobalSummary.setObjectName(_fromUtf8("txtGlobalSummary"))
        self.label_10 = QtGui.QLabel(Form_Parameter)
        self.label_10.setGeometry(QtCore.QRect(10, 334, 131, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.txtLocalSummary = QtGui.QPlainTextEdit(Form_Parameter)
        self.txtLocalSummary.setGeometry(QtCore.QRect(10, 350, 381, 181))
        self.txtLocalSummary.setObjectName(_fromUtf8("txtLocalSummary"))

        self.retranslateUi(Form_Parameter)
        QtCore.QMetaObject.connectSlotsByName(Form_Parameter)

    def retranslateUi(self, Form_Parameter):
        Form_Parameter.setWindowTitle(_translate("Form_Parameter", "Moran\'s I Statistic", None))
        self.label.setText(_translate("Form_Parameter", "Data Layer:", None))
        self.label_3.setText(_translate("Form_Parameter", "Data Column:", None))
        self.rdoSingle.setText(_translate("Form_Parameter", "Moran\'s I : Single", None))
        self.rdoMultiple.setText(_translate("Form_Parameter", "Moran\'s I : Multiple", None))
        self.label_4.setText(_translate("Form_Parameter", "Search Distance:", None))
        self.label_5.setText(_translate("Form_Parameter", "Critical Z-Value:", None))
        self.groupBox.setTitle(_translate("Form_Parameter", "Distance Range", None))
        self.label_6.setText(_translate("Form_Parameter", "From:", None))
        self.label_7.setText(_translate("Form_Parameter", "To:", None))
        self.label_8.setText(_translate("Form_Parameter", "By:", None))
        self.btnRun.setText(_translate("Form_Parameter", "RUN", None))
        self.btnSaveChart.setText(_translate("Form_Parameter", "Save Chart", None))
        self.btnSaveResult.setText(_translate("Form_Parameter", "Save Result", None))
        self.btnSaveMap.setText(_translate("Form_Parameter", "Save Map", None))
        self.label_9.setText(_translate("Form_Parameter", "Global Summary:", None))
        self.label_10.setText(_translate("Form_Parameter", "Local Summary:", None))

