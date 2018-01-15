#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
#===============================================================================

#turbofan.py
#imports:
import numpy
from abstract import *
import compressor,turbine,combChamber,nozzle
from helper_methods import *
import sys

#===============================================================================
# Klasse zur Auslegung und Berechnung von Turbofantriebwerken	
#===============================================================================
class Turbojet(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Turbojet'
		
		self.thermoInputParams=[["thrust","N","Total Thrust of the Engine"], \
								["c_0","m/s","Airspeed of incident flow"],\
								["p_inf","Pa","Air pressure"],\
								["T_inf","K","Air temperature"],\
								["Pi_inlet","-","Total pressure loss of inlet"],\
								["eta_mech_hps","-","Efficiency of high pressure shaft"]]
		
		
		self.thermoOutputParams=[["mflow","kg/s","Total Massflow"],\
								["c_9","m/s","Velocity hot flow"],\
								["F","N","tatal thrust"],\
								["SFC","kg/h/kN","Specific Fuel Consumption"],\
								["eta_th","-","thermodynamic (inner) efficiency"],\
								["eta_p","-","propulsive (outer) efficiency"],\
								["eta_tot","-","total efficiency"],\
								["p_tinf","Pa","Air pressure"],\
								["T_tinf","K","Total temperature inlet"]]
		
		self.aeroInputParams=[["p_inf","Pa","Static pressure of incident flow"],\
							  ["Ma_max","-","Maximum Circumferential Fan Tip Mach Number"]]
		self.aeroOutputParams=[["F_recalc","N","Recalulated Thrustforce"]]
		
		self.modularSubfunctionList.append(self.tsplot)
		
		
		#Initialisation of global variables from lists
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#Dictionary with subcomponents
		self.subcomponentList=[ ["hpc", compressor.CompressorRadial("High Pressure Compressor")],\
								["combc", combChamber.CombChamber("Combustion Chamber")],\
								["hpt", turbine.Turbine("High Pressure Turbine")],\
								["hn", nozzle.Nozzle("Nozzle for hot massflow")]]
		
		#Initialise global variables from dictionary
		self.setVariablesFromList(self.subcomponentList)
		
		#Delete input parameters computed by turbojet
		self.removeComputedParams(self.hpc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.combc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.hpt,["mflow","deltaP","p_t1","T_t1","beta"],["n","c_1","p_t1"])
		self.removeComputedParams(self.hn,["mflow","T_t1","p_t1","beta"],["p_3"])
		
		
		#Default Values:
		self.p_inf=101325.
		self.T_inf=288.15
		self.kappa_inf=getKappa(Tt=self.T_inf,Ma=0)
		self.R_inf=287.15
		self.eta_mech_hps=0.99
		self.eta_mech_lps=0.99
		self.c_0=0.0
		self.Pi_inlet=0.95
		
	
	def calcThermo(self):
		"""Diese Methode berechnet die Eckdaten des Kreisprozesses"""
		
		self.check(self.thermoInputParams)
		self.hpc.check(self.hpc.thermoInputParams)
		self.combc.check(self.combc.thermoInputParams)
		self.hpt.check(self.hpt.thermoInputParams)
		
		self.R=getR()
		
		#Schallgeschwindigkeit in der Umgebung
		a_0=numpy.sqrt(self.kappa_inf*self.R_inf*self.T_inf)
		
		#Inlet Mach number (ohne Einlauf)
		Ma_0=self.c_0/a_0
		
		#Total temperature inlet engine
		self.T_tinf=self.T_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)
		
		#Total pressure inlet engine
		self.p_tinf=self.p_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)**(self.kappa_inf/(self.kappa_inf-1))
		
		#Gesamtmassenstrom
		mflow_start=5.0
				
		#iteration massenstrom
		def iterate_fun(mflow):
			self.mflow=float(mflow)
						
			#Initialisiere Massenströme der Komponenten
			self.hpc.mflow=self.mflow
			self.combc.mflow=self.mflow
			
			#high pressure compressor
			self.hpc.p_t1=self.p_tinf*self.Pi_inlet
			self.hpc.T_t1=self.T_tinf
			self.hpc.calcThermo()	
			
			#combustion chamber
			self.combc.p_t1=self.hpc.p_t3
			self.combc.T_t1=self.hpc.T_t3
			self.combc.calcThermo()
			
			self.hpt.mflow=self.mflow+self.combc.beta*self.mflow
			self.hn.mflow=self.mflow+self.combc.beta*self.mflow
			
			#high pressure turbine
			self.hpt.R=self.combc.R_ex
			self.hpt.p_t1=self.combc.p_t3
			self.hpt.T_t1=self.combc.T_t3
			self.hpt.deltaP=self.hpc.deltaP/self.eta_mech_hps
			self.hpt.beta=self.combc.beta
			self.hpt.calcThermo()
			
			#hot nozzle
			self.hn.R=self.combc.R_ex
			self.hn.T_t1=self.hpt.T_t3
			self.hn.p_t1=self.hpt.p_t3
			self.hn.beta=self.combc.beta
			self.hn.calcThermo()
						
			#schub berechnen
			
			#Ma hot nozzle outlet
			self.Ma_9=(((self.hn.p_t3/self.p_inf)**((self.hpt.kappa-1)/self.hpt.kappa)-1)*2/(self.hpt.kappa-1))**0.5
			
			self.T_9=self.hpt.T_t3/(1+(self.hpt.kappa-1)/2*self.Ma_9**0.5)
			
			self.a_9=(self.hpt.kappa*self.combc.R_ex*self.T_9)**0.5
			
			self.c_9=self.Ma_9*self.a_9
			
			self.F=self.c_9*self.mflow
			
			return self.F-self.thrust
		
		#try:
		self.mflow=float(fsolve(iterate_fun,[mflow_start]))
		#except:
			#if str(sys.exc_info()[1])=="Error occured while calling the Python function named iterate_fun":
				#raise Exception,"Thrust iteration didn't converge. Cycle impossible / Thrust too high."
				#print sys.exc_info()
				
		
		#Thermischer Wirkungsgrad (Strahlleistung/Wärmeeintrag)
		print self.hpt.deltaP*self.eta_mech_hps-self.hpc.deltaP
		self.eta_th=((self.mflow+self.combc.mflow_f)*self.c_9**2-self.mflow*self.c_0**2)/2./self.combc.deltaP
		
		#Vortriebswirkungsgrad
		self.eta_p=2.*(self.F*self.c_0)/(self.mflow*self.c_0**2-(self.mflow+self.combc.beta*self.mflow)*self.c_9**2)
		
		#Gesamtwirkungsgrad
		self.eta_tot=self.eta_p*self.eta_th
		
		
		self.SFC=self.combc.mflow_f*3600./self.F*1000.
		#ende
		
		self.check(self.thermoOutputParams)
	

		
	def calcAero(self):
		"""Diese Methode berechnet die Aerodynamischen Eckdaten der Komponenten"""
		
		self.check(self.aeroInputParams)
		self.hpc.check(self.hpc.aeroInputParams)
		self.combc.check(self.combc.aeroInputParams)
		self.hpt.check(self.hpt.aeroInputParams)
		
		self.check(self.aeroOutputParams)
		
	def tsplot(self,widget):
		#self.calcThermo()
		import cyclePlotter
		from PyQt4.QtCore import SIGNAL
		from PyQt4.QtGui import QDialog,QWidget, QVBoxLayout, QHBoxLayout,QPushButton,QSplitter
		from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar

		
		#plot=TsPlotter.TsPlotter("Tt0",self.T_tinf,0.0,self.p_tinf)
		

		tsplot=cyclePlotter.TsPlotter("",0,0,0)
		tsplot.pyl.clear()
		tsplot.pWidget.format_labels()

		
		hsplot=cyclePlotter.HsPlotter("",0,0,0,0)
		hsplot.pyl.clear()
		hsplot.pWidget.format_labels()
		
		def calcPlot():			

			tsplot.pyl.clear()
			tsplot.pWidget.format_labels()
			tsplot.addnewStart("T_t0",self.T_tinf,0.0,self.p_tinf)

			tsplot.isotherme("T_t2",self.hpc.p_t1)
			#Radialverdichter
			tsplot.polytrope("T_t3",self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			tsplot.isobare("T_t4",self.combc.T_t3)
			#h-Turbine
			tsplot.polytrope("T_t5",self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#Düse
			tsplot.isotherme("T_t8",self.hn.p_t3)
			#Entspannung
			tsplot.isentrope("T_t9",pend=self.p_tinf)
			tsplot.isobare("",self.T_tinf)

			tsplot.pWidget.draw()
			
			
			hsplot.pyl.clear()
			hsplot.pWidget.format_labels()
			hsplot.addnewStart("H_t0",self.mflow,self.T_tinf,0.0,self.p_tinf)
			
			hsplot.isotherme("H_t2",self.mflow,self.hpc.p_t1)
			#Radialverdichter
			hsplot.polytrope("H_t3",self.mflow,self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			hsplot.isobare("H_t4",self.mflow,self.combc.T_t3)
			#h-Turbine
			hsplot.polytrope("H_t5",self.mflow,self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#Düse
			hsplot.isotherme("H_t8",self.mflow,self.hn.p_t3)
			#Entspannung
			hsplot.isentrope("H_t9",self.mflow,pend=self.p_tinf)
			hsplot.isobare("",self.mflow,self.T_tinf)
			
			
			hsplot.pWidget.draw()

		
		toolbar1=NavigationToolbar(tsplot.pWidget,tsplot.pWidget)
		toolbar2=NavigationToolbar(hsplot.pWidget,hsplot.pWidget)
		l=QVBoxLayout()
		plotb=QPushButton("Update Plot")
		sp=QSplitter()
		w1=QWidget()
		l1=QVBoxLayout()
		l1.addWidget(tsplot.pWidget)
		l1.addWidget(toolbar1)
		w1.setLayout(l1)
		
		w2=QWidget()
		l2=QVBoxLayout()
		l2.addWidget(hsplot.pWidget)
		l2.addWidget(toolbar2)
		w2.setLayout(l2)
		
		sp.addWidget(w1)
		sp.addWidget(w2)
		
		l.addWidget(sp)
		l.addWidget(plotb)
		w=QDialog()
		w.setLayout(l)
		
		
		#w.show()
		
		w.connect(plotb, SIGNAL("clicked()"), calcPlot)
		
		widget.addTab(w,"Cycle Plot")