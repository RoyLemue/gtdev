# -*- coding: utf-8 -*-
import sys, os
import numpy

def genCompressorAxial(compressor_object,filepath,projectpath,bd_sourcepath="/home/sebastian/Workspace/bladedesigner/BladeDesigner/src"):
	co=compressor_object
	f=open(filepath,"w")
	f.write("bd_sourcepath="+bd_sourcepath)
	f.write("import sys,os,turboMachine,numpy")
	f.write("sys.path.insert(0,bd_sourcepath)")
	f.write("comp=turboMachine.turboMachine("+projectpath+", [5,5])")
	
	f.write("comp.listRows[0].definition=0")
	f.write("comp.listRows[0].coordinatesHub=zeros((6,2))")
	f.write("comp.listRows[0].coordinatesShroud = zeros((6,2))")
	f.write("comp.listRows[0].coordinatesHub[:,0]="+str(numpy.linspace(0,1.2*co.chordLength_1,6)))
	f.write("comp.listRows[0].coordinatesHub[:,1]="+str(numpy.linspace(co.r_h1,co.r_h2)))
	f.write("comp.listRows[0].coordinatesShroud[:,0]="+str(numpy.linspace(0,1.2*co.chordLength_1,6)))
	f.write("comp.listRows[0].coordinatesShroud[:,1]="+str(numpy.linspace(co.r_s1,co.r_s2)))
	f.write("comp.listRows[0].coordinatesStackingLine = zeros((6,2))")
	f.write("comp.listRows[0].coordinatesStackingLine[:,0]="+str(0.4*co.chordLength))
	f.write("comp.listRows[0].coordinatesStackingLine[:,1]="+str(numpy.linspace(co.r_h1,co.r_s1)))
	f.write("comp.listRows[0].span=[0.0,0.01,0.5,0.99,1.0]")
	f.write("comp.listRows[0].debug=1")
	f.write("comp.listRows[0].angleFlag=1")
	
	f.write("comp.listRows[0].listProfiles[0].chordLength="+str(co.chordLength_1))
	f.write("comp.listRows[0].listProfiles[1].chordLength="+str(co.chordLength_1))
	f.write("comp.listRows[0].listProfiles[2].chordLength="+str(co.chordLength_1))
	f.write("comp.listRows[0].listProfiles[3].chordLength="+str(co.chordLength_1))
	f.write("comp.listRows[0].listProfiles[4].chordLength="+str(co.chordLength_1))
	
	f.write("comp.listRows[0].listProfiles[0].beta1="+str(co.beta_1))
	f.write("comp.listRows[0].listProfiles[1].beta1="+str(co.beta_1))
	f.write("comp.listRows[0].listProfiles[2].beta1="+str(co.beta_1))
	f.write("comp.listRows[0].listProfiles[3].beta1="+str(co.beta_1))
	f.write("comp.listRows[0].listProfiles[4].beta1="+str(co.beta_1))
	
	f.write("comp.listRows[0].listProfiles[0].beta2="+str(co.beta_2))
	f.write("comp.listRows[0].listProfiles[1].beta2="+str(co.beta_2))
	f.write("comp.listRows[0].listProfiles[2].beta2="+str(co.beta_2))
	f.write("comp.listRows[0].listProfiles[3].beta2="+str(co.beta_2))
	f.write("comp.listRows[0].listProfiles[4].beta2="+str(co.beta_2))
	
	f.write("comp.listRows[1].definition=0")
	f.write("comp.listRows[1].coordinatesHub=zeros((6,2))")
	f.write("comp.listRows[1].coordinatesShroud = zeros((6,2))")
	f.write("comp.listRows[1].coordinatesHub[:,0]="+str(numpy.linspace(1.2*co.chordLength_1,1.2*co.chordLength_1+1.2*co.chordLength_2,6)))
	f.write("comp.listRows[1].coordinatesHub[:,1]="+str(numpy.linspace(co.r_h2,co.r_h3)))
	f.write("comp.listRows[1].coordinatesShroud[:,0]="+str(numpy.linspace(1.2*co.chordLength_1,1.2*co.chordLength_1+1.2*co.chordLength_2,6)))
	f.write("comp.listRows[1].coordinatesShroud[:,1]="+str(numpy.linspace(co.r_s2,co.r_s3)))
	f.write("comp.listRows[1].coordinatesStackingLine = zeros((6,2))")
	f.write("comp.listRows[1].coordinatesStackingLine[:,0]="+str(1.2*co.chordLength_1+0.4*co.chordLength_2))
	f.write("comp.listRows[1].coordinatesStackingLine[:,1]="+str(numpy.linspace(co.r_h2,co.r_s2)))
	f.write("comp.listRows[1].span=[0.0,0.01,0.5,0.99,1.0]")
	f.write("comp.listRows[1].debug=1")
	f.write("comp.listRows[1].angleFlag=1")
	
	f.write("comp.listRows[1].listProfiles[0].chordLength="+str(co.chordLength_2))
	f.write("comp.listRows[1].listProfiles[1].chordLength="+str(co.chordLength_2))
	f.write("comp.listRows[1].listProfiles[2].chordLength="+str(co.chordLength_2))
	f.write("comp.listRows[1].listProfiles[3].chordLength="+str(co.chordLength_2))
	f.write("comp.listRows[1].listProfiles[4].chordLength="+str(co.chordLength_2))
	
	f.write("comp.listRows[1].listProfiles[0].beta1="+str(co.alpha_1))
	f.write("comp.listRows[1].listProfiles[1].beta1="+str(co.alpha_1))
	f.write("comp.listRows[1].listProfiles[2].beta1="+str(co.alpha_1))
	f.write("comp.listRows[1].listProfiles[3].beta1="+str(co.alpha_1))
	f.write("comp.listRows[1].listProfiles[4].beta1="+str(co.alpha_1))
	                                                         
	f.write("comp.listRows[1].listProfiles[0].beta2="+str(co.alpha_2))
	f.write("comp.listRows[1].listProfiles[1].beta2="+str(co.alpha_2))
	f.write("comp.listRows[1].listProfiles[2].beta2="+str(co.alpha_2))
	f.write("comp.listRows[1].listProfiles[3].beta2="+str(co.alpha_2))
	f.write("comp.listRows[1].listProfiles[4].beta2="+str(co.alpha_2))
	
	for j in range(2):
		for i in range(5):
			f.write("comp.listRows["+j+"].listProfiles["+i+"].angleDefinition=1")		
			f.write("comp.listRows["+j+"].listProfiles["+i+"].thickMeth=0")	#=0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
			f.write("comp.listRows["+j+"].listProfiles["+i+"].weightCondition=5")	# =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 hyperbel, =5 gerade
			f.write("comp.listRows["+j+"].listProfiles["+i+"].weightCombination=2")	# =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other weight funct
			f.write("comp.listRows["+j+"].listProfiles["+i+"].profileResolution=200")
			f.write("comp.listRows["+j+"].listProfiles["+i+"].polyCamberLineDegree= 3")
			f.write("comp.listRows["+j+"].listProfiles["+i+"].flagCamberLine=1")	#=0 circArc; =1 polynomial; =2 NURBS camber line; =3 NACA 65
			f.write("comp.listRows["+j+"].listProfiles["+i+"].flagThickDistr=2")	#=0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
			f.write("comp.listRows["+j+"].listProfiles["+i+"].approxPolyCoeff  = 1")
			
			f.write("CoeffArray = zeros([1,9],'d')")
			f.write("a0 = 0")
			f.write("a2 = 0.1405026")
			f.write("a3 = -0.56161045")
			f.write("a4 = 0.33630738")
			f.write("a1 = -(a2+a3+a4)")
			f.write("p0 = 2.37085805")
			f.write("p1 = 0.71143029")
			f.write("p2 = 0.71322412")
			f.write("p3 = 1.5")
			f.write("CoeffArray[0][0]= a0")
			f.write("CoeffArray[0][1]= a1")
			f.write("CoeffArray[0][2]= a2")
			f.write("CoeffArray[0][3]= a3")
			f.write("CoeffArray[0][4]= a4")
			f.write("CoeffArray[0][5]= p0")
			f.write("CoeffArray[0][6]= p1")
			f.write("CoeffArray[0][7]= p2")
			f.write("CoeffArray[0][8]= p3")
			
			f.write("comp.listRows["+j+"].listProfiles["+i+"].polyThickRBs = CoeffArray")
			
			f.write("controlPointNumber=8")
			f.write("nurbsCoordinatesThick = zeros([controlPointNumber,2],'d')")
				
			# x-coordinates
			f.write("nurbsCoordinatesThick[0][0]= 0.0")
			f.write("nurbsCoordinatesThick[1][0]= 0.0002")
			f.write("nurbsCoordinatesThick[2][0]= 0.15")
			f.write("nurbsCoordinatesThick[3][0]= 0.37")
			f.write("nurbsCoordinatesThick[4][0]= 0.6")
			f.write("nurbsCoordinatesThick[5][0]= 0.8")
			f.write("nurbsCoordinatesThick[6][0]= 0.9999")
			f.write("nurbsCoordinatesThick[7][0]= 1.0")
			
			# y-coordinates
			f.write("nurbsCoordinatesThick[0][1]= 0.0")
			f.write("nurbsCoordinatesThick[1][1]= 0.018")
			f.write("nurbsCoordinatesThick[2][1]= 0.035")
			f.write("nurbsCoordinatesThick[3][1]= 0.05")
			f.write("nurbsCoordinatesThick[4][1]= 0.045")
			f.write("nurbsCoordinatesThick[5][1]= 0.015")
			f.write("nurbsCoordinatesThick[6][1]= 0.005")
			f.write("nurbsCoordinatesThick[7][1]= 0.0")
			
			f.write("comp.listRows["+j+"].listProfiles["+i+"].approxNurbsNoseRad = 1.0")
			f.write("comp.listRows["+j+"].listProfiles["+i+"].controlPointsThick=nurbsCoordinatesThick")
			f.write("comp.listRows["+j+"].listProfiles["+i+"].error = 1e-11")
			f.write("comp.listRows["+j+"].listProfiles["+i+"].maxIter = 3000")
	
	f.write("comp.computeTurboMachine()")
	f.write("for n in range(comp.numberRows):")
	f.write("\tcomp.listRows[n].writeVRML()")
	
	f.close()
	
	
	