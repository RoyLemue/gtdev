#!/usr/bin/env python
# -*- coding: utf-8 -*-

# z_l muss eins länger sein als die Anzahl der Schaufelreihen!
# *######### Configuration Data ##############
f = open("stage_config.py", "r")
lines = f.readlines()
for line in lines:
    exec(line)
##############################################


# Python Imports
# üöä
import sys, os

sys.path.insert(0, "../bladedesigner-version2")

import gtdev.helper_methods
from numpy import *
from copy import *

# Turbomachine Initialisation
workdir = os.path.abspath('stage1_r')  # '/path/to/workdir'

##### 0,1= Nabe , 2= Mittelschnitt, 4,5 = Gehäuse
useNurbsXml = 1

turbo = turboMachine.turboMachine(workdir, configuration)
# turbo=turboMachine.turboMachine(workdir)

turbo.debug = 1

#################################################  ROTOR     #############################################

for n in rotor_l:
    ## Rowdefinition
    if useNurbsXml == 1:
        turbo.listRows[n].useNurbsXml = True

    turbo.listRows[n].definition = 0
    turbo.listRows[n].numberBlades = nblades_l[n]
    turbo.listRows[n].omega = omega

    s = s_l[n] * 1000

    r_h1 = r_h1_l[n] * 1000
    r_h2 = r_h2_l[n] * 1000
    r_s1 = r_s1_l[n] * 1000
    r_s2 = r_s2_l[n] * 1000
    z_1 = z_l[n] * 1000
    z_2 = z_l[n + 1] * 1000

    turbo.listRows[n].coordinatesHub = zeros((5, 2))
    turbo.listRows[n].coordinatesShroud = zeros((5, 2))
    turbo.listRows[n].coordinatesHub[:, 0] = linspace(z_1, z_2, 5)
    turbo.listRows[n].coordinatesHub[:, 1] = linspace(r_h1, r_h2, 5)
    turbo.listRows[n].coordinatesShroud[:, 0] = linspace(z_1, z_2, 5)
    turbo.listRows[n].coordinatesShroud[:, 1] = linspace(r_s1, r_s2, 5)

    turbo.listRows[n].coordinatesStackingLine = zeros((5, 2))
    turbo.listRows[n].coordinatesStackingLine[:, 0] = (z_2 - z_1) / 2.0 + z_1
    turbo.listRows[n].coordinatesStackingLine[:, 1] = linspace(r_h1, r_s1, 5)

    # print turbo.listRows[n].coordinatesHub
    # print turbo.listRows[n].coordinatesShroud
    # print turbo.listRows[n].coordinatesStackingLine

    span = []
    for i in range(len(r_l[n])):
        turbo.listRows[n].span.append((r_l[n][i] - r_l[n][0]) / (r_l[n][-1] - r_l[n][0]))
    # print turbo.listRows[n].span

    turbo.listRows[n].span = span

    turbo.listRows[n].debug = 1
    turbo.listRows[n].angleFlag = 1
    turbo.listRows[n].teflag = "sharp"

    ## Profildefinition
    zeta1_list = []
    zeta2_list = []
    gamma_list = []
    for i in range(len(beta1_list_l[n])):
        theta = beta1_list_l[n][i] - beta2_list_l[n][i] + dev_list_l[n][i]
        zeta1_list.append(90.0 + theta / 2.0)
        zeta2_list.append(90.0 - theta / 2.0)
        gamma_list.append(beta1_list_l[n][i] - zeta1_list[i])

    gtdev.helper_methods.logger.info("zeta1: " + zeta1_list)
    gtdev.helper_methods.logger.info("zeta2:", zeta2_list)

    gtdev.helper_methods.logger.info("gamma:", gamma_list)

    turbo.listRows[n].setIOAngles(zeta1_list, zeta2_list)

    turbo.listRows[n].setStaggerAngles(gamma_list)
    turbo.listRows[n].setChordLengths([s, s, s, s, s])
    turbo.listRows[n].setMaxThickness(rotor_maxTh)

    CoeffArray = zeros((9))

    a0 = 0
    a2 = 0.1305026
    a3 = -0.55961045
    a4 = 0.33630738
    a1 = -(a2 + a3 + a4)

    p0 = 4.7
    p1 = 0.71143029
    p2 = 0.71323412
    p3 = 1.3

    CoeffArray[0] = a0
    CoeffArray[1] = a1
    CoeffArray[2] = a2
    CoeffArray[3] = a3
    CoeffArray[4] = a4
    CoeffArray[5] = p0
    CoeffArray[6] = p1
    CoeffArray[7] = p2
    CoeffArray[8] = p3

    # turbo.listRows[n].listProfiles[0].Ca0=1.2
    turbo.listRows[n].listProfiles[0].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[0].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        0].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        0].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[0].profileResolution = 200
    turbo.listRows[n].listProfiles[0].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        0].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[0].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[1].Ca0=1.2
    turbo.listRows[n].listProfiles[1].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[1].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        1].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        1].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[1].profileResolution = 200
    turbo.listRows[n].listProfiles[1].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        1].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[1].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[2].Ca0=1.2
    turbo.listRows[n].listProfiles[2].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[2].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        2].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        2].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[2].profileResolution = 200
    turbo.listRows[n].listProfiles[2].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        2].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[2].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[3].Ca0=1.2
    turbo.listRows[n].listProfiles[3].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[3].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        3].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        3].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[3].profileResolution = 200
    turbo.listRows[n].listProfiles[3].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        3].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[3].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[4].Ca0=1.2
    turbo.listRows[n].listProfiles[4].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[4].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        4].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        4].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[4].profileResolution = 200
    turbo.listRows[n].listProfiles[4].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        4].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[4].polyThickRBs = CoeffArray

