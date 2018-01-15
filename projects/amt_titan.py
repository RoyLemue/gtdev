#!/usr/bin/env python
# -*- coding: utf-8 -*-



turbo=turbojet.Turbojet("AMT Titan")


#Turbojet-Randbedingungen
turbo.thrust=400 #N
turbo.T_inf=288.15 #K
turbo.Pi_inlet=0.95

turbo.c_0=0.0 #m/s

turbo.eta_mech_hps=0.99

#HPC Randbedingungen
turbo.hpc.Ma_inlet=0.4
turbo.hpc.eta_pol=0.85
turbo.hpc.Pi=3.9

#Brennkammer RB
turbo.combc.Ma_inlet=0.2
turbo.combc.Ma_outlet=0.4
turbo.combc.T_t3=1100 #K

#HPT RB
turbo.hpt.Ma_inlet=0.4
turbo.hpt.Ma_outlet=0.4
turbo.hpt.eta_pol=0.85

#Nozzle
turbo.hn.Pi=0.97

turbo.calcThermo()
turbo.printThermo()