import qgis.utils
from processing.gui.CommanderWindow import CommanderWindow
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
cw = CommanderWindow(iface.mainWindow(), iface.mapCanvas())
def openAlgorithm3():
    print "alterando 3"
    if iface.activeLayer().name() in ['auditada', 'minerada']:
        print "mudou 3"
        layer = iface.activeLayer()
        layer.startEditing()
        for f in layer.selectedFeatures():
            f["verifica"] = 3
            layer.updateFeature(f)
        layer.commitChanges()
        iface.setActiveLayer(layer)
    print "nao mudou 3"

def openAlgorithm1():
    print "alterando 1"
    if iface.activeLayer().name() in ['auditada', 'minerada']:
        print "mudou 1"
        layer = iface.activeLayer()
        layer.startEditing()
        for f in layer.selectedFeatures():
            f["verifica"] = 1
            layer.updateFeature(f)
        layer.commitChanges()
        iface.setActiveLayer(layer)
    print "nao mudou 1"

shortcut1 = QShortcut(QKeySequence(Qt.Key_1), iface.mainWindow())
shortcut1.setContext(Qt.ApplicationShortcut)
shortcut1.activated.connect(openAlgorithm1)

shortcut3 = QShortcut(QKeySequence(Qt.Key_3), iface.mainWindow())
shortcut3.setContext(Qt.ApplicationShortcut)
shortcut3.activated.connect(openAlgorithm3)