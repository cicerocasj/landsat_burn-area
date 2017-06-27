# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AreaQueimada
                                 A QGIS plugin
 This plugin you can see burn of image Landsat
                             -------------------
        begin                : 2017-06-27
        copyright            : (C) 2017 by Cícero Alves dos Santos Júnior
        email                : cicerocasj@gmail.com
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
    """Load AreaQueimada class from file AreaQueimada.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .area_queimada import AreaQueimada
    return AreaQueimada(iface)
