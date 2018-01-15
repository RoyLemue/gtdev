#-*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import sys,copy,traceback

## control class for the interface between GUI and calculation
class GUIcalcIO(QtGui.QWidget):
	
	## @var cobj
	# master object for storing the component,
	# can be any instance of an AbstractTurbo class
	# @see AbstractTurbo
	cobj = 0
	
	## @var tableList
	# storage for all input/output tables,
	# this is a list of lists of QTableWidget
	# @code
	# tableList[0]: tables for the parent component
	#  tableList[0][0]: table for the thermodynamic input data
	#  tableList[0][1]: table for the thermodynamic output data
	#  tableList[0][2]: table for the aerodynamic input data
	#  tableList[0][3]: table for the aerodynamic output data
	# tableList[1]: tables for the 1st sub-component
	#  tableList[1][:]: tables for the thermo- & aerodynamic in/output data
	# tableList[2]: tables for the 2nd sub-component
	# ...
	# @endcode
	tableList = []
	
	## Constructor
	#
	# initialize the GUI and all associated widgets
	def __init__(self, cobj_, parent_=None):
		QtGui.QWidget.__init__(self, parent_)
		
		# the man tab widget usually is the parent
		# (but this could be any Qt widget)
		self.parent = parent_
		
		# store the reference for the component
		# @todo check type of cobj_
		self.cobj=cobj_

		# widget layout
		self.calcThermoButton = QtGui.QPushButton("Calculate Thermodynamics")
		self.calcAeroButton=QtGui.QPushButton("Calculate Aerodynamics")
		self.calcAeroButton.setEnabled(0)
		
		self.connect( self.calcThermoButton, QtCore.SIGNAL("clicked()"), self.calcThermodynamics )
		self.connect( self.calcAeroButton, QtCore.SIGNAL("clicked()"), self.calcAerodynamics )
		
		self.thermoDone = False
		self.aeroDone = False
		
		# additional buttons if embedded within tab widget
		if self.parentWidget() != 0:
			self.exportSelectedButton = QtGui.QPushButton("Export Selected Component")
			self.closeTabButton = QtGui.QPushButton("Close Tab")
			
			self.connect( self.exportSelectedButton, QtCore.SIGNAL("clicked()"), self.exportSelected )
			self.connect( self.closeTabButton, QtCore.SIGNAL("clicked()"), self.parentWidget().closeTab )
		
		# component tree
		self.tree = QtGui.QTreeWidget()
		self.initTree()
		self.connect(self.tree, QtCore.SIGNAL('itemSelectionChanged()'), self.getActiveWidget)
		
		# widget stack
		self.initIOList()
		
		# error handling
		self.calcErr = QtGui.QErrorMessage()
		
		# layout
		leftbox = QtGui.QWidget()
		vboxtree = QtGui.QVBoxLayout()
		vboxtree.addWidget(self.tree)
		vboxtree.addWidget(self.calcThermoButton)
		vboxtree.addWidget(self.calcAeroButton)
		if self.parentWidget() != 0:
			vboxtree.addWidget(self.exportSelectedButton)
			vboxtree.addWidget(self.closeTabButton)
		leftbox.setLayout(vboxtree)		
		
		splitter = QtGui.QSplitter()
		splitter.addWidget(leftbox)
		splitter.addWidget(self.ioWidgetStack)
				
		vbox0 = QtGui.QVBoxLayout()
		vbox0.addWidget(splitter)
				
		self.setLayout(vbox0)
		
	## initialize structure tree
	#
	# build the structure tree based on the current cobj
	# the current component (cobj) will be the master node,
	# to which a list of corresponding sub-components as children (if present) is appended 
	def initTree(self):
		if self.cobj==None:
			self.getMasterComponent()
		
		self.tree = QtGui.QTreeWidget()
		self.tree.setColumnCount(2)
		self.tree.setHeaderLabels(["Component Name","Type"])
		
		masterTreeItem = QtGui.QTreeWidgetItem()
		masterTreeItem.setText(0,self.cobj.identification)
		masterTreeItem.setText(1,str(self.cobj))
		subTreeItems=[]
		for elem in self.cobj.subcomponentList:
			this = QtGui.QTreeWidgetItem()
			this.setText(0,elem[1].identification)
			this.setText(1,str(elem[1]))
			subTreeItems.append(this)
			masterTreeItem.addChild(this)
		
		self.tree.addTopLevelItem(masterTreeItem)
		self.tree.setColumnWidth(0,250)
		self.tree.setColumnWidth(1,400)
		self.tree.expandAll()
		
		
	## initialize component stack
	#
	# build the component stack based on the current cobj
	# the current component (cobj) will correspond to the first widget,
	# thereafter a widget for each corresponding sub-component (if present) is appended
	# 
	# each widget contains the necessary tables for the corresponding (sub-)component
	def initIOList(self):
		# note: ordering of widgets (components) is important here! 
		del self.tableList[:]
		
		self.ioWidgetStack = QtGui.QStackedWidget()
		
		# add widget for parent component to widget stack
		self.ioWidgetStack.addWidget(self.getParamIOWidget(self.cobj))
		
		# add widgets for sub-components to widget stack
		for elem in self.cobj.subcomponentList:
			self.ioWidgetStack.addWidget(self.getParamIOWidget(elem[1]))
		
		# update all tables
		self.updateTables()
	
	## action for selecting a new component in the structure tree
	#
	# this function is called whenever the user selects a new (sub-)component in the structure tree
	# in consequence, the corresponding widget in the widget stack is selected and sent forward 
	def getActiveWidget(self):
		
		# try to grab tab index if the current widget on the stack is a QTabWidget
		if isinstance(self.ioWidgetStack.currentWidget(),QtGui.QTabWidget):
			tab_index = self.ioWidgetStack.currentWidget().currentIndex()
		else:
			tab_index = -1
			
		# retrieve current selection and update the index of the widget stack
		self.ioWidgetStack.setCurrentIndex( self.getActiveObj()[0] )
		
		# apply the tab index if both the old and the new widget on the stack are QTabWidgets
		if (tab_index >= 0) and (isinstance(self.ioWidgetStack.currentWidget(),QtGui.QTabWidget)):
			self.ioWidgetStack.currentWidget().setCurrentIndex(tab_index)

	## retrieve the currently with the structure tree selected (sub-)component
	#
	# @return 
	#	an array describing the selected (sub-)component: [0] - index of selected component, [1] - reference to instance of selected component
	# 
	def getActiveObj(self):
		
		# get selection of QTreeWidget
		try:
			# try to match the label of the selected component to the list of available components
			label = self.tree.selectedItems()[0].text(0)
			
			if label == self.cobj.identification:
				activeobj = self.cobj
				return [0,activeobj]
				
			for n in range(len(self.cobj.subcomponentList)):
				if label == self.cobj.subcomponentList[n][1].identification:
					activeobj = self.cobj.subcomponentList[n][1]
					return [n+1,activeobj]
		
		except IndexError:
			return None
		
	## export the selected component to a new tab
	#
	# this function is called whenever the user click the buttons "export component"
	# it retrieves the currently selected component and copies it into a new tab
	def exportSelected(self):
		
		# make a deep copy of selected component
		obj = copy.copy(self.getActiveObj()[1])
		
		
		if obj == None:
			QtGui.QMessageBox.information(self,"Error",
				"Could not retrieve the currently selected component.")
			return
			
		# make another deep copy
		# to retrieve and copy the parameter constraints imposed by the parent
		tmp = copy.copy(obj)
		tmp.__init__("tmp")
		obj.thermoInputParams = tmp.thermoInputParams
		obj.thermoOutputParams = tmp.thermoOutputParams
		obj.aeroInputParams = tmp.aeroInputParams
		obj.aeroOutputParams = tmp.aeroOutputParams
		del tmp
		
		# create a new tab based on the generated copy
		self.parent.mainWidget.addTab(GUIcalcIO(obj, self.parent), obj.identification)

	## build the io widget for a (sub-)component
	#
	# @param elem 
	#	component of type AbstractTurbo
	def getParamIOWidget(self,elem):
		
		# thermodynamical GUI
		thermowidget = QtGui.QWidget()
		hboxThermo = QtGui.QHBoxLayout()
		vboxThermo = QtGui.QVBoxLayout()
		vboxThermo.addLayout(hboxThermo)
		thermowidget.setLayout(vboxThermo)
		scrollThermo = QtGui.QScrollArea()
		scrollThermo.setWidget(thermowidget)
		
		# aerodynamical GUI
		aerowidget = QtGui.QWidget()
		hboxAero = QtGui.QHBoxLayout()
		scrollAero = QtGui.QScrollArea()
		vboxAero=QtGui.QVBoxLayout()
		vboxAero.addLayout(hboxAero)
		aerowidget.setLayout(vboxAero)
		scrollAero.setWidget(aerowidget)
		
		# initialize tables for this component
		iotlist=[]
		for i in range(4):
			table = QtGui.QTableWidget(self)
			
			table.setColumnCount(1)
			table.horizontalHeader().setStretchLastSection(True)
			iotlist.append(table)
			# connect the cellChanged action
			self.connect( table, QtCore.SIGNAL("cellChanged(int,int)"), self.tableItemChanged )
			
		self.tableList.append(iotlist)
		
		# populate the widget with the tables
		hboxThermo.addWidget(self.tableList[-1][0])
		hboxThermo.addWidget(self.tableList[-1][1])
		
		hboxAero.addWidget(self.tableList[-1][2])
		hboxAero.addWidget(self.tableList[-1][3])
		
		# add tabs
		widget = QtGui.QTabWidget()
		widget.addTab(thermowidget,"Thermo")
		widget.addTab(aerowidget,"Aero")
		
		# execute custom modular subfunction connected to the component 
		for i in elem.modularSubfunctionList:
			i(widget)

		return widget
	
	## slot for changed table data
	#
	# this function is called whenever data in one of the tables is modified
	# this will reset the thermoDone and aeroDone status indicators
	def tableItemChanged(self, item_):
		thermoDone = False
		aeroDone = False
		
		self.calcAeroButton.setEnabled(0)
	
	## populate a dictionary with data taken from tables
	#
	# @param table_
	#	either a single table (QTableWidget) or a list of QTableWidgets to fetch the data from
	# @return
	#	a dictionary containing key,values-pairs of the data within table_ 
	def getDictFromTable(self,table_):
		
		#target dictionary
		paramdict={}
		
		try:
			# loop over all tables
			for i in range(len(table_)):
				
				# loop over all rows
				for n in range(table_[i].rowCount()):
					paramdict[str(table_[i].verticalHeaderItem(n).text())] = \
						self.getInternalValueType(table_[i].item(n,0).text())
		except TypeError:
			# loop over all rows
			for n in range(table_.rowCount()):
				paramdict[str(table_.verticalHeaderItem(n).text())] = \
					self.getInternalValueType(table_.item(n,0).text())
		
		return paramdict
	
	## populate a table with data taken from a dictionary
	#
	# @todo Documentation!
	def getTableFromDict(self,dict_,table_):
		for i in range(len(table_)):
			for k in range(table_[i].rowCount()):
				for l,m in dict_.iteritems():
					if str(table_[i].verticalHeaderItem(k).text()) == l:
						table_[i].item(k,0).setText(m)
		
	def getInternalValueType(self,qstring):
		try:
			if str(qstring)=="None":
				return None
			else:
				return float(qstring)
		except ValueError:
			return str(qstring)

	## update all tables to reflect the current values stored within the component instances
	#
	# this will reset all tables for all (sub-)components of the current engine,
	#  even the ones not shown (all entries of the widget stack)
	def updateTables(self):
		
		## create item for vertical header
		def headerItem(caption_, tooltip_):
			item = QtGui.QTableWidgetItem()
			item.setText(str(caption_))
			item.setToolTip(str(tooltip_))
			
			return item
		
		## create item for value item
		def valueItem(value_,tooltip_):	
			if isinstance(value_,list) and len(value_) == 1:
				value_ = value_[0]
				print "WARNING: converted atomic list for " + tooltip_ + " to string."
				
			item = QtGui.QTableWidgetItem()
			item.setText(str(value_))
			item.setToolTip(str(tooltip_))
			
			return item
		
		## create item for unit item
		def unitItem(unit_, tooltip_):
			item = QtGui.QTableWidgetItem()
			item.setText("[" + str(unit_) + "]")
			item.setToolTip(str(tooltip_))
			item.setFlags(QtCore.Qt.ItemIsSelectable)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			
			return item
		
		# loop over all tables
		for n in range(len(self.tableList)):
			
			# get object associated to the table
			if n == 0:
				obj = self.cobj
			else:
				obj = self.cobj.subcomponentList[n-1][1]
			
			# storage for all data to be printed
			dictlist=[obj.getThermoInputDict(),
				obj.getThermoOutputDict(),
				obj.getAeroInputDict(),
				obj.getAeroOutputDict()]
			
			# write data into tables
			for index,table in enumerate(self.tableList[n][:]):
				dict_ = dictlist[index]
				table.setRowCount(len(dict_.keys()))
				table.setColumnCount(2)
				labels = []
				for index,item in enumerate(dict_):
					table.setVerticalHeaderItem(index, headerItem(item,dict_[item][2]) )
					table.setItem(index,0, valueItem(dict_[item][0],dict_[item][2]) )
					table.setItem(index,1, unitItem(dict_[item][1],dict_[item][2]) )
				table.setVerticalHeaderLabels(labels)
				table.setHorizontalHeaderLabels(["Value","Unit"])
				table.horizontalHeader().setMinimumSectionSize(50)
				table.horizontalHeader().resizeSection(0,200)
				table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter)
				table.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
				
	## update the input values for all (sub-)components
	#
	# copy the data entered into the input tables to all (sub-)components
	def writeInputToObject(self):
		
		# copy the data for the parent component
		self.cobj.setVariablesFromDict(self.getDictFromTable(self.tableList[0]))
		
		# copy the data for all sub-components
		for i in range(len(self.cobj.subcomponentList)):
			self.cobj.subcomponentList[i][1].setVariablesFromDict(self.getDictFromTable(self.tableList[i+1]))
	
	## launch calculation of thermodynamics
	def calcThermodynamics(self):
		try:
			self.writeInputToObject()
			self.cobj.calcThermo()
			self.updateTables()
		except Exception:
			self.calcErr.showMessage(str(sys.exc_info()[1]))
		except:
			#print sys.exc_info()
			print traceback.print_exc(file=sys.stdout)
			self.calcErr.showMessage(str(sys.exc_info()[1])+"*** Check Console Output for additional Info")
		else:
			self.calcAeroButton.setEnabled(1)
			self.thermoDone = True
	
	## launch calculation of aerodynamics
	def calcAerodynamics(self):
		try:
			self.writeInputToObject()
			self.cobj.calcAero()
			self.updateTables()
		except Exception:
			self.calcErr.showMessage(str(sys.exc_info()[1]))
		except:
			#print sys.exc_info()
			print traceback.print_exc(file=sys.stdout)
			self.calcErr.showMessage(str(sys.exc_info()[1])+"*** Check Console Output for additional Info")
		else:
			self.aeroDone = True