#################################################  STATOR     #############################################

for n in stator_l:
    ## Rowdefinition
    if useNurbsXml == 1:
        turbo.listRows[n].useNurbsXml = True

    turbo.listRows[n].definition = 0
    turbo.listRows[n].numberBlades = nblades_l[n]
    turbo.listRows[n].omega = 0.0

    s = s_l[n] * 1000

    r_h1 = r_h1_l[n] * 1000
    r_h2 = r_h2_l[n] * 1000
    r_s1 = r_s1_l[n] * 1000
    r_s2 = r_s2_l[n] * 1000
    z_1 = z_l[n] * 1000
    z_2 = z_l[n + 1] * 1000

    turbo.listRows[n].coordinatesHub = zeros((5, 2))
    turbo.listRows[n].coordinatesShroud = zeros((5, 2))
    turbo.listRows[n].coordinatesHub[:, 0] = linspace(z_1, z_2, 5)
    turbo.listRows[n].coordinatesHub[:, 1] = linspace(r_h1, r_h2, 5)
    turbo.listRows[n].coordinatesShroud[:, 0] = linspace(z_1, z_2, 5)
    turbo.listRows[n].coordinatesShroud[:, 1] = linspace(r_s1, r_s2, 5)

    turbo.listRows[n].coordinatesStackingLine = zeros((5, 2))
    turbo.listRows[n].coordinatesStackingLine[:, 0] = (z_2 - z_1) / 2.0 + z_1
    turbo.listRows[n].coordinatesStackingLine[:, 1] = linspace(r_h1, r_s1, 5)

    # print turbo.listRows[n].coordinatesHub
    # print turbo.listRows[n].coordinatesShroud
    # print turbo.listRows[n].coordinatesStackingLine

    for i in range(len(r_l[n])):
        turbo.listRows[n].span.append((r_l[n][i] - r_l[n][0]) / (r_l[n][-1] - r_l[n][0]))
    # print turbo.listRows[n].span

    turbo.listRows[n].span = span

    turbo.listRows[n].debug = 1
    turbo.listRows[n].angleFlag = 1
    turbo.listRows[n].teflag = "sharp"

    ## Profildefinition
    zeta1_list = []
    zeta2_list = []
    gamma_list = []
    for i in range(len(beta1_list_l[n])):
        theta = beta1_list_l[n][i] - beta2_list_l[n][i] + dev_list_l[n][i]
        zeta1_list.append(90.0 + theta / 2.0)
        zeta2_list.append(90.0 - theta / 2.0)
        gamma_list.append(beta1_list_l[n][i] - zeta1_list[i])

    gtdev.helper_methods.logger.info("zeta1: " + zeta1_list)
    gtdev.helper_methods.logger.info("zeta2: " + zeta2_list)

    gtdev.helper_methods.logger.info("gamma: " + gamma_list)

    turbo.listRows[n].setIOAngles(zeta1_list, zeta2_list)

    turbo.listRows[n].setStaggerAngles(gamma_list)
    turbo.listRows[n].setChordLengths([s, s, s, s, s])
    turbo.listRows[n].setMaxThickness(stator_maxTh)

    CoeffArray = zeros((9))

    a0 = 0
    a2 = 0.1305026
    a3 = -0.55961045
    a4 = 0.33630738
    a1 = -(a2 + a3 + a4)

    p0 = 4.7
    p1 = 0.71143029
    p2 = 0.71323412
    p3 = 1.3

    CoeffArray[0] = a0
    CoeffArray[1] = a1
    CoeffArray[2] = a2
    CoeffArray[3] = a3
    CoeffArray[4] = a4
    CoeffArray[5] = p0
    CoeffArray[6] = p1
    CoeffArray[7] = p2
    CoeffArray[8] = p3

    # turbo.listRows[n].listProfiles[0].Ca0=1.2
    turbo.listRows[n].listProfiles[0].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[0].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        0].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        0].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[0].profileResolution = 200
    turbo.listRows[n].listProfiles[0].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        0].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[0].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[1].Ca0=1.2
    turbo.listRows[n].listProfiles[1].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[1].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        1].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        1].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[1].profileResolution = 200
    turbo.listRows[n].listProfiles[1].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        1].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[1].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[2].Ca0=1.2
    turbo.listRows[n].listProfiles[2].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[2].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        2].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        2].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[2].profileResolution = 200
    turbo.listRows[n].listProfiles[2].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        2].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[2].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[3].Ca0=1.2
    turbo.listRows[n].listProfiles[3].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[3].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        3].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        3].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[3].profileResolution = 200
    turbo.listRows[n].listProfiles[3].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        3].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[3].polyThickRBs = CoeffArray

    # turbo.listRows[n].listProfiles[4].Ca0=1.2
    turbo.listRows[n].listProfiles[4].debug = 1  # debug level 0-2
    turbo.listRows[n].listProfiles[4].thickMeth = 1  # =0 NACA assumed, =1 poly ThickDistr, =2 elliptic ThickDistr
    turbo.listRows[n].listProfiles[
        4].weightCondition = 5  # =0 parabel, =1 kub. parabel, =2 tangens, =3 arcsin, =4 gerade
    turbo.listRows[n].listProfiles[
        4].weightCombination = 2  # =0 curvature of polynom, =1 curvature of polynomial part, =2 div weight funct, =3 combination of polynomial & other
    turbo.listRows[n].listProfiles[4].profileResolution = 200
    turbo.listRows[n].listProfiles[4].flagCamberLine = 0  # =0 circArc; =1 polynomial; =2 NURBS camber line
    turbo.listRows[n].listProfiles[
        4].flagThickDistr = 1  # =0 no profile; =1 polynomial; =2 NURBS; =3 doubleCircArc profile
    turbo.listRows[n].listProfiles[4].polyThickRBs = CoeffArray

## Berechne die Turbomaschine
turbo.computeTurboMachine()

turbo.writeTurboMachineXml(0)

# blade=turbo.listRows[0]

############## Exporting ######################
# blade.exportBladeToIGES()
# blade.exportBladeToSTEP()
# blade.exportBladeToSTL()

# turbo.exportTurboMachineToIGES()
# turbo.exportTurboMachineToSTEP()

## Schreibe vrml-Dateien der Reihen
# for n in range(turbo.numberRows):
# turbo.listRows[n].exportBladeToSTEP("bladerow_"+str(n)+".stp")

############ opencascade test display ###############
# blade.displayNurbsCurves() #Only select one display per run!
# blade.displayBladeSurface()
# turbo.displayViewer()
# turbo.displayTurboMachine()
