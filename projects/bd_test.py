# -*- coding: utf-8 -*-
#Test BladeDesigner

import numpy
import scipy
from numpy import zeros
from numpy import *

singlestage=compressor.CompressorAxial("Pre-Conception")

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

#Thermodynamische Randbedingungen
singlestage.p_t0=p_t0
singlestage.T_t0=T_t0
singlestage.Pi_intake=Pi_intake
singlestage.Pi=Pi
singlestage.eta_is=eta_is
singlestage.mflow=mflow

#Aerodynamische Randbedingungen
singlestage.r_h1=r_h1
singlestage.r_s1=r_s1
singlestage.n=n
singlestage.alpha_3=numpy.radians(89)
singlestage.reaction=0.7
singlestage.diffusion_rotor=0.45
singlestage.diffusion_stator=0.45
singlestage.b_to_s_rotor=2.0
singlestage.b_to_s_stator=2.0

singlestage.calcThermo()
singlestage.calcAero()
#singlestage.printEverything()

singlestage.calcBladeTwist(numberCuts=5)


import sys
sys.path.append("/home/hummingbird/BladeDesigner/src")
import turboMachine

workdir=os.path.abspath('singlestage')   # '/path/to/workdir'
configuration=[5]

turbo=turboMachine.turboMachine(workdir,configuration)

turbo.debug=1
useNurbsXml=0

rotor=turbo.listRows[0]
#stator=turbo.listRows[1]

rotor.definition = 0
rotor.numberBlades = int(singlestage.z_calc_rotor)

#Geometriekonturen
rotor.coordinatesHub = zeros((5,2))
rotor.coordinatesShroud = zeros((5,2))
rotor.coordinatesHub[:,0]=linspace(0,singlestage.s_rotor,5)
rotor.coordinatesHub[:,1]=linspace(singlestage.r_h1,singlestage.r_h2,5)
rotor.coordinatesShroud[:,0]=linspace(0,singlestage.s_rotor,5)
rotor.coordinatesShroud[:,1]=linspace(singlestage.r_s1,singlestage.r_s2,5)

rotor.coordinatesStackingLine = zeros((5,2))
rotor.coordinatesStackingLine[:,0]=singlestage.s_rotor/2
rotor.coordinatesStackingLine[:,1]=linspace(singlestage.r_h1,singlestage.r_s1,5)

rotor.span=zeros((len(rotor.listProfiles)))
for n,rad in enumerate(singlestage.radius1List):
	rotor.span[n]=(rad-singlestage.radius1List[0])/(singlestage.radius1List[-1]-singlestage.radius1List[0])

rotor.debug=1
rotor.angleFlag=0

rotor.teflag="round"

## Profildefinition
#rotor.setIOAngles([122.49,122.49,129.57,134.42,134.42],[92.7,92.7,108.42,118.12,118.12])
#gammalist=[]
#for 
#rotor.setStaggerAngles([13.5,13.5,26.6,36.4,36.4])
cl=zeros((5))
for s in cl:
	s=singlestage.s_rotor
rotor.setChordLengths(cl)
rotor.setMaxThickness([0.1,0.1,0.1,0.1,0.1])


CoeffArray = zeros([1,9],'d')

a0 = 0
a2 = 0.1305026
a3 = -0.55961045
a4 = 0.33630738
a1 = -(a2+a3+a4)

p0 = 4.7
p1 = 0.71143029
p2 = 0.71323412
p3 = 1.3

CoeffArray[0][0]= a0
CoeffArray[0][1]= a1
CoeffArray[0][2]= a2
CoeffArray[0][3]= a3
CoeffArray[0][4]= a4
CoeffArray[0][5]= p0
CoeffArray[0][6]= p1
CoeffArray[0][7]= p2
CoeffArray[0][8]= p3

for n,p in enumerate(rotor.listProfiles):
	p.angleDefinition=1
	p.beta1=singlestage.beta1List[n]
	p.beta2=singlestage.beta2List[n]
	#p.Ca0=1.2
	p.debug=0		#debug level 0-2
	p.thickMeth=1	#=0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
	p.weightCondition=5	# =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
	p.weightCombination=2	# =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other 
	p.profileResolution=200
	p.flagCamberLine=0 #=0 circArc; =1 polynomial; =2 NURBS camber line
	p.flagThickDistr=1 #=0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
	p.polyThickRBs = CoeffArray


## Berechne die Turbomaschine
turbo.computeTurboMachine()


### Rowdefinition
#if useNurbsXml==1:
	#turbo.listRows[1].useNurbsXml=True

#turbo.listRows[1].definition = 0
#turbo.listRows[1].numberBlades = 29

#turbo.listRows[1].coordinatesHub = zeros((5,2))
#turbo.listRows[1].coordinatesShroud = zeros((5,2))
#turbo.listRows[1].coordinatesHub[:,0]=linspace(z2,z3,5)
#turbo.listRows[1].coordinatesHub[:,1]=linspace(r2,r3,5)
#turbo.listRows[1].coordinatesShroud[:,0]=linspace(z2,z3,5)
#turbo.listRows[1].coordinatesShroud[:,1]=shroudr

#turbo.listRows[1].coordinatesStackingLine = zeros((5,2))
#turbo.listRows[1].coordinatesStackingLine[:,0]=(z3-z2)/2+z2
#turbo.listRows[1].coordinatesStackingLine[:,1]=linspace(r2,shroudr,5)

#turbo.listRows[1].span=[0.0,0.01,0.5,0.99,1.0]

#turbo.listRows[1].debug=1
#turbo.listRows[1].angleFlag=0
#turbo.listRows[1].teflag="round"

### Profildefinition
#turbo.listRows[1].setIOAngles([60.89,60.89,66.4,69.63,69.63],[90.0,90.0,90.0,90.0,90.0])
#turbo.listRows[1].setStaggerAngles([-9.0,-9.0,-10.0,-11.0,-11.0])
#turbo.listRows[1].setChordLengths([42.4,42.4,44.59,41.9,41.9])
#turbo.listRows[1].setMaxThickness([0.1,0.1,0.1,0.1,0.1])

##Polynome Coefficients
#CoeffArray = zeros([1,9],'d')
#a0 = 0
#a2 = 0.1305026
#a3 = -0.55961045
#a4 = 0.33630738
#a1 = -(a2+a3+a4)

#p0 = 4.7
#p1 = 0.71143029
#p2 = 0.71323412
#p3 = 1.3

#CoeffArray[0][0]= a0
#CoeffArray[0][1]= a1
#CoeffArray[0][2]= a2
#CoeffArray[0][3]= a3
#CoeffArray[0][4]= a4
#CoeffArray[0][5]= p0
#CoeffArray[0][6]= p1
#CoeffArray[0][7]= p2
#CoeffArray[0][8]= p3

#for p in turbo.listRows[1].listProfiles:
	##p.Ca0=1.2
	#p.debug=0		#debug level 0-2
	#p.thickMeth=1	#=0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
	#p.weightCondition=5	# =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
	#p.weightCombination=2	# =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other 
	#p.profileResolution=200
	#p.flagCamberLine=0 #=0 circArc; =1 polynomial; =2 NURBS camber line
	#p.flagThickDistr=1 #=0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
	#p.polyThickRBs = CoeffArray


