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
import scipy
from scipy import optimize
from numpy import linspace, zeros, matrix, ma
from abstract import *
from helper_methods import *

#===============================================================================
# Klasse zur Definition und Berechnung eines Axialverdichters
#===============================================================================
class CompressorAxial(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Axial Compressor'
		
		self.thermoInputParams=[["T_t1","K","Total temperature at layer 1"],\
								["p_t1","-","Total pressure inlet"],\
								["Pi","-","Total pressure ratio between layer 1 and 3"],\
								["eta_pol","-",""],\
								["Ma_inlet","-","Approximate Mach number at inlet (0.4-0.6)"],\
								["Ma_outlet","-","Approximate Mach number at outlet (0.4-0.6)"],\
								["mflow","kg/s","Massflow"]]
		self.thermoOutputParams=[["T_t3","K","Total temperature at layer 3 (outlet)"],\
								["p_t3","-","Total pressure outlet"],\
								["R","J/(mol kg)","Specific gas constant of gas entering nozzle"],\
								["deltaP","W","Power of the stage"]]
		
		self.aeroInputParams=[["p_t1","Pa","Stagnation pressure at layer 1 (rotor-inlet)"],\
								["r_h1","m","Radius at Hub at layer 1"],\
								["r_s1","m","Radius at Shroud at layer 1"],\
								["z_1","m","z-Coordinate at layer 1"],\
								["alpha_1","deg","Absolute flow angle at layer 1 (rotor-inlet)"],\
								["alpha_3","deg","Optional: Absolute flow angle at layer 3 (stator-outlet)"],\
								["c_3toc_1","",""],\
								["reaction","-",""],\
								["diffusion_rotor","-","Diffusionfactor according to Lieblein rotor"],\
								["diffusion_stator","-","Diffusionfactor according to Lieblein stator"],\
								["b_to_s_rotor","-","Ratio of blade length to chord length rotor"],\
								["b_to_s_stator","-","Ratio of blade length to chord length stator"],\
								["rho_rotormaterial","kg/m^3","Density of the rotorblade-material"],\
								["n","1/min",""]]
		self.aeroOutputParams=[	["p_1","Pa","Static pressure at layer 1 (rotor-inlet)"],\
								["T_1","K","Static pressure at layer 1 (rotor-inlet)"],\
								["Ma_1","-","Mach number at layer 1 (rotor-inlet)"],\
								["c_1","m/s","Norm of absolute velocity at layer 1 (rotor-inlet)"],\
								["c_u1","m/s","Circumferential velocity at layer 1 (rotor-inlet)"],\
								#["c_1_check","m/s","Norm of absolute velocity at layer 1 (check)"],\
								["u_1","m/s","Norm of circumferential velocity at layer 1 (rotor-inlet)"],\
								["w_1","m/s","Norm of relative velocity at layer 1 (rotor-inlet)"],\
								["T_2","K","Static Temperatur at layer 2 (rotor-outlet)"],\
								["Ma_2","-","Mach number at layer 2 (rotor-outlet)"],\
								["c_2","m/s","Norm of absolute velocity at layer 2 (rotor-outlet)"],\
								["c_u2","m/s","Circumferential velocity at layer 2 (rotor-outlet)"],\
								["u_2","m/s","Norm of circumferential velocity at layer 2 (rotor-outlet)"],\
								["w_2","m/s","Norm of relative velocity at layer 2 (rotor-outlet)"],\
								["p_t3","Pa","Stagnation pressure at layer 3 (stator-outlet)"],\
								["p_3","Pa","Static pressure at layer 3 (stator-outlet)"],\
								["Ma_3","-","Mach number at layer 3 (stator-outlet)"],\
								["c_3","m/s","Norm of absolute velocity at layer 3 (stator-outlet)"],\
								["c_u3","m/s","Norm of circumferential velocity at layer 3 (stator-outlet)"],\
								["c_ax3","m/s","Norm of axial velocity at layer 3 (stator-outlet)"],\
								["T_3","K","Static Temperatur at layer 3 (rotor-outlet)"],\
								["beta_1","deg","Relative flow angle at layer 1 (stator-inlet) with respect to vertical direction"],\
								["beta_2","deg","Relative flow angle at layer 2 (rotor-outlet) with respect to vertical direction"],\
								["alpha_2","deg","Absolute flow angle at layer 2 (rotor-outlet) with respect to vertical direction"],\
								["r_h2","m","Radius of hub at layer 2 (rotor-outlet)"],\
								["r_s2","m","Radius of shroud at layer 2 (rotor-outlet)"],\
								["b_2","m","Radial extension of layer 2 (rotor-outlet)"],\
								["r_m1","m","Radius of merdian-layer"],\
								["r_h3","m","Radius of hub at layer 3 (stator-outlet)"],\
								["r_s3","m","Radius of shroud at layer 3 (stator-outlet)"],\
								["b_3","m","Radial extension of layer 3 (stator-outlet)"],\
								["DeHaller_rotor","-","DeHaller criterion for rotor"],\
								["DeHaller_stator","-","DeHaller criterion for stator"],\
								["pitch_ratio_rotor","-","Space-to-chord ratio t/s rotor"],\
								["pitch_ratio_stator","-","Space-to-chord ratio t/s stator"],\
								["pitch_ratio_recalc_rotor","-","Recalculated Space-to-chord ratio t/s rotor"],\
								["pitch_ratio_recalc_stator","-","Recalculated Space-to-chord ratio t/s stator"],\
								["s_rotor","m","Chord length of rotor"],\
								["s_stator","m","Chord length of stator"],\
								["z_calc_rotor","-","Analytic number of rotor-blades (to be set to integer)"],\
								["z_calc_stator","-","Analytic number of stator-blades (to be set to integer)"],\
								["z_chosen_stator","-","Selected prime-numer of stator-blades"],\
								["z_chosen_rotor","-","Selected prime-numer of rotor-blades"],\
								["deviation_angle_rotor","deg","Difference between blade- and flowanlge rotor (Minderumlenkungswinkel)"],\
								["deviation_angle_stator","deg","Difference between blade- and flowanlge stator (Minderumlenkungswinkel)"],\
								["gamma_stator","deg","Stagger angle stator"],\
								["gamma_rotor","deg","Stagger angle rotor"],\
								["gitterbelastung_rotor","-","Gitterbelastungszahl rotor"],\
								["gitterbelastung_stator","-","Gitterbelastungszahl stator"],\
								["c_a_rotor","-","Lift coefficient rotor"],\
								["c_a_stator","-","Lift coefficient stator"],\
								["sigma_z_bladeroot","N/mm^2","Centrifugal stress bladeroot"],\
								["z_2","m",""],\
								["z_3","m",""]]
								
		self.modularSubfunctionList.append(self.addTabBladeDesign)
		
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#defaults:
		self.z_1=0.0
		self.p_t1=101325
		self.Ma_inlet=0.5
		self.Ma_outlet=0.5
		self.alpha_1=90.0 #Drallfreie Anstroemung
		self.alpha_3=90.0 #Drallfreie Abstroemung
		self.c_3toc_1=1.0 #Geschwindigkeitsverhaeltnis von c_3 zu c_1 auf Repetierstufencharakter gesetzt
		self.reaction=0.5
		self.R=287.15
		self.kappa=1.4
		self.radius_const="rm" # "casing" fuer konstanten Gehaeuseradius, "rm" für konstanten Mittelschnittsradius, "hub" für konstanten Nabenradius!  
		self.rho_rotormaterial=2800.0 #Dichte von Aluminium!	
	#===========================================================================
	# Berechnungsmethode fuer thermodynamische Parameter
	#===========================================================================
	def calcThermo(self):
		self.check(self.thermoInputParams)
		
		self.R=getR()
		
		self.p_t3=self.p_t1*self.Pi

		self.T_t3=polytrope(eta_pol=self.eta_pol,T1=self.T_t1,p1=self.p_t1,p2=self.p_t3,Ma=self.Ma_outlet)
		
		kappa_1=getKappa(Tt=self.T_t1,Ma=self.Ma_inlet)
		kappa_3=getKappa(Tt=self.T_t3,Ma=self.Ma_outlet)
		self.kappa=(kappa_1+kappa_3)/2
		
		self.T_t2=self.T_t3	#Adiabates Leitrad
		
		self.deltaP=self.mflow*self.kappa/(self.kappa-1.)*self.R*(self.T_t3-self.T_t1)

		#self.kappa=getKappa(Tt=((self.T_t3+self.T_t1)/2),Ma=self.Ma_inlet)
		
		
		

		self.check(self.thermoOutputParams)
		

	#===========================================================================
	# Berechnungsmethode fuer aerodynamische und geometrische Parameter der Stufe
	#===========================================================================
	def calcAero(self):
		self.check(self.aeroInputParams)
		
		A_1=numpy.pi*(self.r_s1**2.0-self.r_h1**2.0)
		#Der mittlere Radius bestimmt sich aus der flaechengleichen Halbierung zwischen Nabe und Gehaeuse
		self.r_m1=numpy.sqrt((self.r_h1**2.0+self.r_s1**2.0)/2.0)
		def fkt(Ma_1):
			F=self.mflow*numpy.sqrt(self.T_t1*self.R)/(self.p_t1*A_1*numpy.sin(numpy.radians(self.alpha_1)))-\
			(numpy.sqrt(self.kappa)*Ma_1*(1.0+(self.kappa-1.0)/2.0*(Ma_1**2.0))**(-0.5*(self.kappa+1.0)/(self.kappa-1.0)))
			
			return F
		self.Ma_1=scipy.optimize.fsolve(fkt,0.6)
		
	
		self.p_1=self.p_t1/(1.0+(self.kappa-1.0)/2.0*self.Ma_1**2.0)**(self.kappa/(self.kappa-1.0))
		self.T_1=self.T_t1/(1.0+(self.kappa-1.0)/2.0*self.Ma_1**2.0)
		rho_1=self.p_1/(self.R*self.T_1)
		
		self.c_ax1=self.mflow/(A_1*rho_1)
		self.c_1=self.c_ax1/numpy.sin(numpy.radians(self.alpha_1))
		self.c_u1=self.c_1*numpy.cos(numpy.radians(self.alpha_1))
		
		
		#Dieser auskommentierte Abschnitt dient dazu, c_1 mit einer anderen Berechnungsweise zu vergleichen
		'''c_1_check=numpy.sqrt(2.0*self.kappa/(self.kappa-1.0)*self.R*(self.T_t1-self.T_1))
		print "c_1_check:", c_1_check		
		print "c_1", self.c_1'''
	
		self.u_1=self.n*numpy.pi/30.0*self.r_m1
		self.w_u1=self.c_u1-self.u_1
		self.w_ax1=self.c_ax1	#Meridionalkomponenten = Achskomponente hier sind unabhaengig vom Bezugssystem
		self.w_1=numpy.sqrt(self.w_ax1**2.0+self.w_u1**2.0)

		self.beta_1=numpy.degrees(numpy.pi-numpy.arctan2(self.w_ax1,-1.0*self.w_u1)) #Definition von arctan2 und Winkelkonvention beachten!
		self.omega=self.n*numpy.pi/30.0
		

		#Ebene 3
		self.p_t3=self.p_t1*self.Pi
		self.c_3=self.c_1*self.c_3toc_1
		self.c_ax3=numpy.sin(numpy.radians(self.alpha_3))*self.c_3 
		self.c_u3=numpy.cos(numpy.radians(self.alpha_3))*self.c_3 
		self.T_3=self.T_t3-(self.c_3**2.0)/(2.0*self.kappa*self.R/(self.kappa-1.0))
		a_3=numpy.sqrt(self.T_3*self.kappa*self.R)
		self.Ma_3=self.c_3/a_3
		self.p_3=self.p_t3/((1.0+(self.kappa-1.0)/2.0*(self.Ma_3**2.0))**(self.kappa/(self.kappa-1.0)))
		rho_3=self.p_3/(self.R*self.T_3)
		
		A_3=self.mflow/(self.c_ax3*rho_3)
		if self.radius_const=="rm":		
			self.r_m3=self.r_m1
			self.r_s3=numpy.sqrt((A_3/(2.0*numpy.pi))+(self.r_m3**2.0))
			self.r_h3=numpy.sqrt((self.r_m3**2.0)-(A_3/(2.0*numpy.pi)))
		elif self.radius_const=="casing":
			self.r_s3=self.r_s1
			self.r_m3=numpy.sqrt((self.r_s3**2.0)-(A_3/(2.0*numpy.pi)))
			self.r_h3=numpy.sqrt((self.r_m3**2.0)-(A_3/(2.0*numpy.pi)))
		elif self.radius_const=="hub":
			self.r_h3=self.r_h1
			self.r_m3=numpy.sqrt((A_3/(2.0*numpy.pi))-(self.r_h3**2.0))
			self.r_s3=numpy.sqrt((A_3/(2.0*numpy.pi))+(self.r_m3**2.0))
		self.b_3=self.r_s3-self.r_h3

		
		#Ebene 2
		
		self.T_2=self.reaction*(self.T_3-self.T_1)+self.T_1
		self.c_2=numpy.sqrt(2.0*self.kappa*self.R/(self.kappa-1.0)*(self.T_t2-self.T_2))
		self.r_m2=(self.r_m1+self.r_m3)/2.0
		self.u_2=self.n*numpy.pi/30.0*self.r_m2
		self.c_u2=((self.kappa*self.R/(self.kappa-1.0)*(self.T_t2-self.T_t1))+(self.c_u1*self.u_1))/self.u_2
		self.c_ax2=numpy.sqrt((self.c_2**2.0)-(self.c_u2**2.0))
				
		self.w_u2=self.c_u2-self.u_2
		self.w_ax2=self.c_ax2 #Meridionalkomponenten = Achskomponente hier sind unabhaengig vom Bezugssystem
		self.w_2=numpy.sqrt((self.w_u2**2.0)+(self.w_ax2**2.0))		
		
		#print self.w_1,self.w_2,self.c_1,self.c_2,self.u_1,self.u_2
		
		a_2=numpy.sqrt(self.T_2*self.kappa*self.R)
		self.Ma_2=self.c_2/a_2
		
		self.alpha_2=numpy.degrees(numpy.arccos(self.c_u2/self.c_2))
		self.beta_2=numpy.degrees(numpy.pi-numpy.arctan2(self.w_ax2,-1.0*self.w_u2))	#Definition von arctan2 und Winkelkonvention beachten!		
		
		#Annahme des Druckverlustes über den Stator von 0.93
		self.p_2=self.p_t3*0.93/(self.T_t2/self.T_2)**(self.kappa/(self.kappa-1.))
		rho_2=self.p_2/(self.R*self.T_2)
		
		A_2=self.mflow/self.c_ax2/rho_2
		if self.radius_const=="rm":		
			self.r_m2=self.r_m1
			self.r_s2=numpy.sqrt((A_2/(2.0*numpy.pi))+(self.r_m2**2.0))
			self.r_h2=numpy.sqrt((self.r_m2**2.0)-(A_2/(2.0*numpy.pi)))
		elif self.radius_const=="casing":
			self.r_s2=self.r_s1
			self.r_m2=numpy.sqrt((self.r_s2**2.0)-(A_2/(2.0*numpy.pi)))
			self.r_h2=numpy.sqrt((self.r_m2**2.0)-(A_2/(2.0*numpy.pi)))
		elif self.radius_const=="hub":
			self.r_h2=self.r_h1
			self.r_m2=numpy.sqrt((A_2/(2.0*numpy.pi))-(self.r_h2**2.0))
			self.r_s2=numpy.sqrt((A_2/(2.0*numpy.pi))+(self.r_m2**2.0))
		
		#self.r_s2=(self.r_s1+self.r_s3)/2.0
		#self.r_h2=(self.r_h1+self.r_h3)/2.0
		#A_2=numpy.pi*(self.r_h2**2.0-self.r_s2**2.0)	#Zusaetliche Groesse, die eig. nicht benoetigt wird, evtl fuer Kontrollzwecke 
		self.b_2=self.r_s2-self.r_h2
		
		#Berechnung der Gitterbelastungskriterien

		#De-Haller Kriterien fuer Rotor und Stator
		self.DeHaller_rotor=self.w_2/self.w_1
		self.DeHaller_stator=self.c_3/self.c_2

		delta_w_u=abs(self.w_u1-self.w_u2)
		delta_c_u=abs(self.c_u2-self.c_u3)
		
		self.pitch_ratio_rotor=2.0*self.w_1*(self.diffusion_rotor-1.0+(self.w_2/self.w_1))/delta_w_u # Teilungsverhaeltnis t/s ueber Diffusionszahl, umsgestellte Gl. 8.60, ACHTUNG: Nur gueltig bis zu einer lokalen Machzahl von 0.7!!
		self.pitch_ratio_stator=2.0*self.c_2*(self.diffusion_stator-1.0+(self.c_3/self.c_2))/delta_c_u # Teilungsverhaeltnis t/s ueber Diffusionszahl, umsgestellte Gl. 8.60, ACHTUNG: Nur gueltig bis zu einer lokalen Machzahl von 0.7!!		
		


		#Berechnung der Sehnenlaenge mittels eines vorzugebenden b/s-Verhaeltnisses im Rotor
		self.s_rotor=self.b_2/self.b_to_s_rotor
		self.z_calc_rotor=2.0*self.r_m2*numpy.pi/(self.pitch_ratio_rotor*self.s_rotor)			
		
		#print self.DeHaller_rotor,self.pitch_ratio_rotor,self.w_1,self.w_2,delta_w_u,self.s_rotor,self.z_calc_rotor
		
		#Berechnung der Sehnenlaenge mittels eines vorzugebenden b/s-Verhaeltnisses im Stator
		self.s_stator=self.b_3/self.b_to_s_stator
		self.z_calc_stator=2.0*self.r_m2*numpy.pi/(self.pitch_ratio_stator*self.s_stator)
		
		
		#Bestimmung von ganzzahligen Schaufelzahlen als Primzahlen
		def calcBladeNumbers(z_calculated):
			upper_border = int(z_calculated)*2
			x = range(upper_border)
			for i in range (0,upper_border):
			    x[i] = i

			x[0] = -1
			x[1] = -1

			i = 2
			while x[i] * x[i] <= x[upper_border-1]:
				if x[i] != -1:
					for j in range (x[i] * x[i], x[upper_border-1], x[i]):
						x[j] = -1
				i = i + 1

			'''
			# Zur Kontrolle: Gibt die Gesamtliste mit geloeschten Eintraegen aus
			for i in range (0,upper_border):
				print i, x[i]
			'''

			def counter(a,b):
				count = 0
				for i in range (a,b):
					if x[i]!= -1:
						count=count + 1
				return count

			def create_primelists(a):
				prime_list=range(0,a)
				return prime_list

			def primelist (primelist_border, scanborder_low, scanborder_up):
				prime_list = range(0, primelist_border)
				listcounter=0
				for i in range (scanborder_low, scanborder_up):
					if x[i]!= -1:
						prime_list[listcounter] = x[i]
						listcounter=listcounter + 1
				return prime_list

			prime_counter_lower = counter(0, int(z_calculated))
			prime_counter_upper = counter(int(z_calculated), upper_border)

			prime_list_lower = primelist(prime_counter_lower, 0, int(z_calculated))
			prime_list_upper = primelist(prime_counter_upper, int(z_calculated), upper_border)

			'''
			# Zur Kontrolle: Gibt die beiden Primzahllisten aus
			for i in range (0, prime_counter_lower):
			  print "Untere Liste:", prime_list_lower[i]
			  
			for i in range (0, prime_counter_upper):
			  print "Obere Liste", prime_list_upper[i]
			
			# Zur Kontrolle: Gibt die beiden naechstgelegenen Primzahlen zu z_calculated aus
			print "Die naechste tiefer gelegene Primzahl zu", int(z_calculated),"ist", ma.maximum(prime_list_lower)
			print "Die naechste hoeher gelegene Primzahl zu", int(z_calculated),"ist", ma.minimum(prime_list_upper)
			'''
			return ma.minimum(prime_list_upper) #Es wird die naechst hoehere Primzahl gewaehlt
			
		
		self.z_chosen_stator = calcBladeNumbers(self.z_calc_stator)
		self.z_chosen_rotor = calcBladeNumbers(self.z_calc_rotor)
		'''# Zur Kontrolle
		print self.z_chosen_stator
		print self.z_chosen_rotor'''
		
		self.c_a_rotor,self.gamma_rotor,self.deviation_angle_rotor,self.pitch_ratio_recalc_rotor,self.gitterbelastung_rotor = self.calculateProfile(
			self.beta_1,
			self.beta_2,
			self.w_u1,
			self.w_u2,
			self.w_1,
			self.w_2,
			self.z_chosen_rotor,
			self.s_rotor,
			(self.r_m1+self.r_m2)/2.0 )
		
		self.c_a_stator,self.gamma_stator,self.deviation_angle_stator,self.pitch_ratio_recalc_stator,self.gitterbelastung_stator = self.calculateProfile(
			self.alpha_2,
			self.alpha_3,
			self.c_u2,
			self.c_u3,
			self.c_2,
			self.c_3,
			self.z_chosen_stator,
			self.s_stator,
			(self.r_m2+self.r_m3)/2.0 )
		
		#Erste Abschaetzung der aufgrund der Zentrifugalkraft am Schaufelfuss wirkenden Spannungen
		#Evtl waere es am besten eine eigene Funktion calcMechanic() hinzuzufuegen
		self.rho_rotormaterial=2700
		self.sigma_z_bladeroot=(self.rho_rotormaterial*((self.u_1+self.u_2)*0.5)**2.0*self.b_2/((self.r_m1+self.r_m2)/2.0))/(1000.0**2.0)		
		
		#Berechnung der z-Koordinate (wichtig für den Schaufelreihenabstand)
		#TODO Bisher nur Überschlagsmäßige Rechnung damit die Geometriegenerierung klappt
		self.z_2=self.z_1+self.s_rotor*1.0
		self.z_3=self.z_2+self.s_stator*1.0
		
		
	def addTabBladeDesign(self,widget):
		from PyQt4 import QtGui, QtCore
		import bladeDesignerThread
		bladeDesignWidget = QtGui.QWidget()
		thread = bladeDesignerThread.BladeDesignerThread()
		
		LENumCuts = QtGui.QLineEdit('5')
		CBNLawLay1 = QtGui.QComboBox()
		CBNLawLay1.insertItems(0,['Potentialwirbel -1','Festkoerperrotation +1'])
		CBNLawLay1.setCurrentIndex(1)
		CBNLawLay2 = QtGui.QComboBox()
		CBNLawLay2.insertItems(0,['Potentialwirbel -1','Festkoerperrotation +1'])
		CBNLawLay2.setCurrentIndex(0)
		CBNLawLay3 = QtGui.QComboBox()
		CBNLawLay3.insertItems(0,['Potentialwirbel -1','Festkoerperrotation +1'])
		CBNLawLay3.setCurrentIndex(1)
		
		vbox = QtGui.QVBoxLayout()
		calcBladeDesignButton = QtGui.QPushButton('Calculate Blade Design')
		callBladeDesignerButton = QtGui.QPushButton('Call external bladedesigner (takes several minutes!)')
		callBladeDesignerButton.setEnabled(0)
		
		def calcBladeDesignGUI():
			if widget.parentWidget().parentWidget().parentWidget().thermoDone == True and widget.parentWidget().parentWidget().parentWidget().aeroDone == True:
				GUIcuts = int(LENumCuts.text())
				GUIn_lay1 = int(CBNLawLay1.currentText()[-2:])
				GUIn_lay2 = int(CBNLawLay2.currentText()[-2:])
				GUIn_lay3 = int(CBNLawLay3.currentText()[-2:])
				self.calcBladeGeom(stage=1,cuts=GUIcuts,preStageObj=None,end=1,n_lay1=GUIn_lay1,n_lay2=GUIn_lay2,n_lay3=GUIn_lay3)
				callBladeDesignerButton.setEnabled(1)
				calcBladeDesignOutput()
			else:
				errMesg = QtGui.QMessageBox()
				errMesg.setText('Calculate aerodynamics and thermodynamics first!')
				errMesg.exec_()
			
		def calcBladeDesignOutput():
			outputDialog = QtGui.QDialog()
			outputDialog.setMinimumSize(1200,500)
			vboxDialog = QtGui.QVBoxLayout()
			TOutput = QtGui.QTextEdit()
			TOutput.append(self.returnStageInfo())
			TOutput.setReadOnly(True)
			acceptButton = QtGui.QPushButton('Close')
			outputDialog.connect(acceptButton, QtCore.SIGNAL('clicked()'), outputDialog.accept)
			
			vboxDialog.addWidget(TOutput)
			vboxDialog.addWidget(acceptButton)
			outputDialog.setLayout(vboxDialog)
			outputDialog.setModal(False)
			outputDialog.exec_()
			
		def callBladeDesigner():
			import bladeDesignerXML
			stagelist = [self]
			xml=bladeDesignerXML.BdXML(stagelist)
			xml.writeTurboMachineXML(self.identification)
			try:
				from bladedesigner import turboMachine
				import os

				compbd=turboMachine.turboMachine(os.path.abspath(self.identification))
				compbd.computeTurboMachine()
				compbd.displayViewer()
			except:
				print "Ein Fehler ist aufgetreten. Ist der BladeDesigner installiert und richtig importiert?"
			#stagelist = [self]
			#callBladeDesignerButton.setEnabled(0)
			#thread.startCalculating(stagelist,self.identification)
		
		def updateGUI():
			callBladeDesignerButton.setEnabled(1)

		bladeDesignWidget.connect(calcBladeDesignButton, QtCore.SIGNAL("clicked()"), calcBladeDesignGUI)
		bladeDesignWidget.connect(callBladeDesignerButton, QtCore.SIGNAL("clicked()"), callBladeDesigner)
		bladeDesignWidget.connect(thread, QtCore.SIGNAL("finished()"), updateGUI)
		bladeDesignWidget.connect(thread, QtCore.SIGNAL("terminated()"), updateGUI)

		
		vbox.addWidget(QtGui.QLabel('Enter number of cuts:'))
		vbox.addWidget(LENumCuts)
		vbox.addWidget(QtGui.QLabel('Choose n-law for the first layer:'))
		vbox.addWidget(CBNLawLay1)
		vbox.addWidget(QtGui.QLabel('Choose n-law for the second layer:'))
		vbox.addWidget(CBNLawLay2)
		vbox.addWidget(QtGui.QLabel('Choose n-law for the third layer:'))
		vbox.addWidget(CBNLawLay3)
		#vbox.addWidget
		vbox.addWidget(calcBladeDesignButton)
		vbox.addWidget(callBladeDesignerButton)
		bladeDesignWidget.setLayout(vbox)
		widget.addTab(bladeDesignWidget,"Blade Design")
	
	
	
	#===========================================================================
	# Berechnungsmethode fuer Drallverteilung ueber Schaufelhoehe
	#===========================================================================
	#Übergabeparameter:
	#cuts Anzahl der Profilschnitte
	#preStageObj Das Objekt der vorangegangenen Kompressorstufe (wenn vorhanden)
	#stage Die Stufennummer (bei 1 beginnend)
	#end Flag (0/1) obs die letzte Stufe ist
	#n_lay1/2/3 Exponent für die Verwindungsfunktion an der entsprechenden Schaufelebene (1=Festkörperrotation,-1=Potentialwirbel)
	def calcBladeGeom(self,cuts=5,preStageObj=None,end=1,n_lay1=1,n_lay2=-1,n_lay3=1):
		#Initialisiere
		#print cuts, preStageObj,stage,end,n_lay1,n_lay2,n_lay3
		self.numberCuts=cuts
		
		self.ArrayLayer1=zeros((self.numberCuts,13))
		self.ArrayLayer2=zeros((self.numberCuts,14))
		self.ArrayLayer3=zeros((self.numberCuts,13))
		
		self.r_vec_layer1=linspace(self.r_h1,self.r_s1,self.numberCuts)	#Lineare Aufteilung des Radius ueber Schaufelhoehe #TODO Flächengleiche Aufteilung der Radien ist schicker
		self.r_vec_layer2=linspace(self.r_h2,self.r_s2,self.numberCuts)	#Lineare Aufteilung des Radius ueber Schaufelhoehe
		self.r_vec_layer3=linspace(self.r_h3,self.r_s3,self.numberCuts)	#Lineare Aufteilung des Radius ueber Schaufelhoehe
		
		#Berechne
		if not preStageObj==None:
			self.prelayer2=preStageObj.ArrayLayer2
			self.pre_z=preStageObj.z_chosen_stator
			self.pre_s=preStageObj.s_stator
			stage=0
		else:
			stage=1
		self.calcBladeGeomLayer1(stage,n_lay1)
		if not preStageObj==None:
			preStageObj.ArrayLayer3=self.ArrayLayer1
		self.calcBladeGeomLayer2(n_lay2)
		if end==1:
			self.calcBladeGeomLayer3(n_lay3)

	
	def printStage(self):
		print self.returnStageInfo()
		
	def returnStageInfo(self):
		string = ''
		string += "\n=====================================================================================================\n"
		string += "Verwindung Ebene 1\n"
		string += "=====================================================================================================\n"
		string += "Radius\tC_1\tC_ax1\tC_u1\tAlpha_1\tW_1\tW_u1\tBeta_1\tUmlenkung\tDH\tca\tgamma\tDeviation\n"
		for i in range(self.numberCuts):
			string += "\n"
			for j in range(len(self.ArrayLayer1[0])): 
				string += "%.5f\t" %self.ArrayLayer1[i,j]
		string += "\n=====================================================================================================\n"
		string += "Verwindung Ebene 2\n"
		string += "=====================================================================================================\n"
		string += "Radius\tC_2\tC_ax2\tC_u2\tAlpha_2\tW_2\tW_ax2\tW_u2\tBeta2\tUmlenkung\tDH\tca\tgamma\tDeviation\n"
		for i in range(self.numberCuts):
			string += "\n"
			for j in range(len(self.ArrayLayer2[0])): 
				string += "%.5f\t" %self.ArrayLayer2[i,j]
		string += "\n=====================================================================================================\n"
		string += "Verwindung Ebene 3\n"
		string += "=====================================================================================================\n"
		string += "Radius\tC_1\tC_ax1\tC_u1\tAlpha_3\tW_1\tW_u1\tBeta_1\tUmlenkung\tDH\tca\tgamma\tDeviation\n"
		for i in range(self.numberCuts):
			string += "\n"
			for j in range(len(self.ArrayLayer3[0])): 
				string += "%.5f\t" %self.ArrayLayer3[i,j]
		
		return string
		
	def calcBladeGeomLayer1(self,stage,n_law):
		self.u_m=self.u_1
		self.r_m=self.r_m1 
		def fkt_u_1(i):
			u_1=self.omega*self.r_vec_layer1[i]
			return u_1
		def fkt_w_u1(i):
			w_u1=fkt_c_u1(i)-fkt_u_1(i)
			return w_u1
		def fkt_w_1(i):
			w_1=numpy.sqrt(fkt_c_ax1(i)**2+(fkt_w_u1(i))**2)
			return w_1
		def fkt_beta_1(i):
			beta_1=numpy.degrees(numpy.arccos(fkt_w_u1(i)/numpy.sqrt(fkt_c_ax1(i)**2+(fkt_w_u1(i))**2)))
			return beta_1
		
		
		
		if stage==1:
			for i in range (0, self.numberCuts, 1):
				self.ArrayLayer1[i,0]=self.r_vec_layer1[i]   		   									#Berechnung des Radius     
				self.ArrayLayer1[i,1]=self.c_1			   												#Berechnung von C_1      
				self.ArrayLayer1[i,2]=self.c_ax1 		           										#Berechnung C_ax1        
				self.ArrayLayer1[i,3]=self.c_u1       		   											#Berechnung C_u1
				self.ArrayLayer1[i,4]=self.alpha_1					               						#Berechnung Alpha_1
				self.ArrayLayer1[i,5]=numpy.sqrt(self.c_ax1**2+(self.c_u1-fkt_u_1(i))**2)  			   	#Berechnung W_1    
				self.ArrayLayer1[i,6]=self.c_u1-fkt_u_1(i) 		           								#Berechnung von W_u1
				self.ArrayLayer1[i,7]=numpy.degrees(numpy.arccos((self.c_u1-fkt_u_1(i))/numpy.sqrt(self.c_ax1**2+(self.c_u1-fkt_u_1(i))**2)))	           	#Berechnung Beta_1

		else:
			if n_law==-1:
				def fkt_c_u1(i):
					c_u1=(self.c_u1*self.r_m)/self.r_vec_layer1[i]
					return c_u1
				def fkt_c_ax1(i):
					c_ax1=fkt_c_u1(i)*numpy.tan(numpy.radians(fkt_alpha_1(i)))
					return c_ax1
				def fkt_c_1(i):
					c_1=fkt_c_u1(i)/numpy.cos(numpy.radians(fkt_alpha_1(i)))
					return c_1
				def fkt_alpha_1(i):
					alpha_1=numpy.degrees(numpy.arctan(numpy.tan(numpy.radians(self.alpha_1))*self.r_vec_layer1[i]/self.r_m))
					return alpha_1

			if n_law==1:
				def fkt_c_u1(i):
					c_u1=self.c_u1/self.r_m*self.r_vec_layer1[i]
					return c_u1
				def fkt_c_ax1(i):
					c_ax1=numpy.sqrt(self.c_ax1**2-2*(fkt_c_u1(i)**2-self.c_u1**2))
					return c_ax1
				def fkt_c_1(i):
					c_1=numpy.sqrt(fkt_c_ax1(i)**2+fkt_c_u1(i)**2)
					return c_1
				def fkt_alpha_1(i):
					alpha_1=numpy.degrees(numpy.arccos(fkt_c_u1(i)/fkt_c_1(i)))
					return alpha_1
		
					
			for i in range (0, self.numberCuts, 1):
				self.ArrayLayer1[i,0]=self.r_vec_layer1[i]   		   	#Berechnung des Radius     
				self.ArrayLayer1[i,1]=fkt_c_1(i)			   	#Berechnung von C_1      
				self.ArrayLayer1[i,2]=fkt_c_ax1(i) 		           	#Berechnung C_ax1        
				self.ArrayLayer1[i,3]=fkt_c_u1(i)       		   	#Berechnung C_u1
				self.ArrayLayer1[i,4]=fkt_alpha_1(i)                        	#Berechnung Alpha_1
				self.ArrayLayer1[i,5]=fkt_w_1(i)  			   	#Berechnung W_1    
				self.ArrayLayer1[i,6]=fkt_w_u1(i) 		           	#Berechnung von W_u1
				self.ArrayLayer1[i,7]=fkt_beta_1(i)		           	#Berechnung Beta_1
				self.ArrayLayer1[i,8]=fkt_alpha_1(i)-self.prelayer2[i,4]   		   	#Berechnung Umlenkung Stator     
				self.ArrayLayer1[i,9]=fkt_c_1(i)/self.prelayer2[i,1]
				#ca,gamma,deviation,pitch_ratio,gitterbelastung
				#alpha1,alpha2,cu1,cu2,c1,c2,nblades,s,r
				#print self.prelayer2[i]
				#print self.ArrayLayer1[i]
				self.ArrayLayer1[i,10],self.ArrayLayer1[i,11],self.ArrayLayer1[i,12],pitchr,gitterb = self.calculateProfile(
					self.prelayer2[i,4],
					self.ArrayLayer1[i,4],
					self.prelayer2[i,3],
					self.ArrayLayer1[i,3],
					self.prelayer2[i,1],
					self.ArrayLayer1[i,1],
					self.pre_z,
					self.pre_s,
					self.ArrayLayer1[i,0]   )



	def calcBladeGeomLayer2(self,n_law):
		self.u_m=self.u_2
		self.r_m=self.r_m2

		#FUNKTIONEN ZUR BERECHNUNG DER EINZELNEN KOMPONENTEN
		
		def fkt_u_2(i):
			u_2=self.omega*self.r_vec_layer2[i]
			return u_2
		def fkt_w_u2(i):
			w_u2=fkt_c_u2(i)-fkt_u_2(i)
			return w_u2
		def fkt_w_2(i):
			w_2=numpy.sqrt((fkt_c_ax2(i))**2+(fkt_w_u2(i))**2)
			return w_2
		def fkt_beta_2(i):
			beta_2=numpy.degrees(numpy.arccos(fkt_w_u2(i)/fkt_w_2(i)))
			return beta_2
		def fkt_check_DH_rotor(i):
			DH_rotor=fkt_w_2(i)/self.ArrayLayer1[i,5]
			return DH_rotor
		def fkt_check_deviation_rotor(i):
			deviation_rotor=fkt_beta_2(i)-self.ArrayLayer1[i,7]
			return deviation_rotor

		if n_law==-1:
			def fkt_c_u2(i):
				c_u2=(self.c_u2*self.r_m)/self.r_vec_layer2[i]
				return c_u2
			def fkt_c_ax2(i):
				c_ax2=fkt_c_u2(i)*numpy.tan(numpy.radians(fkt_alpha_2(i)))
				return c_ax2
			def fkt_c_2(i):
				c_2=fkt_c_u2(i)/numpy.cos(numpy.radians(fkt_alpha_2(i)))
				return c_2
			def fkt_alpha_2(i):
				alpha_2=numpy.degrees(numpy.arctan(numpy.tan(numpy.radians(self.alpha_2))*self.r_vec_layer2[i]/self.r_m))
				return alpha_2

		if n_law==1:
			def fkt_c_u2(i):
				c_u2=self.c_u2/self.r_m*self.r_vec_layer2[i]
				return c_u2
			def fkt_c_ax2(i):
				c_ax2=numpy.sqrt(self.c_ax2**2-2*(fkt_c_u2(i)**2-self.c_u2**2))
				return c_ax2
			def fkt_c_2(i):
				c_2=numpy.sqrt(fkt_c_ax2(i)**2+fkt_c_u2(i)**2)
				return c_2
			def fkt_alpha_2(i):
				alpha_2=numpy.degrees(numpy.arccos(fkt_c_u2(i)/fkt_c_2(i)))
				return alpha_2

				
		for i in range(self.numberCuts):
			self.ArrayLayer2[i,0]=self.r_vec_layer2[i]   		   	#Berechnung des Radius     
			self.ArrayLayer2[i,1]=fkt_c_2(i)			   	#Berechnung von C_2      
			self.ArrayLayer2[i,2]=fkt_c_ax2(i) 		        #Berechnung C_ax2        
			self.ArrayLayer2[i,3]=fkt_c_u2(i)       		   	#Berechnung C_u2
			self.ArrayLayer2[i,4]=fkt_alpha_2(i)                        #Berechnung Alpha_2
			self.ArrayLayer2[i,5]=fkt_w_2(i)  			   	#Berechnung W_2    
			self.ArrayLayer2[i,6]=fkt_c_ax2(i) 			#Berechnung W_ax2=C_ax2     
			self.ArrayLayer2[i,7]=fkt_w_u2(i) 		           	#Berechnung von W_u2
			self.ArrayLayer2[i,8]=fkt_beta_2(i)    		   	#Berechnung von Beta_2
			self.ArrayLayer2[i,9]=fkt_check_deviation_rotor(i)	#Berechnung der Umlenkung im Rotor
			self.ArrayLayer2[i,10]=fkt_check_DH_rotor(i)	  	#Berechnung DH im Rotor
			#ca,gamma,deviation,pitch_ratio,gitterbelastung
			#alpha1,alpha2,cu1,cu2,c1,c2,nblades,s,r
			self.ArrayLayer2[i,11],self.ArrayLayer2[i,12],self.ArrayLayer2[i,13],pitchr,gitterb = self.calculateProfile(
				self.ArrayLayer1[i,7],
				self.ArrayLayer2[i,8],
				self.ArrayLayer1[i,6],
				self.ArrayLayer2[i,7],
				self.ArrayLayer1[i,5],
				self.ArrayLayer2[i,5],
				self.z_chosen_rotor,
				self.s_rotor,
				self.ArrayLayer2[i,0] )
			#print dev,pitchr,gitterb
			
			
	def calcBladeGeomLayer3(self,n_law):
		DeHaller_stator=0.7					#Vorgabe eines DH-Kriteriums um Statorauslegung auf verschiedenen Schaufelschnitten zu ermoeglichen
		self.c_2_vec=zeros((self.numberCuts,1))				
		for i in range (0, self.numberCuts, 1):
			self.c_2_vec[i,0]=self.ArrayLayer2[i,1]			   	#Berechnung von C_2  	
		c_ax3=self.c_ax3
		c_3=max(self.c_2_vec)*DeHaller_stator
		def fkt_check_deviation_stator(i):
			deviation_stator=fkt_alpha_3(i)-self.ArrayLayer2[i,4]
			return deviation_stator
		def fkt_check_DH_stator(i):
			DH_stator=fkt_c_3(i)/self.ArrayLayer2[i,1]
			return DH_stator
		if c_3<=self.c_3: 
			def fkt_c_3(i):
				c_3=self.c_3
				return c_3
			def fkt_alpha_3(i):
				alpha_3=self.alpha_3
				return alpha_3
			def fkt_c_u3(i):
				c_u3=self.c_u3
				return c_u3
			def fkt_c_ax3(i):
				c_ax3=self.c_ax3
				return c_ax3

		if c_3>c_ax3:

			if n_law==-1:
				def fkt_c_u3(i):
					c_u3=(self.c_u3*self.r_m)/self.r_vec_layer3[i]
					return c_u3
				def fkt_c_ax3(i):
					c_ax3=numpy.sqrt(fkt_c_3(i)**2-fkt_c_u3(i)**2)
					return c_ax3
				def fkt_c_3(i):
					c_3=fkt_c_u3(i)/numpy.cos(numpy.radians(fkt_alpha_3(i)))
					return c_3
				def fkt_alpha_3(i):
					alpha_3=numpy.degrees(numpy.arctan(numpy.tan(numpy.radians(self.alpha_3))*self.r_vec_layer3[i]/self.r_m))
					return alpha_3

			if n_law==1:
				def fkt_c_u3(i):
					c_u3=self.c_u3/self.r_m*self.r_vec_layer3[i]
					return c_u3
				def fkt_c_ax3(i):
					c_ax3=numpy.sqrt(self.c_ax3**2-2*(fkt_c_u3(i)**2-self.c_u3**2))
					return c_ax3
				def fkt_c_3(i):
					c_3=numpy.sqrt(fkt_c_ax3(i)**2+fkt_c_u3(i)**2)
					return c_3
				def fkt_alpha_3(i):
					alpha_3=numpy.degrees(numpy.arccos(fkt_c_u3(i)/fkt_c_3(i)))
					return alpha_3


		
		#print "\n\n\n=====Berechne Layer 3 Ende\n\n\n"
		for i in range (0, self.numberCuts, 1):
			self.ArrayLayer3[i,0]=self.r_vec_layer3[i]	   			#Berechnung C_ax3
			self.ArrayLayer3[i,1]=fkt_c_3(i)	  	   		#Berechnung C_3
			self.ArrayLayer3[i,2]=fkt_c_ax3(i)	   			#Berechnung C_ax3
			self.ArrayLayer3[i,3]=fkt_c_u3(i)	   			#Berechnung C_u3
			self.ArrayLayer3[i,4]=fkt_alpha_3(i)	  	   	#Berechnung Alpha_3
			self.ArrayLayer3[i,8]=fkt_check_deviation_stator(i)	#Berechnung der Umlenkung im Stator
			self.ArrayLayer3[i,9]=fkt_check_DH_stator(i)	  	#Berechnung DH im Stator
			#alpha1,alpha2,cu1,cu2,c1,c2,nblades,s,r
			self.ArrayLayer3[i,10],self.ArrayLayer3[i,11],self.ArrayLayer3[i,12],pitchr,gitterb = self.calculateProfile(
				self.ArrayLayer2[i,4],
				self.ArrayLayer3[i,4],
				self.ArrayLayer2[i,3],
				self.ArrayLayer3[i,3],
				self.ArrayLayer2[i,1],
				self.ArrayLayer3[i,1],
				self.z_chosen_rotor,
				self.s_rotor,
				self.ArrayLayer3[i,0]   )
			#print dev,pitchr,gitterb
			
			
	def calculateProfile(self,alpha1,alpha2,cu1,cu2,c1,c2,nblades,s,r): #relative schaufelwinkel!
		#print alpha1,alpha2,cu1,cu2,c1,c2,nblades,s,r
		delta_c_u=abs(cu1-cu2)
		c_inf=(c1+c2)/2.0

		#Zur Ueberpruefung wird noch die Gitterbelastungszahl berechnet welche im Bereich von ca. 0.4 bis 2.5 liegen sollte:
		gitterbelastung=2.0*delta_c_u/c_inf
		
		#Berechnung der wahren t/s Verhaeltnisse mit den gewaehlten Prim-Schaufelzahlen
		pitch_ratio_recalc=2.0*numpy.pi*r/(nblades*s)
		
		#Minderumlenkung! > NACA 6510
		deviation_angle=(0.23*((2.0*0.5)**2)+0.1*(alpha2/50.))*(alpha1-alpha2)*(numpy.sqrt(pitch_ratio_recalc))
		gamma=(alpha1/2.0)+((alpha2-deviation_angle)/2.0)-90.0
		
		#Zur Ueberpruefung wird noch der sich aus Gitterbelastungszahl und Teilungsverhaeltnis ergebende Auftriebsbeiwert berechnet
		c_a=gitterbelastung*pitch_ratio_recalc
		
		return c_a,gamma,deviation_angle,pitch_ratio_recalc,gitterbelastung


	#Diese Funktion wird aus der BdXML Klasse aufgerufen und bekommt von dort das dom-xml-objekt. Außerdem wird die Stufennummer (bei 0 beginnend) übergeben.
	def writeXML(self,dom_object,stagenumber=0,z=0):
		#Definiere Hilffunktion
		def createElement(dom_o,elementtype,elementobj,name,value):
			newElement = dom_o.createElement(elementtype)
			newElement.setAttribute(name,value)
			elementobj.appendChild(newElement)
		
		
		#Springe zum turboMachine Element
		elementTurb = dom_object.getElementsByTagName("turboMachine")[0]
		
		for n,rtype in enumerate(["rotor","stator"]):
			#Erzeuge ein neues bladeRow Element
			newElement = dom_object.createElement("bladeRow")
			newElement.setAttribute("i",str(n+stagenumber*2))
			elementTurb.appendChild(newElement)
			#Springe zum neuen Element
			elementRow = elementTurb.getElementsByTagName("bladeRow")[n+stagenumber*2]
			
			#Bereite einige Parameter vor, je nach Rotor/Stator #TODO auslagern in externe Funktion
			if rtype=="rotor":
				nblades=self.z_chosen_rotor
				r_h1=self.r_h1*1000.0
				r_h2=self.r_h2*1000.0
				r_s1=self.r_s1*1000.0
				r_s2=self.r_s2*1000.0
				z_1=self.z_1*1000.0
				z_2=self.z_2*1000.0
				omega=self.n/30.0*numpy.pi
				span=numpy.zeros((len(self.ArrayLayer2)))
				for i,p in enumerate(span):
					span[i]=(self.ArrayLayer2[i][0]-self.ArrayLayer2[0][0])/(self.ArrayLayer2[-1][0]-self.ArrayLayer2[0][0])
			else:
				nblades=self.z_chosen_stator
				r_h1=self.r_h2*1000.0
				r_h2=self.r_h3*1000.0
				r_s1=self.r_s2*1000.0
				r_s2=self.r_s3*1000.0
				z_1=self.z_2*1000.0
				z_2=self.z_3*1000.0
				omega=0.0
				span=numpy.zeros((len(self.ArrayLayer3)))
				for i,p in enumerate(span):
					span[i]=(self.ArrayLayer3[i][0]-self.ArrayLayer3[0][0])/(self.ArrayLayer3[-1][0]-self.ArrayLayer3[0][0])
			
			#coordinatesHub / Shroud
			coordinatesHub = zeros((5,2))
			coordinatesShroud = zeros((5,2))
			
			coordinatesHub[:,0]=linspace(z_1,z_2,5)
			coordinatesHub[:,1]=linspace(r_h1,r_h2,5)
			coordinatesShroud[:,0]=linspace(z_1,z_2,5)
			coordinatesShroud[:,1]=linspace(r_s1,r_s2,5)
			
			coordinatesStackingLine = zeros((5,2))
			coordinatesStackingLine[:,0]=(z_2-z_1)/2.5+z_1
			coordinatesStackingLine[:,1]=linspace(r_h1,r_s1,5)
			
			## Schreibe bladeRow-Parameter
			
			createElement(dom_object,"rowElement",elementRow,"definition","0")
	
			createElement(dom_object,"rowElement",elementRow,"angleFlag","1")

			createElement(dom_object,"rowElement",elementRow,"omega",str(omega))

			createElement(dom_object,"rowElement",elementRow,"numberBlades",str(nblades))

			createElement(dom_object,"rowElement",elementRow,"coordinatesHub",numpy.array2string(coordinatesHub,separator=","))

			createElement(dom_object,"rowElement",elementRow,"coordinatesShroud",numpy.array2string(coordinatesShroud,separator=","))
			
			createElement(dom_object,"rowElement",elementRow,"coordinatesStackingLine",numpy.array2string(coordinatesStackingLine,separator=","))
			
			#TODO: span (bladedesigner bug!!)
			createElement(dom_object,"rowElement",elementRow,"span",numpy.array2string(span,separator=","))
			
			
			for profilenum in range(len(self.ArrayLayer1)):
				#Erzeuge neues profile Element
				newElement = dom_object.createElement("profile")
				newElement.setAttribute("i",str(profilenum))
				elementRow.appendChild(newElement)
				#Springe zu diesem Element
				elementProfile = elementRow.getElementsByTagName("profile")[profilenum]
				
				#Bereite Parameter vor
				if rtype=="rotor":
					angle1=self.ArrayLayer1[profilenum][7]
					angle2=self.ArrayLayer2[profilenum][8]
					dev=self.ArrayLayer2[profilenum][13]
					s=self.s_rotor*1000.0 #TODO Nicht gleichzeitig mit Polynomialer Dickenverteilung nutzen!
					thick=0.14-profilenum*1.0/(len(self.ArrayLayer1)-1)*0.04
				else:
					angle1=self.ArrayLayer2[profilenum][4]
					angle2=self.ArrayLayer3[profilenum][4]
					dev=-self.ArrayLayer3[profilenum][9] #TODO Layer3
					s=self.s_stator*1000.0
					thick=0.1 #TODO Werte nicht erst hier berechnen!
				
				## Profildefinition: Berechne aus beta1 und beta2 die Profilbezogenen Winkel und den Staffelungswinkel
				theta=angle1-angle2+dev
				zeta1=90.0+theta/2.0
				zeta2=90.0-theta/2.0
				#Berechnung für Gamma gilt nur für symmetrische Skelettlinien!
				gamma=angle1-zeta1 #TODO Werte nicht erst hier berechnen!
				#poly=numpy.array([0.,0.09280047,0.1305026,-0.55961045,0.33630738,4.7,0.71143029,0.71323412,1.3]) #Polynom entspricht einer NACA6510 Dickenverteilung mit aufgedickter Hinterkante
				
				#Speichere Parameter ins dom_object
				
				createElement(dom_object,"profileElement",elementProfile,"flagCamberLine",str(0))
		
				createElement(dom_object,"profileElement",elementProfile,"flagThickDistr",str(1))
	
				createElement(dom_object,"profileElement",elementProfile,"profileResolution",str(200))

				createElement(dom_object,"profileElement",elementProfile,"chordLength",str(s))

				createElement(dom_object,"profileElement",elementProfile,"gamma",str(numpy.radians(gamma)))

				createElement(dom_object,"profileElement",elementProfile,"angleOfAttack",str(zeta1))

				createElement(dom_object,"profileElement",elementProfile,"outflowAngle",str(zeta2))

				createElement(dom_object,"profileElement",elementProfile,"maxIter",str(1000))
			
				createElement(dom_object,"profileElement",elementProfile,"error",str(1e-10))

				createElement(dom_object,"profileElement",elementProfile,"maxThickness",str(thick))

				createElement(dom_object,"profileElement",elementProfile,"weightCondition",str(5))

				createElement(dom_object,"profileElement",elementProfile,"weightCombination",str(2))
				
				##thickMeth
				#createElement(dom_object,"thickMeth",str(1))
				
				##polyThickRBs
				#createElement(dom_object,"polyThickRBs",numpy.array2string(poly,separator=","))
	



#===============================================================================
# Klasse zur Definition und Berechnung eines Radialverdichters
#===============================================================================
class CompressorRadial(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Radial Compressor'
		
		self.thermoInputParams=[["T_t1","K",""],\
								["p_t1","-","Total pressure inlet"],\
								["Pi","-",""],\
								["eta_pol","-",""],\
								["Ma_inlet","-","Approximate Mach number at inlet (0.4-0.6)"],\
								["Ma_outlet","-","Approximate Mach number at inlet (0.4-0.6)"],\
								["mflow","kg/s",""]]
		self.thermoOutputParams=[["T_t3","K",""],\
								["p_t3","-","Total pressure outlet"],\
								["deltaP","W","Power of the stage"]]
		
		self.aeroInputParams=[["p_t1","Pa",""],\
								["beta_2s","rad",""],\
								["alpha_2","rad",""],\
								["nblades","-",""],\
								["n_spec","-",""],\
								["c_1","m/s",""],\
								["c_ax1","m/s",""],\
								["c_u1","m/s",""],\
								["d_1h","m",""]]
		self.aeroOutputParams=[["epsilon","-",""],\
								["psi","-",""],\
								["Ma_U2","-",""],\
								["phi_2","-",""],\
								["p_1","Pa",""],\
								["rho_1","kg/m^2",""],\
								["n","1/min",""],\
								["d_1Goverd_2","",""],\
								["w_ax1s","m/s",""],\
								["w_u1s","m/s",""],\
								["w_1s","m/s",""],\
								["beta_1s","rad",""],\
								["u_1s","m/s",""],\
								["w_ax1h","m/s",""],\
								["w_u1h","m/s",""],\
								["w_1h","m/s",""],\
								["beta_1h","rad",""],\
								["u_2","m/s",""],\
								["w_r2","m/s",""],\
								["w_u2","m/s",""],\
								["w_2","m/s",""],\
								["c_r2","m/s",""],\
								["c_u2","m/s",""],\
								["c_2","m/s",""],\
								["c_3","m/s",""],\
								["beta_2","rad",""],\
								["d_2","m",""],\
								["b_2","",""],\
								["A_1","m^2",""],\
								["d_1s","m",""],\
								["verzoegerungsverhaeltnis_TF","-",""],\
								["verzoegerungsverhaeltnis","-",""],\
								["durchmesserverhaeltnis_TF","-",""],\
								["durchmesserverhaeltnis","-",""]]
		
		#self.modularSubfunctionList.append(self.addTabBladeDesign)
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#Defaults:
		self.Pi_Verlust_Stator=0.9
		self.phi_2=0.2
		self.kappa=1.4
		self.p_t1=101325
		self.Ma_inlet=0.5
		self.Ma_outlet=0.7
		
	def calcThermo(self):
		self.check(self.thermoInputParams)
		
		self.R=getR()
		
		self.p_t3=self.p_t1*self.Pi

		self.T_t3=polytrope(eta_pol=self.eta_pol,T1=self.T_t1,p1=self.p_t1,p2=self.p_t3,Ma=self.Ma_outlet)
		
		kappa_1=getKappa(Tt=self.T_t1,Ma=self.Ma_inlet)
		kappa_3=getKappa(Tt=self.T_t3,Ma=self.Ma_outlet)
		
		self.T_t2=self.T_t3	#Adiabates Leitrad
		
		self.deltaP=self.mflow*(kappa_3/(kappa_3-1.)*self.R*self.T_t3-kappa_1/(kappa_1-1.)*self.R*self.T_t1)

		#self.kappa=getKappa(Tt=((self.T_t3+self.T_t1)/2),Ma=self.Ma_inlet)
		self.kappa=(kappa_1+kappa_3)/2
		
		self.check(self.thermoOutputParams)
		

	def calcAero(self):
		self.check(self.aeroInputParams)
		
		self.c_p=self.kappa*self.R/(self.kappa-1.0)
		self.eta_pol=self.R/self.c_p*numpy.log(self.Pi)/numpy.log(self.T_t3/self.T_t1)
		self.calculateRadial()
		
		self.check(self.aeroOutputParams)
		
	#def addTabBladeDesign(self,widget):
		#bladeDesignWidget = QtGui.QWidget()
		#widget.addTab(bladeDesignWidget,"Blade Design")		
	
	def calculateRadial(self):
		self.iteratePhi2() # Aufruf der Iterationsschleife für Phi2 in der ebenfalls eine Iterationsschleife für beta_2 enthalten ist
		self.calcRadialAero()   # Berechnung aller fehlenden Winkel und Geschwindigkeiten die nicht durch die Funktion CalcBeta und CalcPhi_2 berechnet wurden
		self.Wislon_Cordalis() # Ueberpruefung des Verzoegerungsverhaeltnisses


	def calcEpsilon(self):
		self.epsilon=1.0-(1.0/(1.0+(self.nblades/numpy.pi)*((1.0+self.phi_2*(1.0/numpy.tan(self.beta_2)))/numpy.sin(self.beta_2))))
		# Berechnung von Epsilon, dem sog. Minderleistungskoeffizienten - Eingabewerte: beta_2 (Am Anfang den Schaufelwinkel, dann den Stroemungswinkel der bei der
		# Funktion calcBeta herauskommt) sowie Phi_2 (welches aus der Funktion CalcPhi2 herauskommt)
		# Zu Beginn muessen allerdings Anfangwerte getroffen werden: Dh. beta_2 ist vorerst der Schaufelwinkel beta_2s und Phi_2 ist erstmal eine Annahme
	
	
	def calcBeta(self):
		self.beta_2=numpy.pi-numpy.abs(numpy.arcsin((1.0-self.epsilon)*self.nblades/numpy.pi*(1.0+self.phi_2*1.0/numpy.tan(self.beta_2s))))
		# Berechnugn von beta_2 - Eingabewerte Epsilon, beta_2, Phi_2
	
	
	def iterateBeta(self):
		#print "IterateBeta"
		convergence=False
		tolerance=0.00001
		self.beta_2=self.beta_2s
		self.calcEpsilon()
		self.calcBeta()
		while convergence!=True:
			#print self.beta_2
			origBeta2=self.beta_2
			self.calcEpsilon()
			self.calcBeta()
			if numpy.abs(self.beta_2-origBeta2)<tolerance:
				break
		# Die Funktion Iterate Beta soll fogendes machen:
		# 1. Es wird Epsilon berechnet mit calcEpsilon - Ergebnis ist Epsilon
		# 2. Es wird mit dem eben berechneten Epsilon ein beta_2 berechnet, also den tatsaechlichen Stroemungswinkel
		# Mit der Abfrage self.beta_2-origBeta2<Tolerance wird geprüft wie Beta von dem vorher angenommenen Beta (im 1. Schritt der Schaufelwinkel) abweicht
		# Ist die Toleranze noch groeßer 0.00001 (Was sie beim ersten mal ganz sicher sein wird) wird mit dem eben errechneten beta_2 ein neues Epsilon berechnet
		# Mit dem neu brechneten Epsilon wird dann wieder ein beta_2 berechnet bis beta_2 die gewollte Toleranz aufweist
	
	
	def calcPhi2(self):
		#print "calcPhi2"
		self.T_t3=self.T_t1*self.Pi**(self.R/(self.eta_pol*self.c_p))
		self.deltaH_t=self.c_p*(self.T_t3-self.T_t1)
		self.psi=((1.0/self.epsilon)+(numpy.tan(self.beta_2s-numpy.pi/2.0))/(numpy.tan(numpy.pi/2.0-self.alpha_2)))**(-1.0) 
		self.u_2=numpy.sqrt(self.deltaH_t/self.psi)
		self.c_u2=self.psi*self.u_2
		self.c_r2=self.c_u2/numpy.tan(numpy.pi/2.0-self.alpha_2)
		self.phi_2=self.c_r2/self.u_2
		#print self.phi_2
		# In diesem Rechenschritt wird als wichtigste Groesse Psi berechnet - Psi halt als Eingangsgroessen nur Epsilon, den Schaufelwinkel beta_2s und Alpha 2
		# Im Anschluss daran wird U2 brechnet mit dem DeltaH_t was aus der Leistungsrechnung stammt - Hier fliesst der Polytrope Wikrkunsgrad ein
		# Hat man u_2 berechnet kann man hiermit Cu_2 berechnen und mit dem vorgegeben alpha_2 zusammen c_r2
		# Hieraus laesst sich ein neues phi_2 berechnen, welches nach Brauenlich mit c_r2/u_2 definiert ist
		# Da swohl in der Berechnung für beta_2 als auch für psi Epsilon auftaucht muss hier ebenfalls interiert werden bis das phi_2 sich nicht mehr aendert - Siehe IteratePhi2
	
	
	def calcRadialAero(self):
		self.w_r2theo=numpy.abs(self.c_r2*numpy.tan(self.beta_2s-numpy.pi/2.0))
		self.c_2=numpy.sqrt(self.c_r2**2.0+self.c_u2**2.0)
		self.w_2=numpy.sqrt(self.c_r2**2.0+(self.u_2-self.c_u2)**2.0)
		self.w_r2=self.w_2*numpy.cos(self.beta_2-numpy.pi/2.0)
		self.w_u2=numpy.sqrt(self.w_2**2.0-self.w_r2**2.0)
		self.T_2=self.T_t3-self.c_2**2.0/(2.0*self.R*self.kappa/(self.kappa-1.0))	#T_2 mit T_t3? verm. adiabat	
		self.a_2=numpy.sqrt(self.kappa*self.R*self.T_2)					
		self.Ma_U2=self.u_2/self.a_2
		self.T_1=self.T_t1-self.c_1**2.0/(2.0*self.R*self.kappa/(self.kappa-1.0))				
		self.p_t2=self.Pi*self.p_t1
		self.eta_pol=(self.kappa-1.0)/self.kappa*(numpy.log(self.p_t2/self.p_t1)/numpy.log(self.T_t3/self.T_t1))
		self.p_1=self.p_t1*(self.T_1/self.T_t1)**(self.kappa/(self.kappa-1.0))
		self.rho_1=self.p_1/(self.R*self.T_1)
		self.Vflow_1=self.mflow/self.rho_1
		self.omega=(self.n_spec*self.deltaH_t**0.75)/(numpy.sqrt(self.Vflow_1)) 
		# An dieser Stelle wird das erste mal die spezifische Drehzahl verwendet, mit der Omega bzw die Drehzahl berechnet wird
		# Ich denke die spezifische Drehzahl ist eine hilfreiche Groesse um die Drehzahl zu bestimmen da Bereiche bekannt sind in der sie sich bewegen sollte;
		# natuerlich waere es auch denkbar die Drehzahl vorzugeben und so die entsprechenden Geometrien auszurechnen. Ein ebenso gangbarer Weg.
		self.n=(self.omega*30.0)/numpy.pi
		self.d_2=(2.0*self.u_2)/self.omega
		self.p_2=self.p_t1*self.Pi*(self.T_2/self.T_t3)**(self.kappa/(self.kappa-1.0))
		self.b_2=self.mflow*self.R*self.T_2/(self.c_r2*self.p_2*self.d_2*numpy.pi)
		self.A_1=((self.deltaH_t**1.5)*self.n_spec**2.0)/(self.c_ax1*self.omega**2.0) # Entspricht exakt der der Formel dotm=rho*c_ax1*A_1; nur wird hier die spezifische Drehzahl herangezogen; Einsetzen der Definition von n_spec fuehrt auf die bekannte Formel
		self.d_1s=numpy.sqrt(4.0*self.A_1/numpy.pi+self.d_1h**2.0)
		self.d_1Goverd_2=self.d_1s/self.d_2
		self.u_1s=(self.d_1s*self.omega)/2.0
		self.u_1h=(self.d_1h*self.omega)/2.0
		self.w_ax1s=self.c_ax1
		self.w_u1s=self.u_1s-self.c_u1
		self.w_1s=numpy.sqrt(self.w_ax1s**2.0+self.w_u1s**2.0)
		self.beta_1s=(numpy.pi)-numpy.arctan(self.w_ax1s/self.w_u1s)
		self.w_ax1h=self.c_ax1
		self.w_u1h=self.u_1h-self.c_u1
		self.w_1h=numpy.sqrt(self.w_ax1h**2.0+self.w_u1h**2.0)
		self.beta_1h=(numpy.pi)-numpy.arctan(self.w_ax1h/self.w_u1h)
		self.p_t3=self.p_t2-self.Pi_Verlust_Stator*(self.p_t2-self.p_2)
		self.p_3=self.p_2+self.C_p23*(self.p_t2-self.p_2)
		self.T_3=self.T_t3*(self.p_3/self.p_t3)**((self.kappa-1.0)/self.kappa)
		self.c_3=numpy.sqrt(2.0*self.c_p*(self.T_t3-self.T_3))
		self.c_m3=numpy.sin(self.alpha_3)*self.c_3
		self.rho_3=self.p_3/(self.R*self.T_3)
		self.Ma_c3=self.c_3/(numpy.sqrt(self.kappa*self.R*self.T_3))
		self.A_3=self.mflow/(self.rho_3*self.c_m3)
		self.d_3=self.A_3/(numpy.pi*self.b_2)
		self.A_2=self.b_2*self.d_2*numpy.pi

		
	def Wislon_Cordalis(self):
		self.verzoegerungsverhaeltnis_TF=False
		self.durchmesserverhaeltnis_TF=False
		self.verzoegerungsverhaeltnis=(self.u_2/self.u_1s)*(numpy.cos(numpy.pi-self.beta_1s)/((1.0/numpy.tan(self.alpha_2)-1.0/numpy.tan(self.beta_2))*numpy.sin(self.beta_2)))
		self.durchmesserverhaeltnis=(1.0/0.8)*(numpy.cos(numpy.pi-self.beta_1s)/((1.0/numpy.tan(self.alpha_2)-1.0/numpy.tan(self.beta_2))*numpy.sin(self.beta_2)))
		if self.verzoegerungsverhaeltnis>0.8:
			self.verzoegerungsverhaeltnis_TF=True
		if self.durchmesserverhaeltnis>self.d_1Goverd_2:
			self.durchmesserverhaeltnis_TF=True
		# Ueberpruefung des Verzoegerungsverhaeltnisses nach Wilso und Cordalis
		
		
	def iteratePhi2(self):
		convergence=False
		tolerance=0.00001
		origphi_2=self.phi_2
		self.iterateBeta()
		self.calcPhi2()
		while convergence!=True:
			origphi_2=self.phi_2
			self.iterateBeta()
			self.calcPhi2()
			if numpy.abs(self.phi_2-origphi_2)<tolerance:
				break
		# Diese Funktion ist die erste die aufgerufen wird und beinhaltet sowohl calcPhi als auch iterateBeta
		#In der Schleife wird zuerst Beta iteriert, anschließend mit dem neuen beta_2 Phi_2 neu berechnet
		#Ist Phi zwei nicht in der entsprechenden Toleranz wird mit dem neuen Phi_2 wieder Beta iteriert (bis doch die gewuenschte Genauigkeit erreicht wurde;siehe IterateBeta)
		#Und anschliessend mit dem neuen beta_2 wieder Phi2 berechnet
		#Erst wenn Phi2 die gewuente Genauigkeit erreicht hat bricht die Schleife ab und CalcAero wird aufgerufen
	#Der mittlere Radius bestimmt sich aus der flaechengleichen Halbierung zwischen Nabe und Geh�use
		#self.r_m1=numpy.sqrt(((self.d_1h/2)**2.0+self.r_s1**2.0)/2.0)
