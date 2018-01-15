#-*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import cPickle, ConfigParser
import GUIcalcIO

import sys,os

## @package gtdev.gui
#  The GUI module for the gas turbine developer

#if sys.platform == 'linux2':
	#sys.path.append(sys.path[0] + '/src')
#elif sys.platform == 'win32':
	#sys.path.append(sys.path[0] + '\src')
#else:
	#print 'Please define the path for src manually'
	
from gtdev import turbofan,turbojet,compressor,turbine,combChamber,nozzle

## Control class for the GUI interface
class GUIControl(QtGui.QMainWindow):
	
	## @var componentDict
	# dictionary for engine components
	componentDict = 0
	
	## Constructor
	#
	# initialize the GUI and all associated widgets
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		
		# populate componentDict with all recognized types of possible components
		self.componentDict={
			"Turbofan": turbofan.Turbofan,\
			"Turbofan_Recalc": turbofan.Turbofan_Recalc,\
			"Turbojet": turbojet.Turbojet,\
			"Axial Compressor": compressor.CompressorAxial,\
			"Radial Compressor": compressor.CompressorRadial,\
			"Combustion Chamber": combChamber.CombChamber,\
			"Axial Turbine": turbine.Turbine, \
			"Nozzle": nozzle.Nozzle			
		}
		
		self.currentDirectory = sys.path[0] + '/'
		
		# widget layout
		self.tabWidgets = []
				
		self.setWindowTitle('Gas Turbine Developer')
		self.setWindowIcon(QtGui.QIcon(':HummingBirdLogo.jpeg'))
		self.statusBar().showMessage('Ready to rumble...')

		self.mainWidget = QtGui.QTabWidget()
		self.setCentralWidget(self.mainWidget)
		
		# toolbar
		self.exit = QtGui.QAction('Exit', self)
		self.exit.setStatusTip('Exit')
		self.exit.setShortcut('Esc')
		self.connect(self.exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

		self.save = QtGui.QAction('Save', self)
		self.save.setStatusTip('Save engine in current tab')
		self.save.setShortcut('Ctrl+S')
		self.connect(self.save, QtCore.SIGNAL('triggered()'), self.saveObj)

		self.open = QtGui.QAction('Open', self)
		self.open.setStatusTip('Open existing engine in new tab')
		self.open.setShortcut('Ctrl+O')
		self.connect(self.open, QtCore.SIGNAL('triggered()'), self.loadObj)

		self.new = QtGui.QAction('New', self)
		self.new.setStatusTip('New engine in new tab')
		self.new.setShortcut('Ctrl+N')
		self.connect(self.new, QtCore.SIGNAL('triggered()'), self.newObj)

		self.about = QtGui.QAction('About', self)
		self.about.setStatusTip('About')
		self.connect(self.about, QtCore.SIGNAL('triggered()'), self.aboutMessage)

		self.toolbar = self.addToolBar('gtdev Toolbar')
		self.toolbar.addAction(self.new)
		self.toolbar.addAction(self.open)
		self.toolbar.addAction(self.save)
		self.toolbar.addAction(self.exit)
		self.toolbar.addAction(self.about)
		
	## action for creating a new engine
	#
	# displays an input dialog for selecting the type of engine and an engine identification string.
	# will invoke the creation of a new tab upon confirmation.
	def newObj(self):
		
		# dialog GUI
		self.inputDialog = QtGui.QDialog()
		self.LEEngineIdentification = QtGui.QLineEdit('New Engine')
		self.CBEngineType = QtGui.QComboBox()
		for i in self.componentDict.keys():
			self.CBEngineType.insertItem(0, i)
		self.PBCreate = QtGui.QPushButton('Create New Engine')
		self.PBCancel = QtGui.QPushButton('Cancel')

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.PBCreate)
		hbox.addWidget(self.PBCancel)
		
		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(QtGui.QLabel('Enter Engine Identification:'))
		vbox.addWidget(self.LEEngineIdentification)
		vbox.addWidget(QtGui.QLabel('Choose Engine Type:'))
		vbox.addWidget(self.CBEngineType)
		vbox.addLayout(hbox)
		
		self.inputDialog.setLayout(vbox)
		self.connect(self.PBCancel, QtCore.SIGNAL('clicked()'), self.inputDialog.reject)
		self.connect(self.PBCreate, QtCore.SIGNAL('clicked()'), self.inputDialog.accept)
		
		# action upon confirmation: create a new tab for new engine
		if self.inputDialog.exec_() == 1:
			typestr=str(self.CBEngineType.currentText())
			identstr=str(self.LEEngineIdentification.text())
			self.addTab(typestr,identstr)
		# action upon cancelation: do nothing
		else:
			pass
	
	## add a new tab for a newly created engine
	#
	# create a new instance for the selected type of component and place it inside a newly created tab
	#
	# @param typestr 
	#	engine type identifier (has to correspond to an entry in self.componentDict)
	# @param identstr
	#	identification string (any arbitrary string for given this engine a name)
	# @param filename
	#	file to load the component from
	def addTab(self,typestr,identstr,filename=None):
		
		# dynamically create a new instance of typestr using the componentDict
		component = self.componentDict[typestr](identstr)
		if filename!=None:
		    component.loadObject(filename)
		
		# append the new tab, placing a new instance of GUIcalcIO in it and select it
		index = self.mainWidget.addTab(
			GUIcalcIO.GUIcalcIO(component, self),
			component.identification)
		self.mainWidget.setCurrentIndex(index)
	
	## action for saving the currently selected engine
	#
	# displays a file save dialog for selecting the filename
	def saveObj(self):
		
		# select filename
		filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', 
			self.currentDirectory + self.mainWidget.currentWidget().cobj.identification)
		self.currentDirectory = filename
		while self.currentDirectory[-1] != '/':
			self.currentDirectory = self.currentDirectory[:-1]
			
		# save content of current tab to file
		self.mainWidget.currentWidget().writeInputToObject()
		self.mainWidget.currentWidget().cobj.saveObject(filename)

