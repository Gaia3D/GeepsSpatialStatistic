# -*- coding: utf-8 -*-
from PyQt4.QtGui import QMessageBox

# 간단히 메시지 박스 표시
def alert(message, mode=QMessageBox.Information):
    mbx = QMessageBox()
    mbx.setText(message)
    mbx.setIcon(QMessageBox.Information)
    if mode == QMessageBox.Question:
        mbx.setIcon(QMessageBox.Question)
        mbx.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    rc = mbx.exec_()
    return rc

from qgis.core import QgsApplication
from PyQt4.QtCore import QEventLoop

# UI가 갱신될 수 있게 강제 이벤트 처리: 입력은 금지
def forceGuiUpdate():
    QgsApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

