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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import *
from qgis.core import QgsMessageLog

# Initialize Qt resources from file resources.py
#import resources_rc
# Import the code for the dialog
from GeepsSpStats.gui import dlgGlobalMoransI
from plugin_dialog import GeepsSpStatsDialog
from GeepsSpStats.gui.dlgGlobalMoransI import Dlg_GlobalMoransI
import os.path


class GeepsSpStats:
    """QGIS Plugin Implementation."""
    dlgGlobalMoransI = None

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

        # Create the dialog (after translation) and keep reference
        self.dlg = GeepsSpStatsDialog()



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


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.mainMenu,
                action)

        self.actions.append(action)

        return action

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

        ### MENU1 : spatial autocorrelation
        self.menu1 = self.mainMenu.addMenu(self.tr(u'Spatial Autocorrelation'))
        self.mainMenu.addMenu(self.menu1)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.globalMoransI_Action  = QAction(icon, self.tr(u"Global Moran's I Statistic"), self.menu1)
        self.menu1.addAction(self.globalMoransI_Action)
        self.globalMoransI_Action.triggered.connect(self.showDlgGlobalMoransI)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.localMoransI_Action  = QAction(icon, self.tr(u"Local Moran's I Statistic"), self.menu1)
        self.menu1.addAction(self.localMoransI_Action)
        self.localMoransI_Action.triggered.connect(self.run)


        ### MENU2 : spatial clustering
        self.menu2 = self.mainMenu.addMenu(self.tr(u'Spatial Clustering'))
        self.mainMenu.addMenu(self.menu2)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.globalG_Action  = QAction(icon, self.tr(u"Global G Statistic"), self.menu2)
        self.menu2.addAction(self.globalG_Action)
        self.globalG_Action.triggered.connect(self.run)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.localG_Action  = QAction(icon, self.tr(u"Local G Statistic"), self.menu2)
        self.menu2.addAction(self.localG_Action)
        self.localG_Action.triggered.connect(self.run)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.nearestNeighbor_Action  = QAction(icon, self.tr(u"Nearest Neighbor Statistic"), self.menu2)
        self.menu2.addAction(self.nearestNeighbor_Action)
        self.nearestNeighbor_Action.triggered.connect(self.run)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.KFunction_Action  = QAction(icon, self.tr(u"K-function"), self.menu2)
        self.menu2.addAction(self.KFunction_Action)
        self.KFunction_Action.triggered.connect(self.run)


        ### MENU3 : spatiotemporal clustering
        self.menu3 = self.mainMenu.addMenu(self.tr(u'Spatiotemporal Clustering'))
        self.mainMenu.addMenu(self.menu3)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.knoxStatistic_Action  = QAction(icon, self.tr(u"Knox Statistic"), self.menu1)
        self.menu3.addAction(self.knoxStatistic_Action)
        self.knoxStatistic_Action.triggered.connect(self.run)


        ### MENU4 : spatial clusters detection
        self.menu4 = self.mainMenu.addMenu(self.tr(u'Spatial Clusters Detection'))
        self.mainMenu.addMenu(self.menu4)

        icon = QIcon(os.path.dirname(__file__) + "/icon.png")
        self.spatialScanStatistic_Action  = QAction(icon, self.tr(u"Spatial Scan Statistic"), self.menu1)
        self.menu4.addAction(self.spatialScanStatistic_Action)
        self.spatialScanStatistic_Action.triggered.connect(self.run)


        ### HELP
        icon = QIcon(os.path.dirname(__file__) + "/images/help.png")
        self.help_Action  = QAction(icon, self.tr(u"About GEEPS Spatial Stats"), self.menu1)
        self.mainMenu.addAction(self.help_Action)
        self.help_Action.triggered.connect(self.showDlgGlobalMoransI)


        ### Main Menu 등록
        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.mainMenu)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.mainMenu.deleteLater()


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def getLayerList(self):
        retLayerList = []
        for layer in self.canvas.layers():
            retLayerList.append(layer.name())
        return retLayerList

    def showDlgGlobalMoransI(self):
        # Create the dialog (after translation) and keep reference
        if (not self.dlgGlobalMoransI):
            self.dlgGlobalMoransI = Dlg_GlobalMoransI(self.iface)
        self.dlgGlobalMoransI.fillLayerList(self.getLayerList())
        self.dlgGlobalMoransI.show()
        result = self.dlgGlobalMoransI.exec_()
        # See if OK was pressed
        if result:
            pass