#	def saveObj2(self):
#		self.mainWidget.currentWidget().writeInputToObject()
#		filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', sys.path[0])+'.gtdevsave'
#		file = open(filename, 'w')
#		cPickle.dump(self.mainWidget.currentWidget().cobj, file)
#		file.close()

	## action for loading an engine from an already existing file
	#
	# if no filename is supplied, displays a file open dialog for selecting the file.
	# the file must be written using *.ini-file syntax 
	# 
	# @param filename
	#	path to file for loading 
	def loadObj(self,filename=''):
		
		# select file name if none specified
		if filename == '':
			filename = QtGui.QFileDialog.getOpenFileName(self, 'Load File', 
				self.currentDirectory)
		
		# pre-process filename
		self.currentDirectory = filename
		while self.currentDirectory[-1] != '/':
			self.currentDirectory = self.currentDirectory[:-1]

		# use configparser for reading the file
		configparser = ConfigParser.RawConfigParser()
		configparser.optionxform = str
		configparser.read(str(filename))
		
		# check sanity of input file
		if not ( configparser.has_section('general') or \
			(configparser.has_option('general', 'type') or configparser.has_option('general', 'identification') )):
			 QtGui.QMessageBox.critical(self,'Error',
				'Data file corrupted: [general] section is missing or incomplete!')
		else:
			# add a new tab for the engine
			self.addTab(configparser.get('general', 'type'),configparser.get('general', 'identification'),str(filename))
		
			# load the content of the file into the component
			self.mainWidget.currentWidget().updateTables()

#	def loadObj2(self):
#		filename = QtGui.QFileDialog.getOpenFileName(self, 'Load File', sys.path[0])
#		file = open(filename, 'r')
#		abstractturbo = cPickle.load(file)
#		file.close()
#		self.mainWidget.addTab(GUIcalcIO.GUIcalcIO(abstractturbo, self), abstractturbo.identification)
#		self.mainWidget.currentWidget().updateTables()
	
	## action for saving the engine of a closing tab
	# used in the "closeTab"-Funktion
	def saveObjCloseTab(self):                 
		self.saveObj()
		self.mainWidget.removeTab(self.mainWidget.currentIndex())
		self.closeDialog.accept()

	## action for closing a tab
	#
	# display a confirmation for closing the current tab (close w/o saving, close w/ saving or cancel)
	# and perform the corresponding action
	def closeTab(self):
		self.closeDialog = QtGui.QDialog()
		
		# dialog GUI
		self.PBCancelCloseTab = QtGui.QPushButton('Cancel')
		self.PBCloseTab = QtGui.QPushButton('Close without saving')
		self.PBSaveObj = QtGui.QPushButton('Save current engine')
		self.PBSaveObj.setDefault(True)
		
		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.PBCloseTab)
		hbox.addWidget(self.PBCancelCloseTab)
		hbox.addWidget(self.PBSaveObj)
		
		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(QtGui.QLabel('Do you want to save the current engine?'))
		vbox.addLayout(hbox)
		
		self.closeDialog.setLayout(vbox)
		
		self.connect(self.PBCancelCloseTab, QtCore.SIGNAL('clicked()'), self.closeDialog.reject)
		self.connect(self.PBCloseTab, QtCore.SIGNAL('clicked()'), self.closeDialog.accept)		
		self.connect(self.PBSaveObj, QtCore.SIGNAL('clicked()'), self.saveObjCloseTab)
		
		# action upon acceptance: remove tab
		if self.closeDialog.exec_() == 1:
			self.mainWidget.removeTab(self.mainWidget.currentIndex())
		# action upon rejection: do nothing
		else:
			pass
	
	## action for displaying an about dialog
	def aboutMessage(self):
		QtGui.QMessageBox.about(self,'About:',
			'Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines\n'+
			'Institute for Flight Propulsion, TU Munich\n'+
			'Authors:\tSebastian Barthmes, Sebastian Brehm,\n'+
			'\tJan Matheis, Peter Schoettl\n'+
			'Published under the terms of GNU Public Licence GPL v3')
	
	## action for closing the main window
	#
	# quit the application. if at least one tab is still open, ask for confirmation
	def closeEvent(self, event):
		# ask for permission if one or more tabs are still open
		if self.mainWidget.count() >= 1:
			reply = QtGui.QMessageBox.question(self, 'Message', 
				'One or more engines are running.\n\nAre you sure to quit?', 
				QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
			
			# action upon confirmation: allow application to quit
			if reply == QtGui.QMessageBox.Yes:
				event.accept()
			# action upon rejection: prevent application from quitting
			else:
				event.ignore()
		# otherwise, quit the application
		else:
			event.accept()
