#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) Hummingbird, Institute for Flight Propulsion
# Author: Sebastian Barthmes

import math

#Boundary Conditions
MFLOW=0.28
T_T1=293.15
STAGES=6
ETA=0.75
N=90000.
RHO=1.25
C_0=0.0
P_0=101325.0
R_H=0.015
R_S=0.03
PI_INTAKE=1.0
C_3TOC_1=1.0
#BTOSR=1.5
#BTOSS=1.5
DIFF_S=0.45
DIFF_R=0.4

#Initialize Objects
comp=[]
for n in range(STAGES):
	exec("comp.append(compressor.CompressorAxial('"+str(n)+"'))")
	comp[n].eta_is=ETA
	comp[n].mflow=MFLOW
	comp[n].n=N
	comp[n].c_3toc_1=C_3TOC_1	
	comp[n].diffusion_stator=DIFF_S
	comp[n].diffusion_rotor=DIFF_R
	comp[n].radius_const="casing"

#Setup Configuration
comp[0].reaction=0.70
comp[0].Pi=1.20
comp[0].b_to_s_rotor=1.2
comp[0].b_to_s_stator=1.7
comp[1].reaction=0.72
comp[1].Pi=1.19
comp[1].b_to_s_rotor=1.2
comp[1].b_to_s_stator=1.6
comp[2].reaction=0.72
comp[2].Pi=1.18
comp[2].b_to_s_rotor=1.15
comp[2].b_to_s_stator=1.5
comp[3].reaction=0.72
comp[3].Pi=1.17
comp[3].b_to_s_rotor=1.1
comp[3].b_to_s_stator=1.35
comp[4].reaction=0.72
comp[4].Pi=1.16
comp[4].b_to_s_rotor=1.0
comp[4].b_to_s_stator=1.2
comp[5].reaction=0.72
comp[5].Pi=1.15
comp[5].b_to_s_rotor=0.9
comp[5].b_to_s_stator=1.1


#Connect Components and Calculate
comp[0].T_t1=T_T1
comp[0].calcThermo()
comp[0].p_t1=P_0
comp[0].r_s1=R_S
comp[0].r_h1=R_H
comp[0].calcAero()
P=comp[0].deltaP
for n in range(1,STAGES):
	comp[n].T_t1=comp[n-1].T_t3
	comp[n].calcThermo()
	comp[n].r_s1=comp[n-1].r_s3
	comp[n].p_t1=comp[n-1].p_t3
	comp[n].r_h1=comp[n-1].r_h3
	comp[n].z_1=comp[n-1].z_3
	comp[n].calcAero()
	P+=comp[n].deltaP
	
#Calculate Blade Twist
comp[0].calcBladeGeom(cuts=5,end=0,n_lay1=1,n_lay2=-1)
comp[1].calcBladeGeom(cuts=5,preStageObj=comp[0],end=0,n_lay1=1,n_lay2=-1)
comp[2].calcBladeGeom(cuts=5,preStageObj=comp[1],end=0,n_lay1=1,n_lay2=-1)
comp[3].calcBladeGeom(cuts=5,preStageObj=comp[2],end=0,n_lay1=1,n_lay2=-1)
comp[4].calcBladeGeom(cuts=5,preStageObj=comp[3],end=0,n_lay1=1,n_lay2=-1)
comp[5].calcBladeGeom(cuts=5,preStageObj=comp[4],end=1,n_lay1=1,n_lay2=-1,n_lay3=1)


#Output
print "\nPi (ges):",comp[0].Pi*comp[1].Pi*comp[2].Pi*comp[3].Pi*comp[4].Pi*comp[5].Pi
print "deltaT_t:",comp[STAGES-1].T_t3-T_T1
print "P (ges):       ",P
for n in range(STAGES):
	comp[n].printEverything()
for n in range(STAGES):
	print "Stufe:",n+1
	comp[n].printStage()

#BladeDesigner Export und Aufruf
xml=bladeDesignerXML.BdXML(comp)
xml.writeTurboMachineXML("multistage")

#try:
	#from bladedesigner import *
	#import os

	#compbd=turboMachine.turboMachine(os.path.abspath("multistage"))
	#compbd.computeTurboMachine()
	#for n in range(len(compbd.listRows)):
		#compbd.listRows[n].exportBladeToSTEP("bladerow_"+str(n)+".stp")
	#compbd.displayViewer()
#except:
	#print "Ein Fehler ist aufgetreten. Ist der BladeDesigner installiert und richtig importiert?"
