#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
# ===============================================================================

# helper_methods.py

# Importiere notwendige Module
import math
from scipy.optimize import fsolve
import numpy
import logging
import sys

# TODO derive own logging class
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatterText = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatterHeader = logging.Formatter(
    """===============================================================================
    %(message)s
    ===============================================================================""")
formatterModule = logging.Formatter('----- %(message)s -----')
formatterPlain = logging.Formatter('%(message)s')
ch.setFormatter(formatterText)
logger.addHandler(ch)


def logHeader(title):
    ch.setFormatter(formatterHeader)
    logger.info(title)
    ch.setFormatter(formatterText)


def logModule(module):
    ch.setFormatter(formatterModule)
    logger.info(module)
    ch.setFormatter(formatterText)


def logPlain(text):
    ch.setFormatter(formatterPlain)
    logger.info(text)
    ch.setFormatter(formatterText)

## return specific gas constant [J/kgK] for selectable fluid
#
# @todo new class (or container) for material to make functions fail safe
#
# @param material
#	identifier for the fluid under consideration (currently only "Air" and "exhaust" are supported)
# @param beta
#	?
def getR(material="Air", beta=0.0):
    if material == "Air":
        return 287.15
    if material == "exhaust":
        if beta == 0.0:
            return 287.15
        else:
            return 8314.472 * (0.034524 + beta * 0.035645) / (1 + beta)


## return specific heat coefficent kappa [-] for selectable fluid and conditions
#
# calculates kappa for a given total temperature, mach-number iteratively
# @param Tt
#	total temperature [K]
# @param Ma
#	mach number [-]
# @param material
#	identifier for the fluid under consideration (currently only "Air" and "exhaust" are supported)
# @param beta
#	?
def getKappa(Tt=288.15, Ma=0.0, material="Air", beta=0.0):
    # Funktion für die Korrelation zwischen kappa und T (Druck Standardatmosphaere)
    if material == "Air" and beta == 0:
        def kappa_fun(T):
            # Koeffizienten für kappa
            a = 2.764495554e-020
            b = -1.588301666e-016
            c = 2.93836602 * 0.0000000000001
            d = -1.177356679 * 0.0000000001
            e = -1.667416736 * 0.0000001
            f = 5.973962506 * 0.00001
            g = 1.398176676 * 1
            return a * T ** 6 + b * T ** 5 + c * T ** 4 + d * T ** 3 + e * T ** 2 + f * T ** 1 + g * T ** 0

    if material == "exhaust":
        def kappa_fun(T):
            R = getR(material=material, beta=beta)
            if T >= 1000:
                a = 863.29014498
                b = 405.39409798e-3
                c = -153.82359960e-6
                d = 27.94176815e-9
                e = -1.92639216e-12
                f = 1000.10332581
                g = 2994.47427116e-3
                h = -1076.165307870e-6
                i = 175.24619645e-9
                j = -10.62294583e-12
            elif T < 1000:
                a = 1057.99590453
                b = -449.19800335e-3
                c = 1109.19492375e-6
                d = -717.44852819e-9
                e = 140.33180754e-12
                f = 443.41673618
                g = 7367.21480416e-3
                h = -10617.04784788e-6
                i = 8418.76668056e-9
                j = -2529.31551918e-12
            cp = 1 / (1 + beta) * (a + b * T + c * T ** 2 + d * T ** 3 + e * T ** 4 + beta * (
                f + g * T + h * T ** 2 + i * T ** 3 + j * T ** 4))
            return cp / (cp - R)

    # Funktion für fsolve
    def iterate_fun(kappa, Tt, Ma):
        # Berechne mit dem Input-Kappa (kappa_x) die statische Temperatur
        T = Tt / (1 + (kappa - 1) / 2 * Ma ** 2)
        # Gib die Differenz zwischen Input-Kappa und neu berechnetem Kappa aus T aus.
        return kappa - kappa_fun(T)

    kappa = float(fsolve(iterate_fun, 1.4, args=(Tt, Ma)))

    return kappa


