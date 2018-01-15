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
# Klasse zur Definition und Berechnung einer Turbine			
#===============================================================================
class Turbine(AbstractTurbo):
	def __init__(self,ident_):
		#Inheritation of AbstractTurbo
		AbstractTurbo.__init__(self,ident_)

		self.type = 'Axial Turbine'

		self.thermoInputParams=[["deltaP","W","Change of stagnation enthalpy of overall turbine section"],\
								["Ma_inlet","-","Approximate Mach number at inlet (0.4-0.6)"],\
								["Ma_outlet","-","Approximate Mach number at outlet (0.4-0.6)"],\
								["mflow","kg/s","Hot mass flow"],\
								["beta","-","Approximate fuel to air ratio (0.068)"],\
								["eta_pol","-","Polytropic exponent turbine"],\
								["p_t1","-","Total pressure inlet"],\
								["T_t1","K","Stagnation temperature at layer 1 (turbine-inlet)"]]
		self.thermoOutputParams=[["T_t2","K","Stagnation temperature at layer 2 (between stator and rotor)"],\
								["kappa","-","Avg. Isentropic exponent in turbine"],\
								["p_t3","-","Total pressure outlet"],\
								["R","J/(mol kg)","Specific gas constant of gas entering nozzle"],\
								["T_t3","K","Stagnation temperature at layer 3 (turbine-outlet)"]]
		
		
		self.aeroInputParams=[["n","1/min","Rotational speed of respective shaft"],\
								["r","m","Radius of mid-span"],\
								["c_1","m/s","Absolute flow velocity at layer 1 (turbine-inlet)"],\
								["alpha_1","rad","Absolute flow angle at layer 1 (turbine-inlet) with respect to vertical direction"],\
								["p_t1","Pa","Stagnation pressure at layer 1 (turbine-inlet)"],\
								["Reaction","-","Degree of reaction of stages"],\
								["C_u_rotor","-","Kraftbeiwert rotor according to Zweifel"],\
								["C_u_stator","-","Kraftbeiwert stator according to Zweifel"],\
								["Pi_stator","-","Optional: Stagnation pressure ratio over stator (considering viscous losses)"],\
								["b_to_s_rotor","-","Ratio of blade length to chord length rotor"],\
								["b_to_s_stator","-","Ratio of blade length to chord length stator"]]
								
		self.aeroOutputParams=[["alpha_2","rad","Absolute flow angle at layer 2 (between stator and rotor) with respect to vertical direction"],\
								["alpha_3","rad","Absolute flow angle at layer 3 (turbine-outlet) with respect to vertical direction"],\
								["beta_2","rad","Relative flow angle at layer 2 (between stator and rotor) with respect to vertical direction"],\
								["beta_3","rad","Relative flow angle at layer 3 (turbine-outlet) with respect to vertical direction"],\
								["gamma_rotor","rad","Stagger angle rotor"],\
								["gamma_stator","rad","Stagger angle stator"],\
								["c_2","m/s","Norm of absolute velocity at layer 2 (between stator and rotor)"],\
								["w_2","m/s","Norm of relative velocity at layer 2 (between stator and rotor)"],\
								["c_3","m/s","Norm of absolute velocity at layer 3 (turbine-outlet)"],\
								["w_3","m/s","Norm of relative velocity at layer 3 (turbine-outlet)"],\
								["u","m/s","Circumferential speed at mid-span"],\
								["phi","-","Flownumber of turbine section (Durchflusskenngroesse)"],\
								["Psi","-","Enthalpynumber of turbine section"],\
								["pitch_ratio_rotor","-","Space-to-chord ratio t/s rotor"],\
								["pitch_ratio_stator","-","Space-to-chord ratio t/s stator"],\
								["p_t2","Pa","Stagnation pressure at layer 2 (between stator and rotor)"],\
								["p_t3","Pa","Stagnation pressure at layer 3 (turbine-outlet)"],\
								["p_2","Pa","Static pressure at layer 2 (between stator and rotor)"],\
								["p_3","Pa","Stagnation pressure at layer 3 (turbine-outlet)"],\
								["Ma_2","-","Machnumber at layer 2 (between stator and rotor)"],\
								["Ma_3","-","Machnumber at layer 3 (turbine-outlet)"],\
								["T_2","K","Static temperature at layer 2 (between stator and rotor)"],\
								["T_3","K","Static temperature at layer 3 (turbine-outlet)"],\
								["r_s1","m","Radius of shroud at layer 1 (turbine-inlet)"],\
								["r_s2","m","Radius of shroud at layer 2 (between stator and rotor)"],\
								["r_s3","m","Radius of shroud at layer 3 (turbine-inlet)"],\
								["r_h1","m","Radius of hub at layer 1 (turbine-inlet)"],\
								["r_h2","m","Radius of hub at layer 2 (between stator and rotor)"],\
								["r_h3","m","Radius of hub at layer 3 (turbine-inlet)"],\
								["b_1","m","Radial extension of layer 1 (turbine-inlet)"],\
								["b_2","m","Radial extension of layer 2 (between stator and rotor)"],\
								["b_3","m","Radial extension of layer 3 (turbine-inlet)"],\
								["s_rotor","m","Chord length of rotor"],\
								["s_stator","m","Chord length of stator"],\
								["z_calc_rotor","-", "Analytic number of rotor-blades (to be set to integer)"],\
								["z_calc_stator","-", "Analytic number of stator-blades (to be set to integer)"]] 			
		
		self.initialize(self.thermoInputParams)
		self.initialize(self.thermoOutputParams)
		self.initialize(self.aeroInputParams)
		self.initialize(self.aeroOutputParams)
		
		#Default Values
		self.T_t1=1000.0
		self.p_t1=101325
		self.C_u_rotor=1.1
		self.C_u_stator=0.8
		self.Reaction=0.25
		self.alpha_1=numpy.radians(90.0)
		self.R=287.15
		self.kappa=1.3
		self.Pi_stator=0.95
		self.b_to_s_rotor=2.5
		self.b_to_s_stator=2.0
		self.Ma_inlet=0.4
		self.Ma_outlet=0.4
		
	def calcThermo(self):
		self.check(self.thermoInputParams)
		
		self.R=getR(material="exhaust",beta=self.beta)
		
		kappa_1=getKappa(Tt=self.T_t1,Ma=self.Ma_inlet,material="exhaust",beta=self.beta)
		
		#Diese Iteration ist nötig um das kappa am Austritt entsprechend der Totaltemperatur am Austritt zu berechnen
		def iterate_fun(T_t3):
			kappa_3=getKappa(Tt=T_t3,Ma=self.Ma_outlet,material="exhaust",beta=self.beta)
			self.kappa=(kappa_1+kappa_3)/2.
			
			self.T_t3=self.T_t1-self.deltaP/self.mflow/self.R/self.kappa*(self.kappa-1)
			
			return T_t3-self.T_t3
		
		self.T_t3=float(fsolve(iterate_fun,[self.T_t1]))
		
		self.T_t2=self.T_t1	#Adiabates Leitrad
		
		self.p_t3=polytrope(eta_pol=self.eta_pol,T1=self.T_t1,T2=self.T_t3,p1=self.p_t1,Ma=self.Ma_outlet,material="exhaust",beta=self.beta)
		
		self.check(self.thermoOutputParams)
		
		
	def calcAero(self):
		self.check(self.aeroInputParams)
		


		#[-] Vorfaktoren fuer Staffelungswinkelberechnung, nur lokale konstanten Braeunling S 683 / S 684
		kA0=693.64794922	
		kA1=-10.7163448
		kA2=0.0441625752	
		kB0=-5.5007133484
		kB1=0.1052053347
		kB2=-0.0004236867
		kC0=-0.0076573845
		kC1=0.0000145823
		kC2=0.0000001621
		
		#Berechnung nach Bräunling
		self.u=self.n*numpy.pi*self.r/30.0	#[m/s] n muss in [1/min] uebergeben werden
		self.Psi=-1.0*((self.deltaP/self.mflow)/(self.u**2.0))	#[-] Enthalpiekenngroesse, Achtung: Muss bei Turbinen negativ sein um richtige Winkel nach der Auslegung von Braeunling zu erhalten!
		self.c_ax1=numpy.sin(self.alpha_1)*self.c_1	#[m/s] Meridionalkomponenten der Leitradzustroemung; alpha_0 Zustroemwinkel zur HDT, hier auf drallfreie Zustroemung gesetzt
		self.phi=self.c_ax1/self.u	#[-] Durchflusskenngroesse 
		# Berechnung der Winkel
		self.K_beta_2=self.phi/(self.Reaction+(self.Psi/2.0))	#[-] Faktor zur Winkelbestimmung Formel Braeunling 8.119
		self.K_beta_3=self.phi/(self.Reaction-(self.Psi/2.0))	#[-] Faktor zur Winkelbestimmung Formel Braeunling 8.120
		self.K_alpha_2=self.phi/(1.0-self.Reaction-(self.Psi/2.0))	#[-] Faktor zur Winkelbestimmung Formel Braeunling 8.121
		self.K_alpha_3=self.phi/(1.0-self.Reaction+(self.Psi/2.0))	#[-] Faktor zur Winkelbestimmung Formel Braeunling 8.122
		
		if self.K_beta_2>=0.0:	#[rad] Fallunterscheidung nach Braeunling S 647
			self.beta_2=numpy.pi-numpy.arctan(self.K_beta_2)
		else:
			self.beta_2=-numpy.arctan(self.K_beta_2)
		
		if self.K_beta_3>=0.0:
			self.beta_3=numpy.pi-numpy.arctan(self.K_beta_3)
		else:
			self.beta_3=-numpy.arctan(self.K_beta_3)
		
		if self.K_alpha_2>=0.0:
			self.alpha_2=numpy.arctan(self.K_alpha_2)
		else:
			self.alpha_2=numpy.pi+numpy.arctan(self.K_alpha_2)
		
		if self.K_alpha_3>=0.0:
			self.alpha_3=numpy.arctan(self.K_alpha_3)
		else:
			self.alpha_3=numpy.pi+numpy.arctan(self.K_alpha_3)
		
			
		#[rad] Staffelungswinkel Leitrad Gl 8.169 ACHTUNG: Hier wurde das Ergebnis von Gl 8.169 von 180 ° = Pi abgezogen, um den in Bild 8-71 Braeunling richtigen Bereich zu erreichen!
		self.gamma_stator=numpy.pi-(numpy.radians((kA0+kA1*(180.0-numpy.degrees(self.alpha_2))+kA2*((180.0-numpy.degrees(self.alpha_2))**2.0)) \
			       +((kB0+kB1*(180.0-numpy.degrees(self.alpha_2))+kB2*((180.0-numpy.degrees(self.alpha_2))**2.0))*numpy.degrees(self.alpha_1)) \
			       +((kC0+kC1*(180.0-numpy.degrees(self.alpha_2))+kC2*((180.0-numpy.degrees(self.alpha_2))**2.0))*(numpy.degrees(self.alpha_1)**2.0))))

		#[rad] Staffelungswinkel Laufrad Gl 8.168
		self.gamma_rotor=numpy.radians((kA0+kA1*numpy.degrees(self.beta_3)+kA2*numpy.degrees(self.beta_3)**2.0) \
			       +((kB0+kB1*numpy.degrees(self.beta_3)+kB2*numpy.degrees(self.beta_3)**2.0)*numpy.degrees(self.beta_2))\
			       +((kC0+kC1*numpy.degrees(self.beta_3)+kC2*numpy.degrees(self.beta_3)**2.0)*(numpy.degrees(self.beta_2)**2.0)))
		
								
		# Geschwindigkeiten Ebene 1 des Turbinengitters (Ebene 2 im Programm) 
		self.c_ax2=self.c_ax1	#Annahme: Axial- bzw. Meridionalgeschwindigkeit bleibt gleich	
		self.c_2=self.c_ax2/numpy.sin(self.alpha_2)	
		self.c_u2=self.c_ax2/numpy.tan(self.alpha_2)	#Berechnung von c_u2 ueber tan ergibt richtiges VZ mit der Winkelkonvention
		self.w_ax2=self.c_ax2	#Axial- bzw. Meridionalgeschwindigkeit unabhaenig vom Bezugssystem
		self.w_u2=self.c_u2-self.u 
		self.w_2=numpy.sqrt(self.w_u2**2.0+self.w_ax2**2.0)	#Berechnung von w ueber Pythagoras
		
		# Geschwindigkeiten Ebene 2 des Turbinengitters (im Programm Ebene 3)
		self.c_ax3=self.c_ax2	#Annahme: Axial- bzw. Meridionalgeschwindigkeit bleibt gleich	
		self.c_3=self.c_ax3/numpy.sin(self.alpha_3) 
		self.c_u3=self.c_ax3/numpy.tan(self.alpha_3)	#Berechnung von c_u3 ueber tan ergibt richtiges VZ mit der Winkelkonvention
		self.w_ax3=self.c_ax3	#Axial- bzw. Meridionalgeschwindigkeit unabhaenig vom Bezugssystem
		self.w_u3=self.c_u3-self.u 	
		self.w_3=numpy.sqrt(self.w_u3**2.0+self.w_ax3**2.0)	#Berechnung von w ueber Pythagoras
		

		#Statische Temperaturen 
		self.T_1=self.T_t1-(self.c_1**2.0)/(2.0*self.kappa*self.R/(self.kappa-1.0))	#Kontrollmgl. mit Machzahlfunktion der stat. Temperatur
		self.T_2=self.T_t2-(self.c_2**2.0)/(2.0*self.kappa*self.R/(self.kappa-1.0)) 
		self.T_3=self.T_t3-(self.c_3**2.0)/(2.0*self.kappa*self.R/(self.kappa-1.0))

		#Schallgeschwindigkeiten
		self.a_1=numpy.sqrt(self.kappa*self.R*self.T_1)
		self.a_2=numpy.sqrt(self.kappa*self.R*self.T_2)
		self.a_3=numpy.sqrt(self.kappa*self.R*self.T_3)
		
		#Machzahlen			
		self.Ma_1=self.c_1/self.a_1		
		self.Ma_2=self.c_2/self.a_2
		self.Ma_3=self.c_3/self.a_3
		#Ma_2w=self.w_2/self.a_2	#Machzahl mit Relativeschwindigkeit w_2 gebildet fuer p_t-Berechnung nach Braeunling Bsp. S. 649-652
		#Ma_3w=self.w_3/self.a_3	#Machzahl mit Relativeschwindigkeit w_3 gebildet fuer p_t-Berechnung nach Braeunling Bsp. S. 649-652
	
		#Totaldruecke (Berechnung nach Braeunling)
		'''self.p_t2=self.p_t1*self.Pi_stator	#Totaldruckverlust ueber Leitrad mit Schaetzwert fuer Pi_stator	
		p_t2rel=self.p_2*((1.0+(self.kappa-1)*0.5*Ma_2w**2.0)**(self.kappa/(self.kappa-1.0)))
		p_t3rel=p_t2rel*self.Pi_rotor
		self.p_t3=self.p_3*((1.0+(self.kappa-1)*0.5*self.Ma_3**2.0)**(self.kappa/(self.kappa-1.0)))'''
		
		#Totaldruecke (Berechnung nach eigenem Ermessen)
		self.p_t2=self.p_t1*self.Pi_stator	#Totaldruckverlust ueber Leitrad mit Schaetzwert fuer Pi_stator
		self.p_t3=self.p_t1*((self.T_t3/self.T_t1)**(self.kappa/(self.kappa-1.0)/self.eta_pol)) # siehe Doku			
		
		#Statische Druecke
		self.p_1=self.p_t1/((1.0+(self.kappa-1.0)*0.5*self.Ma_1**2.0)**(self.kappa/(self.kappa-1.0)))		
		self.p_2=self.p_t2/((1.0+(self.kappa-1.0)*0.5*self.Ma_2**2.0)**(self.kappa/(self.kappa-1.0)))
		self.p_3=self.p_t3/((1.0+(self.kappa-1.0)*0.5*self.Ma_3**2.0)**(self.kappa/(self.kappa-1.0)))

		#Dichte
		roh_1=self.p_1/(self.R*self.T_1)
		roh_2=self.p_2/(self.R*self.T_2)
		roh_3=self.p_3/(self.R*self.T_3)
		

		#Erforderliche Querschnittsflaechen um die entsprechende Meridionalgeschwindigkeit zu erreichen
		A_1=self.mflow/(roh_1*self.c_ax1)
		A_2=self.mflow/(roh_2*self.c_ax2) 
		A_3=self.mflow/(roh_3*self.c_ax3)  		
		
		#Gehaeuse- und Nabendurchmesser ueber den Mittenschnittsradius, der den Ringraum in zwei flaechengleiche Haelften teilt
		#Gehaeuseradien
		self.r_s1=numpy.sqrt((A_1/(2.0*numpy.pi))+(self.r**2.0))
 		self.r_s2=numpy.sqrt((A_2/(2.0*numpy.pi))+(self.r**2.0))
		self.r_s3=numpy.sqrt((A_3/(2.0*numpy.pi))+(self.r**2.0))	
		
		#Nabenradien
		self.r_h1=numpy.sqrt((self.r**2.0)-(A_1/(2.0*numpy.pi)))
 		self.r_h2=numpy.sqrt((self.r**2.0)-(A_2/(2.0*numpy.pi)))
		self.r_h3=numpy.sqrt((self.r**2.0)-(A_3/(2.0*numpy.pi)))

		#Ringraumhoehen b
		self.b_1=self.r_s1-self.r_h1
		self.b_2=self.r_s2-self.r_h2
		self.b_3=self.r_s3-self.r_h3		
		
		#Sehnenlaengen ueber ein vorgeschaetztes (bzw aus real existierenden Turbinen abgemessenes) Verhaeltnis b/s fuer Rotor und Stator
		self.s_rotor=self.b_2/self.b_to_s_rotor		#2 oder 3 oder Mittelwert aus beiden fuer Rotor?
		self.s_stator=self.b_1/self.b_to_s_stator	#1 oder 2 oder Mittelwert aus beiden fuer Stator?
		
		#Teilungsverhaeltnis (englisch divison ratio) Laufrad
		self.pitch_ratio_rotor=self.C_u_rotor*0.5*(numpy.sin(self.gamma_rotor))/((numpy.sin(self.beta_3)**2.0)*((1.0/numpy.tan(self.beta_2))-(1.0/numpy.tan(self.beta_3))))
		
		#Teilungsverhaeltnis (englisch divison ratio) Leitrad
		self.pitch_ratio_stator=self.C_u_stator*0.5*(numpy.sin(self.gamma_stator))/((numpy.sin(numpy.pi-self.alpha_2)**2.0)*((1.0/numpy.tan(self.alpha_1))-(1.0/numpy.tan(numpy.pi-self.alpha_2))))
		
		#Analytische Schaufelanzahl z_calc ueber Teilung t (ausgedrueckt ueber t/s und s), die natuerlich dann auf eine ganze Zahl (gerade fuer Rotor wg 			Auswuchten bei Schaufelaustausch, Primzahl fuer Stator wg Schwingungsanregung) geaendert werden muss	
		self.z_calc_rotor=(self.r*numpy.pi*2.0)/(self.pitch_ratio_rotor*self.s_rotor)
		self.z_calc_stator=(self.r*numpy.pi*2.0)/(self.pitch_ratio_stator*self.s_stator)		
		
		self.check(self.aeroOutputParams)

