# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_global_morans_i.ui'
#
# Created: Mon Jul 07 18:05:58 2014
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setEnabled(True)
        Dialog.resize(407, 443)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 13, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.cmbLayer = QtGui.QComboBox(Dialog)
        self.cmbLayer.setGeometry(QtCore.QRect(100, 10, 291, 22))
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 100, 381, 81))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.rdoIdw = QtGui.QRadioButton(self.groupBox)
        self.rdoIdw.setGeometry(QtCore.QRect(10, 20, 351, 16))
        self.rdoIdw.setObjectName(_fromUtf8("rdoIdw"))
        self.rdoInDist = QtGui.QRadioButton(self.groupBox)
        self.rdoInDist.setGeometry(QtCore.QRect(10, 40, 351, 16))
        self.rdoInDist.setObjectName(_fromUtf8("rdoInDist"))
        self.rdoContact = QtGui.QRadioButton(self.groupBox)
        self.rdoContact.setGeometry(QtCore.QRect(10, 60, 371, 16))
        self.rdoContact.setObjectName(_fromUtf8("rdoContect"))
        self.btnRun = QtGui.QPushButton(Dialog)
        self.btnRun.setGeometry(QtCore.QRect(10, 232, 381, 31))
        self.btnRun.setObjectName(_fromUtf8("btnRun"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 274, 211, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.txtResult = QtGui.QTextEdit(Dialog)
        self.txtResult.setGeometry(QtCore.QRect(10, 290, 381, 111))
        self.txtResult.setObjectName(_fromUtf8("txtResult"))
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setGeometry(QtCore.QRect(320, 410, 75, 23))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 43, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cmbTgtColumn = QtGui.QComboBox(Dialog)
        self.cmbTgtColumn.setGeometry(QtCore.QRect(100, 40, 291, 22))
        self.cmbTgtColumn.setObjectName(_fromUtf8("cmbTgtColumn"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 73, 81, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cmbIdColumn = QtGui.QComboBox(Dialog)
        self.cmbIdColumn.setGeometry(QtCore.QRect(100, 70, 291, 22))
        self.cmbIdColumn.setObjectName(_fromUtf8("cmbIdColumn"))
        self.ptnShowWeight = QtGui.QPushButton(Dialog)
        self.ptnShowWeight.setGeometry(QtCore.QRect(240, 190, 151, 23))
        self.ptnShowWeight.setObjectName(_fromUtf8("ptnShowWeight"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "전역 모란 I 지수 계산", None))
        self.label.setText(_translate("Dialog", "대상 레이어:", None))
        self.groupBox.setTitle(_translate("Dialog", "가중치 (Weight) 부여 방법", None))
        self.rdoIdw.setText(_translate("Dialog", "거리의 역수(가까운 지역이 영향력 큼. w = 1 / d)", None))
        self.rdoInDist.setText(_translate("Dialog", "일정 거리내 지역을 이웃으로(이웃: 1,  아니면: 0)", None))
        self.rdoContact.setText(_translate("Dialog", "접촉지역을 이웃 지역으로 (폴리곤만 가능. 이웃: 1, 아니면: 0)", None))
        self.btnRun.setText(_translate("Dialog", "분석 실행", None))
        self.label_2.setText(_translate("Dialog", "분석 결과", None))
        self.btnClose.setText(_translate("Dialog", "닫기", None))
        self.label_3.setText(_translate("Dialog", "분석대상 컬럼:", None))
        self.label_4.setText(_translate("Dialog", "지역구분 컬럼:", None))
        self.ptnShowWeight.setText(_translate("Dialog", "지역별 가중치 보기", None))