## calculate end state of an isentropic process
#
# takes the initial thermodynamic state, given by the static temperature T1 [K] and static pressure p1 [Pa],
# and one parameter for the end state (either the static temperature T2 [K] or static pressure p2 [Pa]),
# and calculates the missing parameter for the end state.
#
# @todo unify return output (e.g. via new class thermodynamic state
#
# @param T1
#	static temperature state 1
# @param T2
#	static temperature state 2
# @param p1
#	static pressure state 1
# @param p2
#	static pressure state 2
# @param Ma
#	mach number [-]
# @param material
#	identifier for the fluid under consideration (currently only "Air" and "exhaust" are supported)
# @param beta
#	?
def isentrope(T1=None, T2=None, p1=None, p2=None, Ma=0.0, material="Air", beta=0.0):
    if p2 != None and T2 == None:
        pi_alt = p1
        T = T1
        for pi in numpy.linspace(p1, p2, 10):
            kappa = getKappa(T, Ma, material=material, beta=beta)
            T = T * (pi / pi_alt) ** ((kappa - 1.0) / kappa)
            pi_alt = pi
        T2 = T
        return T2
    if p2 == None and T2 != None:
        Ti_alt = T1
        p = p1
        for Ti in numpy.linspace(T1, T2, 10):
            kappa = getKappa(Ti, Ma, material=material, beta=beta)
            p = p * (Ti / Ti_alt) ** (kappa / (kappa - 1))
            Ti_alt = Ti
        p2 = p
        return p2


## calculate end state of an polytropic process
#
# takes the initial thermodynamic state, given by the static temperature T1 [K] and static pressure p1 [Pa],
# and one parameter for the end state (either the static temperature T2 [K] or static pressure p2 [Pa]),
# and calculates the missing parameter for the end state.
#
# @todo unify return output (e.g. via new class thermodynamic state)
#
# @param eta_pol
#	polytropic efficiency
# @param T1
#	static temperature state 1
# @param T2
#	static temperature state 2
# @param p1
#	static pressure state 1
# @param p2
#	static pressure state 2
# @param Ma
#	mach number [-]
# @param material
#	identifier for the fluid under consideration (currently only "Air" and "exhaust" are supported)
# @param beta
#	?	
def polytrope(eta_pol=None, T1=None, T2=None, p1=None, p2=None, Ma=0.0, material="Air", beta=0.0):
    R = getR(material=material, beta=beta)

    if p2 != None and T2 == None:
        if p2 < p1:
            eta_pol = 1.0 / eta_pol
        pi_alt = p1
        isoT = [T1]
        for pi in numpy.linspace(p1, p2, 10):
            kappa = getKappa(isoT[-1], Ma, material=material, beta=beta)
            isoT.append(isoT[-1] * (pi / pi_alt) ** ((kappa - 1.0) / kappa / eta_pol))
            pi_alt = pi
        T2 = isoT[-1]
        return T2
    if p2 == None and T2 != None:
        if T2 < T1:
            eta_pol = 1.0 / eta_pol
        p_alt = p1
        isoT = [T1]
        for Ti in numpy.linspace(T1, T2, 10):
            kappa = getKappa(isoT[-1], Ma, material=material, beta=beta)
            isoT.append(Ti)
            p = p_alt * (isoT[-1] / isoT[-2]) ** (kappa * eta_pol / (kappa - 1.0))
            p_alt = p
        p2 = p
        return p2


        ##Funktion für die Korrelation zwischen T und cp (Druck Standardatmosphaere)
        # def cp_fun(T):
        ##Koeffizienten für cp
        # l=-6.516909612e-017
        # m=3.956210598*0.0000000000001
        # n=-8.242473265*0.0000000001
        # o=5.660507408*0.0000001
        # p=1.473238802*0.0001
        # q=-8.644305562*0.01
        # r=1.007588401*1000
        # return l*T**6+m*T**5+n*T**4+o*T**3+p*T**2+q*T**1+r*T**0

# print getKappa(Tt=1100,Ma=0.4)

# print getKappa(Tt=1100,Ma=10,material="exhaust",beta=0.034)
