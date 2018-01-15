#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import scipy

from numpy import zeros
from numpy import *
stage_config=compressor.CompressorAxial("Pre-Conception")
#========================================================================================
#Funktion calcBladeGeom(self,cuts,output=1,stage=1,end=1,n_lay1=1,n_lay2=-1,n_lay3=1)
#Flags:	output=1 Ausgabe in Konsole output=0 Ausgabe in Konsole unterdrueckt
#		stage:	 Zuweisung der Stufennummer
#		end=1	Letzte Stufe eines mehrstufigen Verdichters oder einstufiger Verdichter
#		end=0	Mittlere Stufen eines mehrstufigen Verdichters
#		n_lay1=1 Starrkoerperwirbelgesetz in Ebene 1
#		n_lay1=-1 Potentialwirbelgesetz in Ebene 1
#		n_lay2=1 Starrkoerperwirbelgesetz in Ebene 2
#		n_lay2=-1 Potentialwirbelgesetz in Ebene 2
#		Zu n_lay3: Nur von Interesse wenn end=1
#		n_lay3=1 Starrkoerperwirbelgesetz in Ebene 3
#		n_lay3=-1 Potentialwirbelgesetz in Ebene 3
#		cord=1 Berechnung der Sehnenlaenge anhand einer empirischen Formel fuer NACA-65-10
#========================================================================================
#========================================================================================
def header(stage):
	print "\n==============================================================================="
	print "Stufe", stage, 
	print "===============================================================================\n"
#========================================================================================
#							AUSLEGUNGSRECHNUNG
#========================================================================================	
#Thermodynamische Randbedingungen
stages=6.
T_t0=293.15 #K
p_t0=101325
Pi_intake=1.0 # -
Pi=1.14 # -/-
eta_is=0.75 # -/-
mflow=0.2 # kg/s
diffusion_rotor=0.45
diffusion_stator=0.45
b_to_s_rotor=1.0
b_to_s_stator=1.0
#Aerodynamische Randbedingungen
r_h1=0.012
r_s1=0.024
n=100000

#========================================================================================
# Stufe 1 
#========================================================================================
#Thermodynamische Anfangsbedingungen
stage_config.p_t0=p_t0
stage_config.T_t0=T_t0
stage_config.Pi_intake=Pi_intake
stage_config.Pi=Pi
stage_config.eta_is=eta_is
stage_config.mflow=0.2

#Aerodynamische Anfangsbedingungen
stage_config.r_h1=r_h1
stage_config.r_s1=r_s1
stage_config.n=n
stage_config.alpha_3=numpy.radians(89)
stage_config.reaction=0.7
stage_config.diffusion_rotor=0.45
stage_config.diffusion_stator=0.45
stage_config.b_to_s_rotor=2.0
stage_config.b_to_s_stator=2.0

#Berechnug 1. Stufe
stage_config.calcThermo()
stage_config.calcAero()
stage_config.printEverything()
stage_config.calcBladeGeom(cuts=5, stage=1, end=0)
#========================================================================================

#========================================================================================
#Uebergabe der Werte an 2. Stufe
stage_config.Pi=Pi
stage_config.reaction=0.7
stage_config.p_t0=stage_config.p_t3
stage_config.T_t0=stage_config.T_t3
stage_config.r_h1=stage_config.r_h3
stage_config.r_s1=stage_config.r_s3
stage_config.alpha_1=stage_config.alpha_3

#Berechnung 2. Stufe
stage_config.calcThermo()
stage_config.calcAero()
stage_config.printEverything()
stage_config.calcBladeGeom(cuts=5, stage=2,end=1)

#========================================================================================
	
#========================================================================================
