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
class Turbofan(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Turbofan'
		
		self.thermoInputParams=[["thrust","N","Total Thrust of the Engine"], \
								["c_0","m/s","Airspeed of incident flow"],\
								["p_inf","Pa","Air pressure"],\
								["T_inf","K","Air temperature"],\
								["bypassRatio","-","Ratio of cold massflow to hot massflow"],\
								["Pi_inlet","-","Total pressure loss of inlet"],\
								["Pi_splitter","-","Total pressure loss of the splitter"],\
								["eta_mech_hps","-","Efficiency of high pressure shaft"],\
								["eta_mech_lps","-","Efficiency of low pressure shaft"]]
		
		
		self.thermoOutputParams=[["mflow","kg/s","Total Massflow"],\
								["mflow_h","kg/s","Hot Massflow"],\
								["mflow_c","kg/s","Cold Massflow"],\
								["c_19","m/s","Velocity cold flow"],\
								["c_9","m/s","Velocity hot flow"],\
								["F_fan","N","thrust fan"],\
								["F_main","N","thrust main"],\
								["F","N","total thrust"],\
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
		self.subcomponentList=[ \
								["fan", compressor.CompressorAxial("Fan")],\
								["hpc", compressor.CompressorRadial("High Pressure Compressor")],\
								["combc", combChamber.CombChamber("Combustion Chamber")],\
								["hpt", turbine.Turbine("High Pressure Turbine")],\
								["lpt", turbine.Turbine("Low Pressure Turbine")],\
								["hn", nozzle.Nozzle("Nozzle for hot massflow")],\
								["cn", nozzle.Nozzle("Nozzle for cold massflow")]\
								]
		
		#Initialise global variables from dictionary
		self.setVariablesFromList(self.subcomponentList)
		
		#Delete input parameters computed by turbofan
		self.removeComputedParams(self.fan,["mflow","T_t1","p_t1"],[])
		self.removeComputedParams(self.hpc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.combc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.hpt,["mflow","deltaP","p_t1","T_t1","beta"],["n","c_1","p_t1"]) #hpt.c_1 der soll nicht eingegeben werden muessen fuer gesamte Turbofanberechnung 
		self.removeComputedParams(self.lpt,["mflow","deltaP","p_t1","T_t1","beta"],["n","c_1","p_t1","alpha_1"])
		self.removeComputedParams(self.hn,["mflow","T_t1","p_t1","beta"],["p_3"])		
		self.removeComputedParams(self.cn,["mflow","T_t1","p_t1","beta"],["p_3"])
		
		
		
		
		#Default Values:
		self.p_inf=101325.
		self.T_inf=288.15
		self.kappa_inf=getKappa(Tt=self.T_inf,Ma=0)
		self.R_inf=287.15
		self.eta_mech_hps=0.98
		self.eta_mech_lps=0.98
		self.c_0=0.0
		self.Pi_splitter=0.95
		self.Pi_inlet=0.95
		
	
	def calcThermo(self):
		"""Diese Methode berechnet die Eckdaten des Kreisprozesses"""
		
		self.check(self.thermoInputParams)
		self.fan.check(self.fan.thermoInputParams)
		self.hpc.check(self.hpc.thermoInputParams)
		self.combc.check(self.combc.thermoInputParams)
		self.hpt.check(self.hpt.thermoInputParams)
		self.lpt.check(self.lpt.thermoInputParams)
		
		self.R=getR()
		
		#Schallgeschwindigkeit in der Umgebung
		a_0=numpy.sqrt(self.kappa_inf*self.R_inf*self.T_inf)
		
		#Inlet Mach number (ohne Einlauf)
		Ma_0=self.c_0/a_0
		
		#Total temperature inlet engine
		self.T_tinf=self.T_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)
		
		#Total pressure inlet engine
		self.p_tinf=self.p_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)**(self.kappa_inf/(self.kappa_inf-1))
		
		#Totaltemperaturverhältnis der Brennkammer (dim.loses T_t4)
		tau_lambda=self.combc.T_t3/self.T_inf
		
		#Totaltemperaturverhältnis der Anströmung
		tau_0=1.0+(self.kappa_inf-1.0)/2.0*Ma_0**2.0
		
		#Fantemperatur (dimensionslos), berechnet über das vorgegebene Druckverhältnis
		tau_Fan=self.fan.Pi**((self.fan.kappa-1.0)/self.fan.kappa)
		
		#Totaltemperaturverh. des Verdichters
		tau_Comp=(self.fan.Pi*self.hpc.Pi)**((self.hpc.kappa-1.0)/self.hpc.kappa)
		
		#Spezifischer Schub
		F_s=a_0/(1.0+self.bypassRatio)* \
		(numpy.sqrt(2.0/(self.kappa_inf-1.0)*((tau_lambda-tau_0*((tau_Comp-1.0)+self.bypassRatio*(tau_Fan-1.0)))-(tau_lambda/tau_0/tau_Comp))) \
		+self.bypassRatio*numpy.sqrt(2.0/(self.kappa_inf-1.0)*(tau_0*tau_Fan-1.0)) \
		-Ma_0*(1.0+self.bypassRatio))
		
		#Heissmassenstrom
		self.mflow_h=self.thrust/F_s/(1.0+self.bypassRatio)
		
		#Kaltmassenstrom
		self.mflow_c=self.mflow_h*self.bypassRatio
		
		#Gesamtmassenstrom
		self.mflow=self.mflow_h+self.mflow_c
		
		#iteration massenstrom
		def iterate_fun(mflow):
			
			self.mflow=float(mflow)
			
			self.mflow_h=self.mflow/(self.bypassRatio+1)
			
			self.mflow_c=self.mflow*self.bypassRatio/(self.bypassRatio+1)
				
			#Initialisiere Massenströme der Komponenten
			self.fan.mflow=self.mflow
			self.hpc.mflow=self.mflow_h
			self.combc.mflow=self.mflow_h
			self.cn.mflow=self.mflow_c	
		
			#Berechne Thermodynamischen Kreisprozess
			#low pressure compressor
			self.fan.p_t1=self.p_tinf*self.Pi_inlet
			self.fan.T_t1=self.T_tinf
			self.fan.calcThermo()
			
			#high pressure compressor
			self.hpc.p_t1=self.fan.p_t3*self.Pi_splitter
			self.hpc.T_t1=self.fan.T_t3
			self.hpc.calcThermo()	
			
			#combustion chamber
			self.combc.p_t1=self.hpc.p_t3
			self.combc.T_t1=self.hpc.T_t3
			self.combc.calcThermo()
			
			self.hpt.mflow=self.mflow_h+self.combc.beta*self.mflow_h
			self.lpt.mflow=self.mflow_h+self.combc.beta*self.mflow_h
			self.hn.mflow=self.mflow_h+self.combc.beta*self.mflow_h
			
			#high pressure turbine
			self.hpt.R=self.combc.R_ex
			self.hpt.p_t1=self.combc.p_t3
			self.hpt.T_t1=self.combc.T_t3
			self.hpt.deltaP=self.hpc.deltaP/self.eta_mech_hps
			self.hpt.beta=self.combc.beta
			self.hpt.calcThermo()
			
			#low pressure turbine
			self.lpt.R=self.combc.R_ex
			self.lpt.p_t1=self.hpt.p_t3
			self.lpt.T_t1=self.hpt.T_t3
			self.lpt.deltaP=self.fan.deltaP/self.eta_mech_lps
			self.lpt.beta=self.combc.beta
			self.lpt.calcThermo()
			
			#hot nozzle
			self.hn.R=self.combc.R_ex
			self.hn.T_t1=self.lpt.T_t3
			self.hn.p_t1=self.lpt.p_t3
			self.hn.beta=self.combc.beta
			self.hn.calcThermo()
			
			#cold nozzle
			self.cn.R=self.combc.R_ex
			self.cn.T_t1=self.fan.T_t3
			self.cn.p_t1=self.fan.p_t3*self.Pi_splitter
			self.cn.calcThermo()
			
			#schub berechnen
			#Ma cold nozzle outlet
			self.Ma_19=(((self.cn.p_t3/self.p_inf)**((self.fan.kappa-1)/self.fan.kappa)-1)*2/(self.fan.kappa-1))**0.5
			
			self.T_19=self.fan.T_t3/(1+(self.fan.kappa-1)/2*self.Ma_19**0.5)
			
			self.a_19=(self.fan.kappa*self.R_inf*self.T_19)**0.5
			
			self.c_19=self.Ma_19*self.a_19
			
			self.F_fan=(self.c_19-self.c_0)*self.mflow_c
			
			#Ma hot nozzle outlet
			self.Ma_9=(((self.hn.p_t3/self.p_inf)**((self.lpt.kappa-1)/self.lpt.kappa)-1)*2/(self.lpt.kappa-1))**0.5
			
			self.T_9=self.lpt.T_t3/(1+(self.lpt.kappa-1)/2*self.Ma_9**0.5)
			
			self.a_9=(self.lpt.kappa*self.combc.R_ex*self.T_9)**0.5
			
			self.c_9=self.Ma_9*self.a_9
			
			self.F_main=(self.c_9-self.c_0)*(self.mflow_h+self.combc.beta*self.mflow_h)
			
			self.F=self.F_main+self.F_fan
			return self.F-self.thrust
		
		try:
			self.mflow=fsolve(iterate_fun,self.mflow)
			if type(self.mflow)=='list':
					self.mflow=self.mflow[0]
		except:
			if str(sys.exc_info()[1])=="Error occured while calling the Python function named iterate_fun":
				raise Exception,"Thrust iteration didn't converge. Cycle impossible / Thrust too high."
				print sys.exc_info()
				
		#SFC
		self.SFC=self.combc.mflow_f*3600./self.F*1000.
		
		self.mflow_f=self.combc.beta*self.mflow_h
		
		#Thermischer Wirkungsgrad
		self.eta_th=((self.mflow_h+self.combc.mflow_f)*self.c_9**2+(self.mflow_c)*self.c_19**2-self.mflow*self.c_0**2)/2./self.combc.deltaP
		
		#Vortriebswirkungsgrad
		self.eta_p=2.*(self.F*self.c_0)/((self.mflow_h+self.combc.beta*self.mflow_h)*self.c_9**2+self.mflow_c*self.c_19**2-self.mflow*self.c_0**2)
		
		#Gesamtwirkungsgrad
		self.eta_tot=self.eta_p*self.eta_th
		
		self.check(self.thermoOutputParams)
	

		
	def calcAero(self):
		"""Diese Methode berechnet die Aerodynamischen Eckdaten der Komponenten"""
		
		self.check(self.aeroInputParams)
		self.fan.check(self.fan.aeroInputParams)
		self.hpc.check(self.hpc.aeroInputParams)
		self.combc.check(self.combc.aeroInputParams)
		self.hpt.check(self.hpt.aeroInputParams)
		self.lpt.check(self.lpt.aeroInputParams)
		
		#=======================================================================
		# Fan
		#=======================================================================
		#Die Stirnfläche des Fans und der Nabenradius sind die zentralen Auslegungsgrößen für die Geometrie
		#Daraus leitet sich der Gehäuseradius ab:
		#self.fan.r_s1=numpy.sqrt(self.fan.A_1/numpy.pi+self.fan.r_h1**2)
		self.fan.A_1=numpy.pi*(self.fan.r_s1**2.0-self.fan.r_h1**2.0)
		#Und die Eintrittsgeschwindigkeiten:
		self.fan.c_1=self.fan.mflow/self.fan.rho_1/self.fan.A_1
		#Die Schallgeschwindigkeit am Eintritt ist:
		a_1=numpy.sqrt(self.fan.kappa*self.fan.R*self.T_inf)
		#Die Grenze der relativen Anströmgeschwindigkeit soll festgelegt werden. Diese wird am Gehäuse erreicht.
		w_g1=self.Ma_max*a_1
		#Daraus ergibt sich die Umfangsgeschwindigkeit und die Drehzahl:
		u_g1=numpy.sqrt(w_g1**2.0-self.fan.c_1**2.0)
		self.fan.n=u_g1/self.fan.r_s1/numpy.pi*30.0
		
		#Mit diesen Parametern kann nun die aerodynamische 1D-Berechnung des Fans erfolgen:
		self.fan.calcAero()
				
		#=======================================================================
		# Radialverdichter
		#=======================================================================
		self.hpc.c_1=self.fan.c_3 # Konstanter Strömungskanalquerschnitt
		self.hpc.c_ax1=self.hpc.c_1 #Drallfreie Anströmung!
		self.hpc.c_u1=0.0
		self.hpc.p_t1=self.fan.p_t3
		self.hpc.T_t1=self.fan.T_t3
		self.hpc.calcAero()

		#=======================================================================
		# Brennkammer
		#=======================================================================		
		self.combc.c_1=self.hpc.c_3*0.5 #annahme diffusor mit c2/c1=0.5
		self.combc.p_t1=self.hpc.p_t3		#Evtl noch Druckverlust des Diffusors manuell oder evtl mit Diffusorklasse dazwischen
		self.combc.calcAero()
		
		#=======================================================================
		# Hochdruckturbine
		#=======================================================================
		self.hpt.c_1=self.combc.c_3
		self.hpt.p_t1=self.combc.p_t3		
		self.hpt.n=self.hpc.n
		self.hpt.calcAero()
		
		#=======================================================================
		# Niederdruckturbine
		#=======================================================================
		self.lpt.c_1=self.hpt.c_3
		self.lpt.p_t1=self.hpt.p_t3
		self.lpt.n=self.fan.n
		self.lpt.alpha_1=self.hpt.alpha_3
		self.lpt.calcAero()
		
		#=======================================================================
		# Hot nozzle
		#=======================================================================
		self.hn.p_3=self.p_inf	#Annhame: Ideale Duesenexpansion => Stat. Druck im Duesenaustritt = Umgebungsdruck
		self.hn.p_t1=self.lpt.p_t3	#Evtl noch Druckverlust des Uebergangsstuecks oder evtl mit Diffusorklasse dazwischen
		self.hn.r_h3=0.0	 #Annahme: Hotnozzle ist kreisfoermig => r_h3 ist 0
		self.hn.calcAero()
		
		#=======================================================================
		# Cold nozzle
		#=======================================================================
		self.cn.p_3=self.p_inf		#Annhame: Ideale Duesenexpansion => Stat. Druck im Duesenaustritt = Umgebungsdruck
		self.cn.p_t1=self.fan.p_t3	#Evtl noch Druckverlust des Nebenstromkanals oder evtl mit Diffusorklasse dazwischen
		self.cn.r_h3=self.hn.r_s3	#Coldnozzle ist kreisringfoermig => self.cn.r_h3 =self.hn.r_s3		
		self.cn.calcAero()


		self.F_recalc=self.hn.c_3*self.hn.mflow+self.cn.c_3*self.cn.mflow #Berechnung des Schubes mit Duesengeschwindigkeiten und Massenstroemen
		
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

			#Einlauf
			tsplot.isotherme("T_t12",self.fan.p_t1)
			#Fan
			tsplot.polytrope("T_t13",self.fan.eta_pol,pend=self.fan.p_t3)
			#Splitter
			tsplot.isotherme("T_t2",self.hpc.p_t1)
			#Zwischenspeichen für Verzweigung
			s=tsplot.s
			p=tsplot.p
			T=tsplot.T
			
			#tsplot.addnewStart("H_t2",self.mflow_h,T,s,p)
			#Radialverdichter
			tsplot.polytrope("T_t3",self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			tsplot.isobare("T_t4",self.combc.T_t3)
			#h-Turbine
			tsplot.polytrope("T_t52",self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#l-Turbine
			tsplot.polytrope("T_t53",self.lpt.eta_pol,Tend=self.lpt.T_t3)
			#Düse
			tsplot.isotherme("T_t8",self.hn.p_t3)
			#Entspannung
			tsplot.isentrope("T_t9",pend=self.p_tinf)
			tsplot.isobare("",self.T_tinf)
			
			tsplot.addnewStart("",T,s,p)
			#Düse
			tsplot.isotherme("T_t18",self.cn.p_t3)
			#Entspannung
			tsplot.isentrope("T_t19",pend=self.p_tinf)
			

			tsplot.pWidget.draw()
			
			
			hsplot.pyl.clear()
			hsplot.pWidget.format_labels()
			hsplot.addnewStart("H_t0",self.mflow,self.T_tinf,0.0,self.p_tinf)
			#Einlauf
			hsplot.isotherme("H_t12",self.mflow,self.fan.p_t1)
			#Fan
			hsplot.polytrope("H_t13",self.mflow,self.fan.eta_pol,pend=self.fan.p_t3)
			#Splitter
			hsplot.isotherme("H_t2",self.mflow,self.hpc.p_t1)
			#Zwischenspeichen für Verzweigung
			s=hsplot.S
			p=hsplot.p
			T=hsplot.T
			
			hsplot.addnewStart("H_t2",self.mflow_h,T,s,p)
			#Radialverdichter
			hsplot.polytrope("H_t3",self.mflow_h,self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			hsplot.isobare("H_t4",self.mflow_h,self.combc.T_t3)
			#h-Turbine
			hsplot.polytrope("H_t52",self.mflow_h,self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#l-Turbine
			hsplot.polytrope("H_t53",self.mflow_h,self.lpt.eta_pol,Tend=self.lpt.T_t3)
			#Düse
			hsplot.isotherme("H_t8",self.mflow_h,self.hn.p_t3)
			#Entspannung
			hsplot.isentrope("H_t9",self.mflow_h,pend=self.p_tinf)
			hsplot.isobare("",self.mflow_h,self.T_tinf)
			
			hsplot.addnewStart("H_t2",self.mflow_c,T,s,p)
			#Düse
			hsplot.isotherme("H_t18",self.mflow_c,self.cn.p_t3)
			#Entspannung
			hsplot.isentrope("H_t19",self.mflow_c,pend=self.p_tinf)
			hsplot.isobare("",self.mflow_c,self.T_tinf)
			
			
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
		
		
		
		
		
		
		

#===============================================================================
# Klasse zur Auslegung und Berechnung von Turbofantriebwerken	
#===============================================================================
class Turbofan_Recalc(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Turbofan_Recalc'
		
		self.thermoInputParams=[["c_0","m/s","Airspeed of incident flow"],\
								["mflow","kg/s","Total Massflow"],\
								["p_inf","Pa","Air pressure"],\
								["T_inf","K","Air temperature"],\
								["bypassRatio","-","Ratio of cold massflow to hot massflow"],\
								["Pi_inlet","-","Total pressure loss of inlet"],\
								["Pi_splitter","-","Total pressure loss of the splitter"],\
								["eta_mech_hps","-","Efficiency of high pressure shaft"],\
								["eta_mech_lps","-","Efficiency of low pressure shaft"]]
		
		
		self.thermoOutputParams=[
								["mflow_h","kg/s","Hot Massflow"],\
								["mflow_c","kg/s","Cold Massflow"],\
								["c_19","m/s","Velocity cold flow"],\
								["c_9","m/s","Velocity hot flow"],\
								["F_fan","N","thrust fan"],\
								["F_main","N","thrust main"],\
								["F","N","total thrust"],\
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
		self.subcomponentList=[ \
								["fan", compressor.CompressorAxial("Fan")],\
								["hpc", compressor.CompressorRadial("High Pressure Compressor")],\
								["combc", combChamber.CombChamber("Combustion Chamber")],\
								["hpt", turbine.Turbine("High Pressure Turbine")],\
								["lpt", turbine.Turbine("Low Pressure Turbine")],\
								["hn", nozzle.Nozzle("Nozzle for hot massflow")],\
								["cn", nozzle.Nozzle("Nozzle for cold massflow")]\
								]
		
		#Initialise global variables from dictionary
		self.setVariablesFromList(self.subcomponentList)
		
		#Delete input parameters computed by turbofan
		self.removeComputedParams(self.fan,["mflow","T_t1","p_t1"],[])
		self.removeComputedParams(self.hpc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.combc,["mflow","T_t1","p_t1"],["p_t1"])
		self.removeComputedParams(self.hpt,["mflow","deltaP","p_t1","T_t1","beta"],["n","c_1","p_t1"]) #hpt.c_1 der soll nicht eingegeben werden muessen fuer gesamte Turbofanberechnung 
		self.removeComputedParams(self.lpt,["mflow","deltaP","p_t1","T_t1","beta"],["n","c_1","p_t1","alpha_1"])
		self.removeComputedParams(self.hn,["mflow","T_t1","p_t1","beta"],["p_3"])		
		self.removeComputedParams(self.cn,["mflow","T_t1","p_t1","beta"],["p_3"])
		
		
		
		
		#Default Values:
		self.p_inf=101325.
		self.T_inf=288.15
		self.kappa_inf=getKappa(Tt=self.T_inf,Ma=0)
		self.R_inf=287.15
		self.eta_mech_hps=0.98
		self.eta_mech_lps=0.98
		self.c_0=0.0
		self.Pi_splitter=0.95
		self.Pi_inlet=0.95
		
	
	def calcThermo(self):
		"""Diese Methode berechnet die Eckdaten des Kreisprozesses"""
		
		self.check(self.thermoInputParams)
		self.fan.check(self.fan.thermoInputParams)
		self.hpc.check(self.hpc.thermoInputParams)
		self.combc.check(self.combc.thermoInputParams)
		self.hpt.check(self.hpt.thermoInputParams)
		self.lpt.check(self.lpt.thermoInputParams)
		
		self.R=getR()
		
		#Schallgeschwindigkeit in der Umgebung
		a_0=numpy.sqrt(self.kappa_inf*self.R_inf*self.T_inf)
		
		#Inlet Mach number (ohne Einlauf)
		Ma_0=self.c_0/a_0
		
		#Total temperature inlet engine
		self.T_tinf=self.T_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)
		
		#Total pressure inlet engine
		self.p_tinf=self.p_inf*(1+(self.kappa_inf-1)/2*Ma_0**2)**(self.kappa_inf/(self.kappa_inf-1))
		
		self.mflow_h=self.mflow/(self.bypassRatio+1)
		
		self.mflow_c=self.mflow*self.bypassRatio/(self.bypassRatio+1)
			
		#Initialisiere Massenströme der Komponenten
		self.fan.mflow=self.mflow
		self.hpc.mflow=self.mflow_h
		self.combc.mflow=self.mflow_h
		self.cn.mflow=self.mflow_c	
	
		#Berechne Thermodynamischen Kreisprozess
		#low pressure compressor
		self.fan.p_t1=self.p_tinf*self.Pi_inlet
		self.fan.T_t1=self.T_tinf
		self.fan.calcThermo()
		
		#high pressure compressor
		self.hpc.p_t1=self.fan.p_t3*self.Pi_splitter
		self.hpc.T_t1=self.fan.T_t3
		self.hpc.calcThermo()	
		
		#combustion chamber
		self.combc.p_t1=self.hpc.p_t3
		self.combc.T_t1=self.hpc.T_t3
		self.combc.calcThermo()
		
		self.hpt.mflow=self.mflow_h+self.combc.beta*self.mflow_h
		self.lpt.mflow=self.mflow_h+self.combc.beta*self.mflow_h
		self.hn.mflow=self.mflow_h+self.combc.beta*self.mflow_h
		
		#high pressure turbine
		self.hpt.R=self.combc.R_ex
		self.hpt.p_t1=self.combc.p_t3
		self.hpt.T_t1=self.combc.T_t3
		self.hpt.deltaP=self.hpc.deltaP/self.eta_mech_hps
		self.hpt.beta=self.combc.beta
		self.hpt.calcThermo()
		
		#low pressure turbine
		self.lpt.R=self.combc.R_ex
		self.lpt.p_t1=self.hpt.p_t3
		self.lpt.T_t1=self.hpt.T_t3
		self.lpt.deltaP=self.fan.deltaP/self.eta_mech_lps
		self.lpt.beta=self.combc.beta
		self.lpt.calcThermo()
		
		#hot nozzle
		self.hn.R=self.combc.R_ex
		self.hn.T_t1=self.lpt.T_t3
		self.hn.p_t1=self.lpt.p_t3
		self.hn.beta=self.combc.beta
		self.hn.calcThermo()
		
		#cold nozzle
		self.cn.R=self.R_inf
		self.cn.T_t1=self.fan.T_t3
		self.cn.p_t1=self.fan.p_t3*self.Pi_splitter
		self.cn.calcThermo()
		
		#schub berechnen
		#Ma cold nozzle outlet
		self.Ma_19=(((self.cn.p_t3/self.p_inf)**((self.fan.kappa-1)/self.fan.kappa)-1)*2/(self.fan.kappa-1))**0.5
		
		self.T_19=self.fan.T_t3/(1+(self.fan.kappa-1)/2*self.Ma_19**0.5)
		
		self.a_19=(self.fan.kappa*self.R_inf*self.T_19)**0.5
		
		self.c_19=self.Ma_19*self.a_19
		
		self.F_fan=(self.c_19-self.c_0)*self.mflow_c
		
		#Ma hot nozzle outlet
		self.Ma_9=(((self.hn.p_t3/self.p_inf)**((self.lpt.kappa_3-1)/self.lpt.kappa_3)-1)*2/(self.lpt.kappa_3-1))**0.5
		
		self.T_9=self.lpt.T_t3/(1+(self.lpt.kappa_3-1)/2*self.Ma_9**0.5)
		
		self.a_9=(self.lpt.kappa_3*self.combc.R_ex*self.T_9)**0.5
		
		self.c_9=self.Ma_9*self.a_9
		
		self.F_main=(self.c_9-self.c_0)*(self.mflow_h+self.combc.beta*self.mflow_h)
		
		self.mflow_f=self.combc.beta*self.mflow_h
		
		self.F=self.F_main+self.F_fan
		
		#SFC
		self.SFC=self.combc.mflow_f*3600./self.F*1000.
		
		#Thermischer Wirkungsgrad
		self.eta_th=((self.mflow_h+self.combc.mflow_f)*self.c_9**2+(self.mflow_c)*self.c_19**2-self.mflow*self.c_0**2)/2./self.combc.deltaP
		
		#Vortriebswirkungsgrad
		self.eta_p=2.*(self.F*self.c_0)/((self.mflow_h+self.combc.beta*self.mflow_h)*self.c_9**2+self.mflow_c*self.c_19**2-self.mflow*self.c_0**2)
		
		#Gesamtwirkungsgrad
		self.eta_tot=self.eta_p*self.eta_th
		
		self.check(self.thermoOutputParams)
	

		
	def calcAero(self):
		"""Diese Methode berechnet die Aerodynamischen Eckdaten der Komponenten"""
		
		self.check(self.aeroInputParams)
		self.fan.check(self.fan.aeroInputParams)
		self.hpc.check(self.hpc.aeroInputParams)
		self.combc.check(self.combc.aeroInputParams)
		self.hpt.check(self.hpt.aeroInputParams)
		self.lpt.check(self.lpt.aeroInputParams)
		
		#=======================================================================
		# Fan
		#=======================================================================
		#Die Stirnfläche des Fans und der Nabenradius sind die zentralen Auslegungsgrößen für die Geometrie
		#Daraus leitet sich der Gehäuseradius ab:
		#self.fan.r_s1=numpy.sqrt(self.fan.A_1/numpy.pi+self.fan.r_h1**2)
		self.fan.A_1=numpy.pi*(self.fan.r_s1**2.0-self.fan.r_h1**2.0)
		#Und die Eintrittsgeschwindigkeiten:
		self.fan.c_1=self.fan.mflow/self.fan.rho_1/self.fan.A_1
		#Die Schallgeschwindigkeit am Eintritt ist:
		a_1=numpy.sqrt(self.fan.kappa*self.fan.R*self.T_inf)
		#Die Grenze der relativen Anströmgeschwindigkeit soll festgelegt werden. Diese wird am Gehäuse erreicht.
		w_g1=self.Ma_max*a_1
		#Daraus ergibt sich die Umfangsgeschwindigkeit und die Drehzahl:
		u_g1=numpy.sqrt(w_g1**2.0-self.fan.c_1**2.0)
		self.fan.n=u_g1/self.fan.r_s1/numpy.pi*30.0
		
		#Mit diesen Parametern kann nun die aerodynamische 1D-Berechnung des Fans erfolgen:
		self.fan.calcAero()
				
		#=======================================================================
		# Radialverdichter
		#=======================================================================
		self.hpc.c_1=self.fan.c_3 # Konstanter Strömungskanalquerschnitt
		self.hpc.c_ax1=self.hpc.c_1 #Drallfreie Anströmung!
		self.hpc.c_u1=0.0
		self.hpc.p_t1=self.fan.p_t3
		self.hpc.T_t1=self.fan.T_t3
		self.hpc.calcAero()

		#=======================================================================
		# Brennkammer
		#=======================================================================		
		self.combc.c_1=self.hpc.c_3*0.5 #annahme diffusor mit c2/c1=0.5
		self.combc.p_t1=self.hpc.p_t3		#Evtl noch Druckverlust des Diffusors manuell oder evtl mit Diffusorklasse dazwischen
		self.combc.calcAero()
		
		#=======================================================================
		# Hochdruckturbine
		#=======================================================================
		self.hpt.c_1=self.combc.c_3
		self.hpt.p_t1=self.combc.p_t3		
		self.hpt.n=self.hpc.n
		self.hpt.calcAero()
		
		#=======================================================================
		# Niederdruckturbine
		#=======================================================================
		self.lpt.c_1=self.hpt.c_3
		self.lpt.p_t1=self.hpt.p_t3
		self.lpt.n=self.fan.n
		self.lpt.alpha_1=self.hpt.alpha_3
		self.lpt.calcAero()
		
		#=======================================================================
		# Hot nozzle
		#=======================================================================
		self.hn.p_3=self.p_inf	#Annhame: Ideale Duesenexpansion => Stat. Druck im Duesenaustritt = Umgebungsdruck
		self.hn.p_t1=self.lpt.p_t3	#Evtl noch Druckverlust des Uebergangsstuecks oder evtl mit Diffusorklasse dazwischen
		self.hn.r_h3=0.0	 #Annahme: Hotnozzle ist kreisfoermig => r_h3 ist 0
		self.hn.calcAero()
		
		#=======================================================================
		# Cold nozzle
		#=======================================================================
		self.cn.p_3=self.p_inf		#Annhame: Ideale Duesenexpansion => Stat. Druck im Duesenaustritt = Umgebungsdruck
		self.cn.p_t1=self.fan.p_t3	#Evtl noch Druckverlust des Nebenstromkanals oder evtl mit Diffusorklasse dazwischen
		self.cn.r_h3=self.hn.r_s3	#Coldnozzle ist kreisringfoermig => self.cn.r_h3 =self.hn.r_s3		
		self.cn.calcAero()


		self.F_recalc=self.hn.c_3*self.hn.mflow+self.cn.c_3*self.cn.mflow #Berechnung des Schubes mit Duesengeschwindigkeiten und Massenstroemen
		
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

			#Einlauf
			tsplot.isotherme("T_t12",self.fan.p_t1)
			#Fan
			tsplot.polytrope("T_t13",self.fan.eta_pol,pend=self.fan.p_t3)
			#Splitter
			tsplot.isotherme("T_t2",self.hpc.p_t1)
			#Zwischenspeichen für Verzweigung
			s=tsplot.s
			p=tsplot.p
			T=tsplot.T
			
			#tsplot.addnewStart("H_t2",self.mflow_h,T,s,p)
			#Radialverdichter
			tsplot.polytrope("T_t3",self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			tsplot.isobare("T_t4",self.combc.T_t3)
			#h-Turbine
			tsplot.polytrope("T_t52",self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#l-Turbine
			tsplot.polytrope("T_t53",self.lpt.eta_pol,Tend=self.lpt.T_t3)
			#Düse
			tsplot.isotherme("T_t8",self.hn.p_t3)
			#Entspannung
			tsplot.isentrope("T_t9",pend=self.p_tinf)
			tsplot.isobare("",self.T_tinf)
			
			tsplot.addnewStart("",T,s,p)
			#Düse
			tsplot.isotherme("T_t18",self.cn.p_t3)
			#Entspannung
			tsplot.isentrope("T_t19",pend=self.p_tinf)
			

			tsplot.pWidget.draw()
			
			
			hsplot.pyl.clear()
			hsplot.pWidget.format_labels()
			hsplot.addnewStart("H_t0",self.mflow,self.T_tinf,0.0,self.p_tinf)
			#Einlauf
			hsplot.isotherme("H_t12",self.mflow,self.fan.p_t1)
			#Fan
			hsplot.polytrope("H_t13",self.mflow,self.fan.eta_pol,pend=self.fan.p_t3)
			#Splitter
			hsplot.isotherme("H_t2",self.mflow,self.hpc.p_t1)
			#Zwischenspeichen für Verzweigung
			s=hsplot.S
			p=hsplot.p
			T=hsplot.T
			
			hsplot.addnewStart("H_t2",self.mflow_h,T,s,p)
			#Radialverdichter
			hsplot.polytrope("H_t3",self.mflow_h,self.hpc.eta_pol,pend=self.hpc.p_t3)
			#Brennkammer
			hsplot.isobare("H_t4",self.mflow_h,self.combc.T_t3)
			#h-Turbine
			hsplot.polytrope("H_t52",self.mflow_h,self.hpt.eta_pol,Tend=self.hpt.T_t3)
			#l-Turbine
			hsplot.polytrope("H_t53",self.mflow_h,self.lpt.eta_pol,Tend=self.lpt.T_t3)
			#Düse
			hsplot.isotherme("H_t8",self.mflow_h,self.hn.p_t3)
			#Entspannung
			hsplot.isentrope("H_t9",self.mflow_h,pend=self.p_tinf)
			hsplot.isobare("",self.mflow_h,self.T_tinf)
			
			hsplot.addnewStart("H_t2",self.mflow_c,T,s,p)
			#Düse
			hsplot.isotherme("H_t18",self.mflow_c,self.cn.p_t3)
			#Entspannung
			hsplot.isentrope("H_t19",self.mflow_c,pend=self.p_tinf)
			hsplot.isobare("",self.mflow_c,self.T_tinf)
			
			
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