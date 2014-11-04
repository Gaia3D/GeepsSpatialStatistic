# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeepsSpStats
                                 A QGIS plugin
 Spatial Statistics by PySAL
                              -------------------
        begin                : 2014-07-01
        git sha              : $Format:%H$
        copyright            : (C) 2014 by GEEPS / Gaia3D
        email                : geeps.man@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os.path
from Utility import *
from Widget_MoransI import Widget_MoransI
from Widget_GetisOrdsG import Widget_GetisOrdsG
from Widget_NearestNeighbor import Widget_NearestNeighbor
from Widget_KFunction import Widget_KFunction

from Process_NearestNeighbor import Process_NearestNeighbor

class WidgetContainer(object):

    def __init__(self, iface, classTemplet, dockType=Qt.RightDockWidgetArea):
        self.__iface = iface
        self.__dockwidget = None
        self.__oloWidget = None
        self.__classTemplet = classTemplet
        self.__title = classTemplet.title
        self.__objectName = classTemplet.objectName
        self.__dockType = dockType

    # Private
    def __setDocWidget(self):
        self.__dockwidget = QDockWidget(self.__title, self.__iface.mainWindow() )
        self.__dockwidget.setObjectName(self.__objectName)
        self.__oloWidget = self.__classTemplet(self.__iface, self.__dockwidget)
        self.__dockwidget.setWidget(self.__oloWidget)
        self.__oloWidget.updateGuiLayerList()

    def __initGui(self):
        self.__setDocWidget()
        self.__iface.addDockWidget(self.__dockType, self.__dockwidget)

    def __unload(self):
        self.__dockwidget.close()
        self.__iface.removeDockWidget( self.__dockwidget )
        # 이벤트 헨들러가 자동제거 되지 않아 강제로 제거
        self.__oloWidget.disconnectGlobalSignal()
        del self.__oloWidget
        self.__dockwidget = None

    # Public
    def setVisible(self, visible):
        if visible:
            if self.__dockwidget is None:
                self.__initGui()
        else:
            if not self.__dockwidget is None:
                self.__unload()
    # TODO: reflash
    def repaint(self):
        if self.__dockwidget:
            self.__dockwidget.update()
            self.__dockwidget.repaint()


