# -*- coding: utf-8 -*-
from PyQt4.QtGui import QMessageBox

def alert(message, mode=QMessageBox.Information):
    mbx = QMessageBox()
    mbx.setText(message)
    mbx.setIcon(QMessageBox.Information)
    if mode == QMessageBox.Question:
        mbx.setIcon(QMessageBox.Question)
        mbx.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    rc = mbx.exec_()
    return rc

