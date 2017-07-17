# -*- coding: utf-8 -*-
import os.path
import paramiko
import datetime as dt
import time
import psycopg2
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QShortcut, QKeySequence, QProgressBar, QMessageBox
from qgis.core import QgsVectorLayer, QgsDataSourceURI, QgsMapLayerRegistry
from ConfigParser import ConfigParser
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from area_queimada_dialog import AreaQueimadaDialog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AreaQueimada:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.log = self.get_log("/tmp/plugin.txt")
        arquivo_config = os.path.join(BASE_DIR, 'AreaQueimada', 'config.ini')
        print arquivo_config
        self.config_ini = self.arquivo_config(arquivo_config)
        self.set_variaveis()
        self.atalho_teclado()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AreaQueimada_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Área queimada Landsat')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AreaQueimada')
        self.toolbar.setObjectName(u'AreaQueimada')

    def set_variaveis(self):
        print "setando variaveis", self.config_ini
        self.DB = self.config_ini.get("db")
        self.HOST = self.config_ini.get("host")
        self.USER = self.config_ini.get("user")
        self.KEY = self.config_ini.get("key")
        self.PORT = self.config_ini.get("port")
        self.SERVER_RGB = self.config_ini.get("server_rgb")
        self.PATH_RGB = self.config_ini.get("path_rgb")

    def arquivo_config(self, config_file, section='default'):
        config = ConfigParser()
        config.read(config_file)
        options = []
        config_default = {}
        if config.has_section(section):
            options = config.options(section)
        for option in options:
            config_default[option] = config.get(section, option)
        return config_default
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
        return QCoreApplication.translate('AreaQueimada', message)


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
        """Add a toolbar icon to the toolbar.

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

        # Create the dialog (after translation) and keep reference
        self.dlg = AreaQueimadaDialog()

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
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.add_action(
            '/home/cicero/ownCloud/Documents/script_cicero/AreaQueimada/icon.png',
            text=self.tr(u'RGB'),
            callback=self.rgb,
            parent=self.iface.mainWindow()
        )
        self.add_action(
            '/home/cicero/Desktop/favicon.ico',
            text=self.tr(u'AQM - Auditoria'),
            callback=self.auditoria,
            parent=self.iface.mainWindow()
        )
        self.add_action(
            '/home/cicero/ownCloud/Documents/script_cicero/AreaQueimada/r.png',
            text=self.tr(u'Gera Conhecimento - R'),
            callback=self.gera_conhecimento,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Área queimada Landsat'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def gera_conhecimento(self):
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            cena = self.dlg.CENA.text()
            # cena = "LC82250702016119LGN00.tar.bz"
            resultado = self.exec_sql("select gera_conhecimento('%s')" % cena)
            print resultado
            QMessageBox.information(None, "Gera de conhecimento:", "Modelo de conhecimento gerado com sucesso")

    def auditoria(self):
        log = self.get_log("/tmp/plugin.txt")
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            cena = self.dlg.CENA.text()
            # cena = "LC82250702016119LGN00.tar.bz"
            # cicatrizes
            uri = QgsDataSourceURI()
            uri.setConnection(self.HOST, self.PORT, self.DB, self.USER, self.KEY)
            uri.setDataSource("public", "auditada", "geom", "nome_arq='{}'".format(cena))
            uri.setKeyColumn('fid')
            vlayer = QgsVectorLayer(uri.uri(False), "auditada", "postgres")
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            self.iface.mapCanvas().refresh()

    def rgb(self):
        self.dlg.show()
        result = self.dlg.exec_()
        self.iface.messageBar().clearWidgets()
        global progressMessageBar
        global progress
        progressMessageBar = self.iface.messageBar()
        progress = QProgressBar()
        if result:
            cena = self.dlg.CENA.text()
            cena = "LC82250702016119LGN00.tar.bz"

            # dados
            dia = cena[13:16]
            orb_pto = '%s_%s' % (cena[3:6], cena[6:9])
            ano = cena[9:13]
            cod_sat = cena[2]
            data = (dt.datetime(int(ano), 1, 1) + dt.timedelta(days=int(dia) - 1)).strftime("%Y-%m-%d")
            path_download = "{path_rgb}/{cod_sat}/{ano}/{orb_pto}/".format(
                cod_sat=cod_sat, ano=ano, orb_pto=orb_pto, path_rgb=self.PATH_RGB
            )

            # transferencia
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.SERVER_RGB, username=self.USER, password=self.KEY)
            sftp = ssh.open_sftp()
            arquivos = sftp.listdir(path_download)
            todos_rgb = filter(lambda x: x.upper()[-3:] in ('TIF', 'JPG'), arquivos)
            arquivo_data = filter(lambda x: x.count(data) and x.count("RGB"), todos_rgb)
            if arquivo_data:
                rgb = "/tmp/%s" % arquivo_data[0]
                global total
                global valor
                global intervalo
                intervalo = []
                total = 0
                valor = 0
                progress.setMaximum(100)
                progressMessageBar.pushWidget(progress)

                def printTotals(transferred, toBeTransferred):
                    global total
                    global intervalo
                    global valor
                    if not total:
                        total = int(toBeTransferred)
                        parte = total/100
                        for i in range(1, 101):
                            intervalo.append(parte * i)
                        progress.setValue(valor)
                    else:
                        if intervalo and (transferred >= intervalo[0]):
                            valor += 1
                            progress.setValue(valor)
                            intervalo.pop(0)

                sftp.get("%s%s" % (path_download, arquivo_data[0]), rgb, callback=printTotals)
                self.iface.messageBar().clearWidgets()
                self.iface.addRasterLayer(rgb, arquivo_data[0][:-4], "gdal")

            sftp.close()
            ssh.close()
            self.iface.mapCanvas().refresh()

    def get_log(self, nome='/tmp/log.txt'):
        import logging

        fileh = logging.FileHandler(nome, 'a')
        formatter = logging.Formatter(fmt='%(asctime)s PID=%(process)d (%(levelname)s): %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        fileh.setFormatter(formatter)

        log = logging.getLogger()
        log.setLevel(logging.INFO)

        for hdlr in log.handlers[:]:
            log.removeHandler(hdlr)
        log.addHandler(fileh)
        print "Salvando log em: %s" % nome
        return log

    def atalho_teclado(self):
        shortcut1 = QShortcut(QKeySequence(Qt.ALT + Qt.Key_1), self.iface.mainWindow())
        shortcut1.setContext(Qt.ApplicationShortcut)
        shortcut1.activated.connect(self.setVerifica1)

        shortcut3 = QShortcut(QKeySequence(Qt.ALT + Qt.Key_3), self.iface.mainWindow())
        shortcut3.setContext(Qt.ApplicationShortcut)
        shortcut3.activated.connect(self.setVerifica3)

    def setVerifica3(self):
        print "alterando 3"
        if self.iface.activeLayer().name() in ['auditada', 'minerada']:
            print "mudou 3"
            layer = self.iface.activeLayer()
            layer.startEditing()
            for f in layer.selectedFeatures():
                f["verifica"] = 3
                layer.updateFeature(f)
            layer.commitChanges()
            self.iface.setActiveLayer(layer)
        print "nao mudou 3"

    def setVerifica1(self):
        print "alterando 1"
        if self.iface.activeLayer().name() in ['auditada', 'minerada']:
            print "mudou 1"
            layer = self.iface.activeLayer()
            layer.startEditing()
            for f in layer.selectedFeatures():
                f["verifica"] = 1
                layer.updateFeature(f)
            layer.commitChanges()
            self.iface.setActiveLayer(layer)
        print "nao mudou 1"

    def exec_sql(self, sql):
        string_connection = "dbname=%s host=%s user=%s password=%s" % (self.DB, self.HOST, self.USER, self.KEY)
        print 'string_connection', string_connection
        conn = psycopg2.connect(string_connection)
        cur = conn.cursor()
        saida = ""
        try:
            if not sql.strip():
                return "SQL VAZIO E O SQL NAO FOI EXECUTADO"
            cur.execute(sql)
            # print "sql fake"
        except psycopg2.Error as e:
            print e
            conn.rollback()
            raise Exception(e)
        else:
            if cur.rowcount >= 0:
                saida = "%s rows affected" % cur.rowcount
            else:
                saida = "no result"
            conn.commit()
        finally:
            cur.close()
            conn.close()
        return saida