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
from helper_methods import *



#===============================================================================
# Klasse zur Definition und Berechnung einer Duese		
#===============================================================================
class Nozzle(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)
		
		self.type = 'Nozzle'
		
		self.thermoInputParams=[["T_t1","K","Stagnation temperature at layer 1 (nozzle-inlet)"],\
								["p_t1","Pa","Total (stagnation) pressure at layer 1 (nozzle-inlet)"],\
								["beta","-","Approximate fuel to air ratio (0.068)"],\
								["Pi","-","Total (stagnation) pressure ratio over nozzle (considering viscous losses)"]]
		self.thermoOutputParams=[["T_t3","K","Stagnation temperature at layer 3 (nozzle-outlet)"],\
								["R","J/(mol kg)","Specific gas constant of gas entering nozzle"],\
								["p_t3","Pa","Total (stagnation) pressure at layer 3 (nozzle-outlet)"]]

							
		
		# Achtung! Siehe Fragenliste!
		self.aeroInputParams=[["p_3","Pa","Static pressure at layer 3 (nozzle-outlet); For ideal expansion: Ambient static pressure "],\
								["eta_n","-","Nozzle efficiency"],\
								["mflow","kg/s","Mass flow"],\
								["kappa","-","Ratio of specific heats (kappa) of gas entering nozzle"],\
								["r_h3","m","Inner nozzle diameter (Hot nozzle: 0; Cold nozzle: r_s3 of hot nozzle"]]
		
		self.aeroOutputParams=[["c_3","m/s","Norm of absolute velocity at layer 3 (nozzle-outlet)"],\
								["T_3","K","Static temperature at layer 3 (nozzle-outlet)"],\
								["A_3","m^2","Area at layer 3 (nozzle-)outlet"],\
								["r_s3","m","Outer nozzle diameter"]]
		
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#Default Values
		self.kappa=1.3
		self.beta=0.0
		
	def calcThermo(self):
		self.check(self.thermoInputParams)
		
		self.R=getR(material="exhaust",beta=self.beta)
	    
	    #Total temperature outlet
		self.T_t3=self.T_t1 			#Annahme: Adiabate Duese, sowohl im ueberkritischen, im kritischen und unterkritischen Fall

		self.p_t3=self.Pi*self.p_t1	#Totaldruckverlust ueber die Duese
		
		self.check(self.thermoOutputParams)
	
		
	def calcAero(self):
		self.check(self.aeroInputParams)
		
		# Kritisches Druckverhaeltnis fuer isentrope Stroemung bei der im Austrittsquerschnitt A_3 der Duese gerade Schallgeschwindigkeit erreicht 			wird: c_3=a_3 => Ma_3=1		
		self.critPressRatio=((self.kappa+1.0)/2.0)**(self.kappa/(self.kappa-1.0)) #p_t1/p_crit9
		
		
		#Unterkritische Durchstroemung
		if self.p_t1/self.p_3<self.critPressRatio:
			#Braeunling Gl (13.23) S 1167 ACHTUNG: In Braeunling Gl. (13.23) wird mit dem Turbinenaustrittsdruck p_t5 gearbeitet und dieser mit 				Pi_connection reduziert 
			#(Hier muss ggf. nach gewaehlter Vorgehensweise (ob Zusammenfassung der Verlustfaktoren oder eigene Klasse fuer Zwischenstuecke etc 				korrigiert werden)
			self.T_3is=self.T_t3*((self.p_3/self.p_t3)**((self.kappa-1.0)/self.kappa))
			self.c_3is=numpy.sqrt((self.T_t3-self.T_3is)*2.0*self.R*self.kappa/(self.kappa-1.0))
			self.c_3=self.c_3is*(numpy.sqrt(self.eta_n))

			self.T_3=self.T_t3-((0.5*(self.c_3**2.0)/(self.kappa/(self.kappa-1.0)*self.R)))
			self.Ma_3=self.c_3/(numpy.sqrt(self.kappa*self.R*self.T_3))
			

		
		#Kritische bzw. ueberkritische Durchstroemung (Ma=1 im engsten Duesenquerschnitt)
		else:				
			self.Ma_3=1.0				
			#Gl 13.29	Kritische statische Temperatur im Duesenaustritt mittels Isentropenbeziehung ermittelt, Gl. 13.29 
			self.T_3=self.T_t3/(1.0+(self.kappa-1.0)*0.5) 
			#c_3 entspricht im kritischen Fall genau der Schallgeschwindigkeit
			self.c_3=self.Ma_3*numpy.sqrt(self.kappa*self.R*self.T_3) 
			#Braeunling Gl (13.23) S 1167 ACHTUNG: In Braeunling Gl. (13.23) wird mit dem Turbinenaustrittsdruck p_t5 gearbeitet und dieser mit 				Pi_connection reduziert 
			#(Hier muss ggf. nach gewaehlter Vorgehensweise (ob Zusammenfassung der Verlustfaktoren oder eigene Klasse fuer Zwischenstuecke etc 				korrigiert werden)
			
		
		# Berechnung der Duesenflaeche und des Duesenradiuses ausserhalb der Schleife
		self.A_3=self.mflow*numpy.sqrt(self.T_t3)/self.p_t3/self.Ma_3*numpy.sqrt(self.R/self.kappa)*((1.0+0.5*(self.kappa-1.0)*(self.Ma_3**2.0))**(0.5*(self.kappa+1.0)/(self.kappa-1.0)))	

		self.r_s3=numpy.sqrt((self.A_3/numpy.pi)+(self.r_h3**2.0)) #Annahme: Hotnozzle ist kreisfoermig => r_3h ist 0, Coldnozzle ist 			kreisringfoermig => self.cn.r_3h =self.hn.r_3s		
		
		self.check(self.aeroOutputParams)



