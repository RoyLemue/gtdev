# -*- coding: utf-8 -*-

# Diese Datei beinhaltet den Thermodynamischen Kreisprozess des TF01 nach dem Freeze am 2.12.10
# NICHT MEHR VERÄNDERN!!!

turbo=turbofan.Turbofan("TF-01 Prototype")

############## Turbofan Initialisierung ####################################

#Turbofan-Randbedingungen
turbo.thrust=800 #N
turbo.bypassRatio=2.5  
turbo.T_inf=288.15 #K

turbo.c_0=0.0 #m/s

turbo.eta_mech_lps=0.99
turbo.eta_mech_hps=0.99

#Fanrandbedingungen
turbo.fan.Ma_inlet=0.4
turbo.fan.eta_pol=0.80
turbo.fan.T_t1=288.15
turbo.fan.Pi=1.3

#HPC Randbedingungen
turbo.hpc.Ma_inlet=0.4
turbo.hpc.eta_pol=0.80
turbo.hpc.Pi=3.5

#Brennkammer RB
turbo.combc.Ma_inlet=0.2
turbo.combc.Ma_outlet=0.4
turbo.combc.T_t3=1100. #K

#HPT RB
turbo.hpt.Ma_inlet=0.4
turbo.hpt.Ma_outlet=0.4
turbo.hpt.eta_pol=0.80

#LPT RB
turbo.lpt.Ma_inlet=0.4
turbo.hpt.Ma_outlet=0.4
turbo.lpt.eta_pol=0.80

#Nozzles
turbo.hn.Pi=0.95
turbo.cn.Pi=0.95

############################################################################

turbo.calcThermo()
turbo.printThermo()