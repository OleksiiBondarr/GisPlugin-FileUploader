# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FileUploader
                                 A QGIS plugin
 File Uploader
                              -------------------
        begin                : 2017-08-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Vitaliy Prozur
        email                : .
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from FileUploader_dialog import FileUploaderDialog
import os.path
import subprocess
from qgis.core import QgsMapLayerRegistry
class FileUploader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.quickFinderFile = None
        self.shareDir = None

        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FileUploader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FileUploader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FileUploader')
        self.toolbar.setObjectName(u'FileUploader')

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
        return QCoreApplication.translate('FileUploader', message)


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
        self.dlg = FileUploaderDialog()

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
                self.menu,
                action)

        self.actions.append(action)
        self.city = None
        for item in QgsMapLayerRegistry.instance().mapLayers():
            if 'buildings' in item:
                self.city = item[0:item.find('_')]
        self.dlg.openDir1.setIcon(QIcon(":/icons/icon_path.png"))

        #self.dlg.openDir2.setIcon(QIcon(":/icons/icon_path.png"))
        self.dlg.openDir1.clicked.connect(self.openDirSlot1)
        #self.dlg.openDir2.clicked.connect(self.openDirSlot2)
        self.dlg.btn_upload.clicked.connect(self.saveFileSlot)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/FileUploader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&FileUploader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def saveFileSlot(self):
        try:
            if self.quickFinderFile != None and self.dlg.pathLineEdit2.text():
                try:
            	       import paramiko, sys
                except ImportError:
            	       import subprocess
            	       subprocess.call(["easy_install","paramiko"])
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                time_out = 10000
                ssh.connect("10.112.129.165", 5432, username="yshpylovyi", password="yshpylovyi2017", timeout=time_out)
                #ssh.exec_command('cd /mnt/samba/share')
                sftp = ssh.open_sftp()


                sftp.put(self.quickFinderFile, "/mnt/samba/share/"+self.quickFinderFile[self.quickFinderFile.rfind('/')+1:])




                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Successful upload")

                msg.setWindowTitle("All is ok")
                msg.setDetailedText("File: "+self.quickFinderFile+" successfully uploaded to "+ "/mnt/samba/share/"+self.quickFinderFile[self.quickFinderFile.rfind('/')+1:])
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.exec_()
                ssh.close()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Oops... Something go wrong...")

                msg.setWindowTitle("Oops...")
                msg.setDetailedText("Chek file and path")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.exec_()
        except IOError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Oops... Something go wrong...")

            msg.setWindowTitle("Oops...")
            msg.setDetailedText("Chek your connection")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.exec_()



    def openDirSlot1(self):
        self.quickFinderFile = QFileDialog.getOpenFileName(self.dlg,"Open file","","Quickfinder files (*.qfts)")
        self.dlg.pathLineEdit1.setText(self.quickFinderFile)
        self.dlg.pathLineEdit2.setText("/mnt/samba/share/"+self.quickFinderFile[self.quickFinderFile.rfind('/')+1:])


    def openDirSlot2(self):
        #self.dlg.pathLineEdit2.setText(self.shareDir)
        pass

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
