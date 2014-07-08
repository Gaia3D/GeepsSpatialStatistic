# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeepsSpStats
                                 A QGIS plugin
 Spatial Statistics by PySAL
                             -------------------
        begin                : 2014-07-01
        copyright            : (C) 2014 by GEEPS / Gaia3D
        email                : geeps.man@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeepsSpStats class from file GeepsSpStats.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mainPlugin import GeepsSpStats
    return GeepsSpStats(iface)
