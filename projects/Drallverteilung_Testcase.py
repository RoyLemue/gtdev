#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import scipy

from numpy import zeros
from numpy import *
multistage=compressor.CompressorAxial("Pre-Conception")

#Thermodynamische Randbedingungen

Stages=6.
T_t0=293.15 #K
p_t0=101325
Pi_intake=1.0 # -
Pi=1.14 # -/-
eta_is=0.75 # -/-
mflow=0.2 # kg/s
diffusion_rotor=0.5
diffusion_stator=0.5
b_to_s_rotor=1.0
b_to_s_stator=1.0
#Aerodynamische Randbedingungen
r_h1=0.012
r_s1=0.024
n=100000

#========================================================================================
print "\n==============================================================================="
print "Stufe 1"
print "===============================================================================\n"
#Thermodynamische Randbedingungen
multistage.p_t0=p_t0
multistage.T_t0=T_t0
multistage.Pi_intake=Pi_intake
multistage.Pi=Pi
multistage.eta_is=eta_is
multistage.mflow=0.2

#Aerodynamische Randbedingungen
multistage.r_h1=r_h1
multistage.r_s1=r_s1
multistage.n=n
multistage.alpha_3=numpy.radians(89)
multistage.reaction=0.7
multistage.diffusion_rotor=0.45
multistage.diffusion_stator=0.45
multistage.b_to_s_rotor=2.0
multistage.b_to_s_stator=2.0

multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()

#Layer, end, n-lr, n-st, drallfrei
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 1----Ebene 1" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,1)

print "\n==============================================================================="
print "Schaufelverwindung----Stufe 1----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,0,-1,1,0)
savetxt("Stage_1-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_1-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')		
#========================================================================================


#========================================================================================
print "\n==============================================================================="
print "Stufe 2"
print "===============================================================================\n"
#Randbedingungen-Input
multistage.p_t0=multistage.p_t3
multistage.T_t0=multistage.T_t3
multistage.Pi=Pi
multistage.reaction=0.7
multistage.r_h1=multistage.r_h3
multistage.r_s1=multistage.r_s3
multistage.alpha_1=multistage.alpha_3
multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 2----Ebene 1" 
print "\n===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,0)
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 2----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,0,-1,1,0)
savetxt("Stage_2-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_2-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')	
#========================================================================================


#========================================================================================
print "\n==============================================================================="
print "Stufe 3"
print "===============================================================================\n"
multistage.p_t0=multistage.p_t3
multistage.T_t0=multistage.T_t3
multistage.Pi=Pi
multistage.reaction=0.7
multistage.r_h1=multistage.r_h3
multistage.r_s1=multistage.r_s3
multistage.alpha_1=multistage.alpha_3
multistage.alpha_3=numpy.radians(89)
multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 3----Ebene 1" 
print "\n===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,0)
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 3----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,0,-1,1,0)
savetxt("Stage_3-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_3-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')	
#========================================================================================


#========================================================================================
print "\n==============================================================================="
print "Stufe 4"
print "===============================================================================\n"
multistage.p_t0=multistage.p_t3
multistage.T_t0=multistage.T_t3
multistage.Pi=Pi
multistage.reaction=0.7
multistage.r_h1=multistage.r_h3
multistage.r_s1=multistage.r_s3
multistage.alpha_1=multistage.alpha_3
multistage.alpha_3=numpy.radians(89)
multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 4----Ebene 1" 
print "\n===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,0)
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 4----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,0,-1,1,0)
savetxt("Stage_4-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_4-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')	
#========================================================================================


#========================================================================================
print "\n==============================================================================="
print "Stufe 5"
print "===============================================================================\n"
multistage.p_t0=multistage.p_t3
multistage.T_t0=multistage.T_t3
multistage.Pi=Pi
multistage.reaction=0.7
multistage.r_h1=multistage.r_h3
multistage.r_s1=multistage.r_s3
multistage.alpha_1=multistage.alpha_3
multistage.alpha_3=numpy.radians(89)
multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 5----Ebene 1" 
print "\n===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,0)
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 5----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,0,-1,1,0)
savetxt("Stage_5-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_5-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')	
#========================================================================================


#========================================================================================
print "\n==============================================================================="
print "Stufe 6"
print "===============================================================================\n"
multistage.p_t0=multistage.p_t3
multistage.T_t0=multistage.T_t3
multistage.Pi=Pi
multistage.reaction=0.7
multistage.r_h1=multistage.r_h3
multistage.r_s1=multistage.r_s3
multistage.alpha_1=multistage.alpha_3
multistage.alpha_3=numpy.radians(89)
multistage.calcThermo()
multistage.calcAero()
multistage.printEverything()
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 6----Ebene 1" 
print "\n===============================================================================\n"
multistage.calcSchaufelverwindung(1,0,1,1,0)
print "\n==============================================================================="
print "Schaufelverwindung----Stufe 6----Ebene 2" 
print "===============================================================================\n"
multistage.calcSchaufelverwindung(2,1,-1,1,0)
savetxt("Stage_6-Layer1.txt", multistage.FunctionValueArrayLayer1,fmt='%10.5f',delimiter='	')
savetxt("Stage_6-Layer2.txt", multistage.FunctionValueArrayLayer2,fmt='%10.5f',delimiter='	')	
#========================================================================================





