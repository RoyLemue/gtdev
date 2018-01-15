#!/usr/bin/env python
# -*- coding: utf-8 -*-



turbo=turbojet.Turbojet("TJ-70")


#Turbojet-Randbedingungen
turbo.thrust=120 #N
turbo.T_inf=288.15 #K
turbo.Pi_inlet=0.95

turbo.c_0=0.0 #m/s

turbo.eta_mech_hps=0.99

#HPC Randbedingungen
turbo.hpc.Ma_inlet=0.4
turbo.hpc.eta_pol=0.75
turbo.hpc.Pi=3.9

#Brennkammer RB
turbo.combc.Ma_inlet=0.2
turbo.combc.Ma_outlet=0.4
turbo.combc.T_t3=1000 #K

#HPT RB
turbo.hpt.Ma_inlet=0.4
turbo.hpt.Ma_outlet=0.4
turbo.hpt.eta_pol=0.8

#Nozzle
turbo.hn.Pi=0.95

turbo.calcThermo()
turbo.printThermo()

