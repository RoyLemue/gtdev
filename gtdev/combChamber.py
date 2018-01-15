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
from gtdev.abstract import *
from gtdev.helper_methods import *
from scipy.optimize import fsolve


#===============================================================================
# Klasse zur Definition und Berechnung einer Brennkammer
#===============================================================================
class CombChamber(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)

		self.type = 'Combustion Chamber'
		
		self.thermoInputParams=[["H_f","J/kg",""],\
								["p_t1","-","Total pressure inlet"],\
								["T_t1","K","combustion chamber inlet temperature (total)"],\
								["T_t3","K","combustion chamber outlet temperature (total)"],\
								["Ma_inlet","-","Mach number at inlet (0.15-0.25)"],\
								["Ma_outlet","-","Mach number at outlet (0.35-0.45)"],\
								["Pi_Combc_fr","-","combustion chamber pressure loss"],\
								["eta_combc","-","combustion chamber efficiency"],\
								["mflow","kg/s",""]]
		self.thermoOutputParams=[["deltaP","W",""],\
								["p_t3","-","Total pressure outlet"],\
								["R_ex","J/(kgK)","Gas constant outlet"],\
								["beta","-","fuel to air ratio"],\
								["lambda_air","-","air to air_st ratio"],\
								["mflow_f","kg/s",""]]
		
		self.aeroInputParams=[["c_1","m/s",""],\
								["p_t1","Pa","Stagnation pressure at layer 1 (chamber inlet)"]]
		self.aeroOutputParams=[["c_3","m/s",""],\
								["Pi_Combc","-",""],\
								["p_t3","Pa","Stagnation pressure at layer 3 (chamber outlet)"],\
								["p_3","Pa","Static pressure at layer 3 (chamber outlet)"],\
								["Ma_1","-",""],\
								["Ma_3","-",""]]
		
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#Standardwerte:
		self.H_f=43100000.0 #J/kg
		self.kappa=1.4 #*
		self.Pi_Combc_fr=0.9 #Nach Braeunling fester Wert
		self.R=287.15
		self.Ma_inlet=0.2
		self.Ma_outlet=0.4
		self.p_t1=101325
		self.eta_combc=0.95
		
	
	def calcThermo(self):
		self.check(self.thermoInputParams)
		
		self.R=getR()
		
		#Isentropic exponent inlet
		self.kappa_1=getKappa(Tt=self.T_t1,Ma=self.Ma_inlet)
		
		#Totaltemperaturdifferenz:
		deltaT_t=self.T_t3-self.T_t1
		
		def iterate_fun(beta):
			kappa_3=getKappa(Tt=self.T_t3,Ma=self.Ma_outlet,material="exhaust",beta=beta)
			
			R_ex=8314.472*(0.034524+beta*0.035645)/(1+beta)
			
			#Zunahme der Enthalpie
			deltaP=self.mflow*(kappa_3/(kappa_3-1.)*R_ex*self.T_t3-self.kappa_1/(self.kappa_1-1.)*self.R*self.T_t1)
			
			#Brennstoffmassenstrom
			mflow_f=deltaP/(self.H_f*self.eta_combc)
			
			return beta-mflow_f/self.mflow
  
		self.beta=float(fsolve(iterate_fun,[0.034]))
		
		self.lambda_air=0.068/self.beta #kerosin only!
		
		#Isentropic exponent outlet
		self.kappa_3=getKappa(Tt=self.T_t3,Ma=self.Ma_outlet,material="exhaust",beta=self.beta)
		
		#Gas constant outlet 
		self.R_ex=8314.472*(0.034524+self.beta*0.035645)/(1+self.beta)

		#Heat insertion combustion chamber
		self.deltaP=self.mflow*(self.kappa_3/(self.kappa_3-1.)*self.R_ex*self.T_t3-self.kappa_1/(self.kappa_1-1.)*self.R*self.T_t1)
		
		#Massflow fuel
		self.mflow_f=self.deltaP/(self.H_f*self.eta_combc)
		
		#Total pressure outlet
		self.p_t3=self.p_t1*self.Pi_Combc_fr
		
		
		self.check(self.thermoOutputParams)


	def calcAero(self):
		self.check(self.aeroInputParams)
		
		T_1=self.T_t1-self.c_1**2.0/2.0/(self.R*self.kappa_1/(self.kappa_1-1.0))
		a_1=numpy.sqrt(self.kappa_1*self.R*T_1)
		self.Ma_1=self.c_1/a_1
		
		self.iterate_Ma_3()
		self.calcPi_Combc()
		
		T_3=self.T_t3*(1.0+(self.kappa_3-1.0)*0.5*(self.Ma_3**2.0))
		a_3=(self.kappa_3*self.R*T_3)**0.5
		self.c_3=self.Ma_3*a_3
		self.p_t3=self.p_t1*self.Pi_Combc
		self.p_3=self.p_t3/((1.0+((self.kappa_3-1.0)*0.5*(self.Ma_3**2.0)))**(self.kappa_3/(self.kappa_3-1.0)))		
		
		self.check(self.aeroOutputParams)
		
		
	def calcMa_3(self):
		self.Ma_3=self.Ma_1*((1.0+self.kappa_3*(self.Ma_3)**2.0)/(1.0+self.kappa_3*(self.Ma_1)**2.0))*numpy.sqrt((self.kappa_1*self.T_t3*(1.0+(self.kappa_1-1.0)/2.0*self.Ma_1**2.0))/(self.kappa_3*self.T_t1*(1.0+(self.kappa_3-1.0)/2.0*self.Ma_3**2.0)))
		
		
	def iterate_Ma_3(self):
		maxIter=100
		convergence=False
		tolerance=0.001
		self.Ma_3=self.Ma_1
		self.calcMa_3()
		for i in range(maxIter):
			origMa_3=self.Ma_3
			self.calcMa_3()
			if i==(maxIter-1):
                raise Exception("Max. Iteration exceeded -> Combustion Chamber. Try using different entry conditions!")
			if numpy.abs(self.Ma_3-origMa_3)<tolerance:
				break
	
	
	def calcPi_Combc(self):
		self.Pi_Combc_th=((1.0+self.kappa_1*self.Ma_1**2.0)*(1.0+(self.kappa_3-1.0)/2.0*self.Ma_3**2.0)**(self.kappa_3/(self.kappa_3-1.0)))/((1.0+self.kappa_3*self.Ma_3**2.0)*(1.0+(self.kappa_3-1.0)/2.0*self.Ma_1**2.0)**(self.kappa_1/(self.kappa_1-1.0)))
		self.Pi_Combc=self.Pi_Combc_th+self.Pi_Combc_fr-1.0
			
		
