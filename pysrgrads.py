# author: jjr4P
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication,QFileDialog
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import sys
import os
import time


pathGrads = "$HOME/GRADS/opengrads/Contents"


class CtlFile:
    def __init__(self, path):
        ivar = False
        tmpDef = False
        with open(path, "r") as ctl:
            datos = ctl.readlines()
            lastCommand = ""
            for line in datos:
                line = line[:-1].split(" ")
                if len(line[0]) < 1 and len(line) == 1:
                    continue
                elif tmpDef:
                    line = CtlFile.removeEmpty(line)
                try:
                    if line[0][0] != '*' and not ivar:
                        command = line[0].upper()
                        if command == "DSET" or command == "INDEX":
                            self.__dict__[command] = CtlFile.removeEmpty(line)[1][1:]
                        elif command == "OPTIONS" or command == "UNDEF" or command == "DTYPE":
                            self.__dict__[command] = CtlFile.removeEmpty(line)[1]
                        elif command == "TITLE":
                            self.__dict__[command] = " ".join(CtlFile.removeEmpty(line)[1:])
                        elif command.endswith("DEF"):
                            lastCommand = command
                            line = CtlFile.removeEmpty(line)[1:]
                            if command == "TDEF":
                                self.__dict__[command] = {'nvalues':int(line[0]), 'type':line[1].upper(), 'init':line[2], 'step':line[3]}
                            else:
                                tmpDef = True
                                self.__dict__[command] = CtlFile.convertDEFs(line)
                                if not command in self.__dict__.keys():
                                    tmpDef = False
                        elif command == "VARS":
                            ivar = True
                            self.__dict__[command] = {'nvars':int(line[1])}
                        else:                       
                            if tmpDef:
                                data = list(map(float, line))               
                                self.__dict__[lastCommand]["values"].extend(data)
                                values = self.__dict__[lastCommand]["values"]
                                self.__dict__[lastCommand]["min"] = min(values)
                                self.__dict__[lastCommand]["max"] = max(values)
                    elif ivar:
                        line = CtlFile.removeEmpty(line)
                        var = line[0]
                        if var.upper() == "ENDVARS":
                            break
                        try:
                            self.__dict__["VARS"][var] = [float(line[1]), line[2], " ".join(line[3:])]
                        except Exception as ee:
                            self.__dict__["VARS"][var] = [line[1], line[2], " ".join(line[3:])]
                except Exception as e:
                    print(line, e)
                    print(self.__dict__)
                    raise e
        

    def removeEmpty(lWords):
        while '' in lWords:
            lWords.remove('')
        return lWords

    def convertDEFs(lDEFs):
        data = {"nvalues":int(lDEFs[0]), "type":lDEFs[1].upper(), "min":None,
                "max":None, "values":[]}

        if(data["type"] == "LINEAR"):
            data["min"] = float(lDEFs[2])
            step = float(lDEFs[3])
            data["max"] = float(data["min"] + (int(lDEFs[0])-1)*step)

        elif data["type"] == 'LEVELS':
            lvls = list(map(float, lDEFs[2:]))
            data["values"] = lvls
            if len(lvls) > 0 :
                data["min"] = min(lvls)
                data["max"] = max(lvls)

        return data



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1123, 750)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setStyleSheet("background-color: rgb(211, 215, 207);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnGenGraph = QtWidgets.QCommandLinkButton(self.centralwidget)
        self.btnGenGraph.setGeometry(QtCore.QRect(90, 620, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.btnGenGraph.setFont(font)
        self.btnGenGraph.setObjectName("btnGenGraph")
        self.listVars = QtWidgets.QListWidget(self.centralwidget)
        self.listVars.setGeometry(QtCore.QRect(20, 300, 131, 211))
        self.listVars.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.listVars.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listVars.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.listVars.setSelectionRectVisible(True)
        self.listVars.setObjectName("listVars")
        self.lblTitle = QtWidgets.QLabel(self.centralwidget)
        self.lblTitle.setGeometry(QtCore.QRect(20, 10, 1001, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lblTitle.setFont(font)
        self.lblTitle.setStyleSheet("")
        self.lblTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitle.setObjectName("lblTitle")
        self.lblTitle_2 = QtWidgets.QLabel(self.centralwidget)
        self.lblTitle_2.setGeometry(QtCore.QRect(20, 270, 91, 17))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lblTitle_2.setFont(font)
        self.lblTitle_2.setObjectName("lblTitle_2")
        self.treeDesc = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeDesc.setGeometry(QtCore.QRect(20, 51, 311, 201))
        self.treeDesc.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.treeDesc.setObjectName("treeDesc")
        self.treeDesc.header().setDefaultSectionSize(120)
        self.treeDesc.header().setMinimumSectionSize(70)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(160, 270, 51, 17))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.cmbGxout = QtWidgets.QComboBox(self.centralwidget)
        self.cmbGxout.setGeometry(QtCore.QRect(220, 264, 111, 31))
        self.cmbGxout.setStyleSheet("background-color: rgb(114, 159, 207);\n"
        "selection-background-color: rgb(136, 138, 133);")
        self.cmbGxout.setObjectName("cmbGxout")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.cmbGxout.addItem("")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(340, 40, 771, 631))
        self.tabWidget.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.lblGraphic = QtWidgets.QLabel(self.tab)
        self.lblGraphic.setGeometry(QtCore.QRect(10, 10, 750, 580))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lblGraphic.setFont(font)
        self.lblGraphic.setStyleSheet("border: 2px solid blue;")
        self.lblGraphic.setText("")
        self.lblGraphic.setAlignment(QtCore.Qt.AlignCenter)
        self.lblGraphic.setObjectName("lblGraphic")
        self.btnSaveGraphic = QtWidgets.QCommandLinkButton(self.tab)
        self.btnSaveGraphic.setEnabled(False)
        self.btnSaveGraphic.setGeometry(QtCore.QRect(680, 540, 60, 30))
        self.btnSaveGraphic.setText("Save")
        self.btnSaveGraphic.setObjectName("btnSaveGraphic")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.txtScript = QtWidgets.QPlainTextEdit(self.tab_2)
        self.txtScript.setGeometry(QtCore.QRect(10, 10, 751, 521))
        self.txtScript.setStyleSheet("background-color: rgb(85, 87, 83);\n"
        "color: rgb(255, 255, 255);\n"
        "font: 15pt \"Ubuntu Mono\";\n"
        "border: 2px solid blue;")
        self.txtScript.setPlainText("")
        self.txtScript.setObjectName("txtScript")
        self.btnRunScript = QtWidgets.QCommandLinkButton(self.tab_2)
        self.btnRunScript.setGeometry(QtCore.QRect(320, 550, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.btnRunScript.setFont(font)
        self.btnRunScript.setObjectName("btnRunScript")
        self.btnSaveScript = QtWidgets.QCommandLinkButton(self.tab_2)
        self.btnSaveScript.setEnabled(False)
        self.btnSaveScript.setGeometry(QtCore.QRect(680, 540, 60, 30))
        self.btnSaveScript.setText("Save")
        self.btnSaveScript.setObjectName("btnSaveScript")
        self.tabWidget.addTab(self.tab_2, "")
        self.checkSameG = QtWidgets.QCheckBox(self.centralwidget)
        self.checkSameG.setGeometry(QtCore.QRect(20, 520, 121, 41))
        self.checkSameG.setObjectName("checkSameG")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(160, 310, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(160, 340, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(160, 380, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(160, 410, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.minLon = QtWidgets.QSpinBox(self.centralwidget)
        self.minLon.setGeometry(QtCore.QRect(250, 310, 81, 26))
        self.minLon.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.minLon.setMinimum(-180)
        self.minLon.setMaximum(180)
        self.minLon.setProperty("value", -180)
        self.minLon.setObjectName("minLon")
        self.maxLon = QtWidgets.QSpinBox(self.centralwidget)
        self.maxLon.setGeometry(QtCore.QRect(250, 340, 81, 26))
        self.maxLon.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.maxLon.setMinimum(-180)
        self.maxLon.setMaximum(180)
        self.maxLon.setProperty("value", 180)
        self.maxLon.setObjectName("maxLon")
        self.minLat = QtWidgets.QSpinBox(self.centralwidget)
        self.minLat.setGeometry(QtCore.QRect(250, 380, 81, 26))
        self.minLat.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.minLat.setMinimum(-90)
        self.minLat.setMaximum(90)
        self.minLat.setProperty("value", -90)
        self.minLat.setObjectName("minLat")
        self.maxLat = QtWidgets.QSpinBox(self.centralwidget)
        self.maxLat.setGeometry(QtCore.QRect(250, 410, 81, 26))
        self.maxLat.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.maxLat.setMinimum(-90)
        self.maxLat.setMaximum(90)
        self.maxLat.setProperty("value", 90)
        self.maxLat.setObjectName("maxLat")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(160, 482, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(160, 450, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.minTime = QtWidgets.QSpinBox(self.centralwidget)
        self.minTime.setGeometry(QtCore.QRect(250, 450, 81, 26))
        self.minTime.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.minTime.setMinimum(1)
        self.minTime.setObjectName("minTime")
        self.maxTime = QtWidgets.QSpinBox(self.centralwidget)
        self.maxTime.setGeometry(QtCore.QRect(250, 480, 81, 26))
        self.maxTime.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.maxTime.setMinimum(1)
        self.maxTime.setObjectName("maxTime")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(160, 520, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.spinLev = QtWidgets.QSpinBox(self.centralwidget)
        self.spinLev.setGeometry(QtCore.QRect(250, 520, 81, 26))
        self.spinLev.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.spinLev.setObjectName("spinLev")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(740, 680, 381, 20))
        self.label_9.setObjectName("label_9")
        self.tabWidget.raise_()
        self.btnGenGraph.raise_()
        self.listVars.raise_()
        self.lblTitle.raise_()
        self.lblTitle_2.raise_()
        self.treeDesc.raise_()
        self.label.raise_()
        self.cmbGxout.raise_()
        self.checkSameG.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.label_4.raise_()
        self.label_5.raise_()
        self.minLon.raise_()
        self.maxLon.raise_()
        self.minLat.raise_()
        self.maxLat.raise_()
        self.label_6.raise_()
        self.label_7.raise_()
        self.minTime.raise_()
        self.maxTime.raise_()
        self.label_8.raise_()
        self.spinLev.raise_()
        self.label_9.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1123, 25))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.menubar.setFont(font)
        self.menubar.setStyleSheet("background-color: rgb(136, 138, 133);\n"
        "selection-background-color: rgb(114, 159, 207);")
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.statusbar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.statusbar.setStyleSheet("background-color: rgb(211, 215, 207);")
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpenFile = QtWidgets.QAction(MainWindow)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionOpen_recents = QtWidgets.QAction(MainWindow)
        self.actionOpen_recents.setEnabled(False)
        self.actionOpen_recents.setObjectName("actionOpen_recents")
        self.actionOpenScript = QtWidgets.QAction(MainWindow)
        self.actionOpenScript.setObjectName("actionOpenScript")
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addAction(self.actionOpenScript)
        self.menuFile.addAction(self.actionOpen_recents)
        self.menuFile.addSeparator()
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.cmbGxout.setCurrentIndex(-1)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Script Runner Grads"))
        self.btnGenGraph.setText(_translate("MainWindow", "Make graphic"))
        self.lblTitle.setText(_translate("MainWindow", "Title:"))
        self.lblTitle_2.setText(_translate("MainWindow", "Variables:"))
        self.treeDesc.headerItem().setText(0, _translate("MainWindow", "Property"))
        self.treeDesc.headerItem().setText(1, _translate("MainWindow", "Value"))
        self.label.setText(_translate("MainWindow", "Gxout:"))
        self.cmbGxout.setItemText(0, _translate("MainWindow", "bar"))
        self.cmbGxout.setItemText(1, _translate("MainWindow", "barb"))
        self.cmbGxout.setItemText(2, _translate("MainWindow", "contour"))
        self.cmbGxout.setItemText(3, _translate("MainWindow", "errbar"))
        self.cmbGxout.setItemText(4, _translate("MainWindow", "geotiff"))
        self.cmbGxout.setItemText(5, _translate("MainWindow", "grfill"))
        self.cmbGxout.setItemText(6, _translate("MainWindow", "grid"))
        self.cmbGxout.setItemText(7, _translate("MainWindow", "line"))
        self.cmbGxout.setItemText(8, _translate("MainWindow", "linefill"))
        self.cmbGxout.setItemText(9, _translate("MainWindow", "scatter"))
        self.cmbGxout.setItemText(10, _translate("MainWindow", "shaded"))
        self.cmbGxout.setItemText(11, _translate("MainWindow", "shade1"))
        self.cmbGxout.setItemText(12, _translate("MainWindow", "shade2"))
        self.cmbGxout.setItemText(13, _translate("MainWindow", "shade2b"))
        self.cmbGxout.setItemText(14, _translate("MainWindow", "stream"))
        self.cmbGxout.setItemText(15, _translate("MainWindow", "stat"))
        self.cmbGxout.setItemText(16, _translate("MainWindow", "vector"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Graphic"))
        self.btnRunScript.setText(_translate("MainWindow", "Run script"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Script Runner"))
        self.checkSameG.setText(_translate("MainWindow", "Same graphic"))
        self.label_2.setToolTip(_translate("MainWindow", "Longitude minimum"))
        self.label_2.setText(_translate("MainWindow", "Min. Long.:"))
        self.label_3.setToolTip(_translate("MainWindow", "Longitude maximum"))
        self.label_3.setText(_translate("MainWindow", "Max. Long.:"))
        self.label_4.setToolTip(_translate("MainWindow", "Latitude minimum"))
        self.label_4.setText(_translate("MainWindow", "Min. Lati.:"))
        self.label_5.setToolTip(_translate("MainWindow", "Latitude maximum"))
        self.label_5.setText(_translate("MainWindow", "Max. Lati.:"))
        self.label_6.setToolTip(_translate("MainWindow", "Latitude maximum"))
        self.label_6.setText(_translate("MainWindow", "Max. Time:"))
        self.label_7.setToolTip(_translate("MainWindow", "Latitude minimum"))
        self.label_7.setText(_translate("MainWindow", "Min. Time:"))
        self.label_8.setText(_translate("MainWindow", "Value Lev.:"))
        self.label_9.setText(_translate("MainWindow", "Creado por Julio Raime Perez - Meteorologia - UNMSM"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open ctl/grb file"))
        self.actionOpenFile.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionOpen_recents.setText(_translate("MainWindow", "Open recents"))
        self.actionOpenScript.setText(_translate("MainWindow", "Open script gs"))



class SRGradsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SRGradsWindow, self).__init__()
        uic.loadUi('ScriptRunnerGrads.ui', self)
        #uic.loadUi('ScriptRunnerGrads.ui', self)
        self.ctlFile = None
        self.actionOpenFile.triggered.connect(self.openFile)
        self.actionOpenScript.triggered.connect(self.openScript)
        self.btnGenGraph.clicked.connect(self.generateGraphic)
        self.btnRunScript.clicked.connect(self.runScript)
        self.btnSaveGraphic.clicked.connect(self.saveGraphic)
        self.btnSaveScript.clicked.connect(self.saveScript)
        self.show()

    def openScript(self):
        self.fpath,_ = QFileDialog.getOpenFileName(self, 'Open script', os.getcwd(), "Script GRADS(*.gs)")
        if len(self.fpath) > 0:
            if self.fpath.endswith('.gs'):
                with open(self.fpath) as f:
                    lines = f.readlines()
                    txt = ""
                    for line in lines:
                        txt += line
                    self.txtScript.setPlainText(txt)
                    self.tabWidget.setCurrentIndex(1)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("File not supported")
                msg.setInformativeText('Only .gs files are supports')
                msg.setWindowTitle("Error when open file")
                msg.exec_()

    def openFile(self):
        self.fpath,_ = QFileDialog.getOpenFileName(self, 'Open file', os.getcwd(), "Ctl/Grib files(*.*)")
        if len(self.fpath) > 0:
            if self.fpath.endswith('.ctl'):
                self.openCtlFile(self.fpath)
                
            elif self.fpath.endswith('.grb'):
                QApplication.setOverrideCursor(Qt.WaitCursor)
                file = self.convertGribFile(self.fpath).split("/")[-1]                
                QApplication.restoreOverrideCursor()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("File converted")
                msg.setInformativeText(f"Open file: {file}")
                msg.setWindowTitle("Convert file to CTL")
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("File not supported")
                msg.setInformativeText('Only ctl or grb files are supports')
                msg.setWindowTitle("Error when open file")
                msg.exec_()

    def openCtlFile(self, pathF):
        print(pathF)
        self.ctlFile = CtlFile(pathF)
        self.fillInData()
        self.directory = "/".join(pathF.split('/')[:-1])
        os.chdir(self.directory)

    def fillInData(self):
        datos = self.ctlFile.__dict__
        title = datos["TITLE"]
        items = []
        # Upload description
        self.lblTitle.setText("Title: " + title)
        for key, value in datos.items():
            if key != "TITLE":
                if type(value) != dict:
                    item = QTreeWidgetItem([key, value])
                else:
                    item = QTreeWidgetItem([key])
                    for s_key, s_value in value.items():
                        child = QTreeWidgetItem([s_key, str(s_value)])
                        item.addChild(child)
            items.append(item)
        self.treeDesc.clear()
        self.treeDesc.insertTopLevelItems(0, items)
        # Upload variables
        varsDict = datos["VARS"]
        self.listVars.clear()
        self.listVars.addItems(list(varsDict.keys())[1:])
        # Upload time value maximum
        self.minTime.setMaximum(datos["TDEF"]["nvalues"])
        self.maxTime.setMaximum(datos["TDEF"]["nvalues"])
        minLon, maxLon = int(datos["XDEF"]["min"]), int(datos["XDEF"]["max"])
        self.minLon.setMinimum(minLon)
        self.minLon.setMaximum(maxLon)
        self.minLon.setValue(minLon)
        self.maxLon.setMinimum(minLon)
        self.maxLon.setMaximum(maxLon)
        self.maxLon.setValue(maxLon)
        minLat, maxLat = int(datos["YDEF"]["min"]), int(datos["YDEF"]["max"])
        self.minLat.setMinimum(minLat)
        self.minLat.setMaximum(maxLat)
        self.minLat.setValue(minLat)
        self.maxLat.setMinimum(minLat)
        self.maxLat.setMaximum(maxLat)
        self.maxLat.setValue(maxLat)
        minLev, maxLev = int(datos["ZDEF"]["min"]), int(datos["ZDEF"]["max"])
        self.spinLev.setMinimum(minLev)
        self.spinLev.setMaximum(maxLev)
        self.spinLev.setValue(minLev)
        self.lblGraphic.setPixmap(QPixmap())
        self.txtScript.setPlainText("")

    def generateGraphic(self):
        if self.ctlFile != None:
            self.makeScript()
            self.runScript()
            script = self.txtScript.toPlainText()
            if(len(script)>0):
                self.btnSaveGraphic.setEnabled(True)
                self.btnSaveScript.setEnabled(True)

    def makeScript(self):
        if not self.checkSameG.isChecked():
            datos = self.ctlFile.__dict__
            color = "white"
            # Add open file
            txtCurrent = "'open " + self.fpath +"'"
            # Add display color
            txtCurrent += f"\n'set display color {color}'"

            # Add needed information
            minLon, maxLon = self.minLon.value(), self.maxLon.value()
            minLat, maxLat = self.minLat.value(), self.maxLat.value()
            lev = self.spinLev.value()
            txtCurrent += f"\n'set LON {minLon} {maxLon}'"
            txtCurrent += f"\n'set LAT {minLat} {maxLat}'"
            txtCurrent += f"\n'set LEV {lev}'"
            # Add set gxout
            gxout = self.cmbGxout.currentText()
            if len(gxout) > 0:
                txtCurrent += f"\n'set gxout {gxout}'"
            # Add display vars
            varsSel = self.listVars.selectedItems()
            for var in varsSel:
                txtCurrent += f"\n'd {var.text()}'"
        else:

            if len(self.txtScript.toPlainText()) > 0:
                txtCurrent = "\n".join(self.txtScript.toPlainText().split("\n")[:-2])
                lev = self.spinLev.value()
                txtCurrent += f"\n'set LEV {lev}'"
                # Add set gxout
                gxout = self.cmbGxout.currentText()
                if len(gxout) > 0:
                    txtCurrent += f"\n'set gxout {gxout}'"
                # Add display vars
                varsSel = self.listVars.selectedItems()
                for var in varsSel:
                    txtCurrent += f"\n'd {var.text()}'"

        txtCurrent += "\n'printim tmp.png'\n"
        self.txtScript.setPlainText(txtCurrent)

    def runScript(self):
        self.lblGraphic.setPixmap(QPixmap())
        # Run script
        script = self.txtScript.toPlainText()
        with open('tmp.gs', 'w') as f:
            f.write(script)
        self.imageFile = None
        for line in script.split('\n'):
            if 'printim' in line and not '\'' in line[9:-1]:
                self.imageFile = line[9:-1]
        if self.imageFile == None:
            self.lblGraphic.setText("WITHOUT IMAGE")
            return
        os.system(f"rm -f {self.imageFile}")
        os.system(f"{pathGrads}/grads -lbxc 'run tmp.gs'")
        pixmap = QPixmap(self.imageFile)
        if pixmap:
            pixmap = pixmap.scaled(self.lblGraphic.width(), 
                                self.lblGraphic.height(), 
                                QtCore.Qt.KeepAspectRatio)
            self.lblGraphic.setPixmap(pixmap)
        self.tabWidget.setCurrentIndex(0)

    def saveGraphic(self):
        name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',".png","Images PNG(*.png)")
        if(name):
            os.system(f"cp {self.imageFile} {name}")

    def saveScript(self):
        name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',".gs","GS Scripts(*.gs)")
        if(name):
            os.system(f"cp tmp.gs {name}")
        

    def closeEvent(self, event):
        os.system("rm -f tmp.gs & rm -f tmp.png")
        event.accept() 

    def convertGribFile(self, pathF):
        command = f"{pathGrads}/grib2ctl.pl {pathF} > {pathF}.ctl"
        command2 = f"{pathGrads}/gribmap -i {pathF}.ctl" 
        os.system(command)
        os.system(command2)
        return f"{pathF}.ctl"


class SRGrads:
    
    def show(self):
        app = QtWidgets.QApplication([])
        window = SRGradsWindow()
        app.exec_()