### QGIS Plugin Implementation.
class GeepsSpStats:
    crrWidget = None

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # reference to map canvas
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeepsSpStats_{}.qm'.format(locale))
        # 한국어는 GeepsSpStats_ko.qm 파일이 필요

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Overview
        #self.crrWidget = WidgetContainer(iface, Widget_MoransI)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """

        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeepsSpStats', message)


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Qt에서는 Action이 메뉴의 최종 아이템이라 생각하면 됨
        actions = self.iface.mainWindow().menuBar().actions()

        self.mainMenu = QMenu(self.iface.mainWindow())
        self.mainMenu.setTitle(self.tr(u'Spatial Statics'))

        # 이미 메뉴가 있다면 그냥 있는 것 이용
        for action in actions:
            if action.text() == self.tr(u'Spatial Statics'):
                self.mainMenu = action.menu()
                break

        ### MENU1 : spatial clusters detection
        icon = QIcon(os.path.dirname(__file__) + "/images/publish-to-geonode.png")
        self.menu1 = self.mainMenu.addMenu(icon, self.tr(u'Spatial Autocorrelation'))
        self.mainMenu.addMenu(self.menu1)

        # Moran's I Statistic Menu
        self.moransI_Action = QAction(self.tr("Moran's I Statistic"), self.iface.mainWindow())
        self.menu1.addAction(self.moransI_Action)
        self.moransI_Action.triggered.connect(self.showWidgetMoransI)

        ### MENU2 : Spatial Clustering
        icon = QIcon(os.path.dirname(__file__) + "/images/tree.png")
        self.menu2 = self.mainMenu.addMenu(icon, self.tr(u'Spatial Clustering'))
        self.mainMenu.addMenu(self.menu2)

        # Getis-Ord's G Statistic Menu
        self.getisOrdsG_Action = QAction(self.tr("Getis-Ord's G Statistic"), self.iface.mainWindow())
        self.menu2.addAction(self.getisOrdsG_Action)
        self.getisOrdsG_Action.triggered.connect(self.showWidgetGetisOrdsG)

        # Nearest neighbor statistic Menu
        self.nearestNeighborStatistic_Action  = QAction( self.tr(u"Nearest Neighbor Statistic"), self.menu2)
        self.menu2.addAction(self.nearestNeighborStatistic_Action)
        self.nearestNeighborStatistic_Action.triggered.connect(self.showWidgetNearestNeighbor)

        # K-function Menu
        self.Kfunction_Action  = QAction(self.tr(u"K-function"), self.menu2)
        self.menu2.addAction(self.Kfunction_Action)
        self.Kfunction_Action.triggered.connect(self.showWidgetKFunction)

        ### MENU3 : Spatiotemporal Clustering
        icon = QIcon(os.path.dirname(__file__) + "/images/workspace.png")
        self.menu3 = self.mainMenu.addMenu(icon, self.tr(u'Spatiotemporal Clustering'))
        self.mainMenu.addMenu(self.menu3)

        # Knox statistic Menu
        self.knoxStatistic_Action = QAction(self.tr(u"Knox Statistic"), self.menu3)
        self.menu3.addAction(self.knoxStatistic_Action)
        self.knoxStatistic_Action.triggered.connect(self.run)

        ### MENU4 : spatial clusters detection
        icon = QIcon(os.path.dirname(__file__) + "/images/view.png")
        self.menu4 = self.mainMenu.addMenu(icon, self.tr(u'Spatial Clusters Detection'))
        self.mainMenu.addMenu(self.menu4)

        # Knox statistic Menu
        self.spatialScanStatistic_Action = QAction(self.tr(u"Spatial Scan Statistic"), self.menu4)
        self.menu4.addAction(self.spatialScanStatistic_Action)
        self.spatialScanStatistic_Action.triggered.connect(self.run)

        ### HELP
        icon = QIcon(os.path.dirname(__file__) + "/images/help.png")
        self.help_Action  = QAction(icon, self.tr(u"About GEEPS Spatial Stats"), self.menu1)
        self.mainMenu.addAction(self.help_Action)
        self.help_Action.triggered.connect(self.run)

        ### Main Menu 등록
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.mainMenu)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.mainMenu.deleteLater()
        if not self.crrWidget is None:
            self.crrWidget.setVisible( False )
            del self.crrWidget
            self.crrWidget = None

    def getLayerList(self):
        retLayerList = []
        for layer in self.canvas.layers():
            retLayerList.append(layer.name())
        return retLayerList


    def showWidgetMoransI(self):
        if not self.crrWidget is None:
            self.crrWidget.setVisible(False)
            del self.crrWidget
            self.crrWidget = None
        self.crrWidget = WidgetContainer(self.iface, Widget_MoransI)
        self.crrWidget.setVisible(True)
        # TODO: UI reflash
        self.crrWidget.repaint()
        pass

    def showWidgetGetisOrdsG(self):
        if not self.crrWidget is None:
            self.crrWidget.setVisible(False)
            del self.crrWidget
            self.crrWidget = None
        self.crrWidget = WidgetContainer(self.iface, Widget_GetisOrdsG)
        self.crrWidget.setVisible(True)
        pass

    def showWidgetNearestNeighbor(self):
        if not self.crrWidget is None:
            self.crrWidget.setVisible(False)
            del self.crrWidget
            self.crrWidget = None
        self.crrWidget = WidgetContainer(self.iface, Widget_NearestNeighbor)
        self.crrWidget.setVisible(True)
        pass

    def showWidgetKFunction(self):
        if not self.crrWidget is None:
            self.crrWidget.setVisible(False)
            del self.crrWidget
            self.crrWidget = None
        self.crrWidget = WidgetContainer(self.iface, Widget_KFunction)
        self.crrWidget.setVisible(True)
        pass

    def run(self):
        alert("Under Construction!!!")