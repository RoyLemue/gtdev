#!/usr/bin/env python
# -*- coding: utf-8 -*-



#Liste der zu untersuchenden Werte
#Hier können alle Werte eingetragen werden, die in der äußeren Schleife iteriert werden sollen.
#Der erste Wert wird in einer durchgezogenen Linie geplottet, die darauffolgenden gestrichelt.
varlist=[1]

#Liste der x-Achse über die geplottet wird. Dies ist die innere Schleife
xlist=numpy.linspace(1.3,1.3,1)




import numpy

turbo=turbofan.Turbofan_Recalc("Hummingbird Turbofan Prototype TF-01")

sfcp=[]
mflp=[]
c19p=[]
c9p=[]
mup=[]
fOut=open("liste.txt", 'w')

for var in varlist:
	
	mup.append([])
	sfcp.append([])
	mflp.append([])
	c19p.append([])
	c9p.append([])
	
	for x in xlist:

############## Turbofan Initialisierung ####################################

		#Turbofan-Randbedingungen
		turbo.thrust=800.0 #N
		turbo.bypassRatio=2.5   #Bypass ist die x-Achse
		turbo.T_inf=288.15 #K
		turbo.mflow=5.01163828844
		turbo.Pi_inlet=0.95
		turbo.Pi_splitter=0.95

		turbo.c_0=0.0 #m/s

		turbo.eta_mech_lps=0.98
		turbo.eta_mech_hps=0.98

		#Fanrandbedingungen
		turbo.fan.Ma_inlet=0.5
		turbo.fan.Ma_outlet=0.5
		turbo.fan.eta_pol=0.8
		turbo.fan.T_t1=288.15
		turbo.fan.Pi=1.3       #Fandruckverhältnis wird variiert

		#HPC Randbedingungen
		turbo.hpc.Ma_inlet=0.5
		turbo.hpc.Ma_outlet=0.7
		turbo.hpc.eta_pol=0.75
		turbo.hpc.Pi=3.5

		#Brennkammer RB
		turbo.combc.Ma_inlet=0.2
		turbo.combc.Ma_outlet=0.5
		turbo.combc.T_t3=1100.0 #K

		#HPT RB
		turbo.hpt.Ma_inlet=0.5
		turbo.hpt.Ma_outlet=0.5
		turbo.hpt.eta_pol=0.8

		#LPT RB
		turbo.lpt.Ma_inlet=0.45
		turbo.lpt.Ma_outlet=0.45
		turbo.lpt.eta_pol=0.8

		#Nozzles
		turbo.hn.Pi=0.95
		turbo.cn.Pi=0.95

############################################################################

		# Berechnung:
		turbo.calcThermo()
		print "\npi_fan:",x
		print "SFC",turbo.SFC
		print "F",turbo.F
		
		
		mup[-1].append(x)
		sfcp[-1].append(turbo.SFC)
		mflp[-1].append(turbo.mflow)
		c19p[-1].append(turbo.c_19)
		c9p[-1].append(turbo.c_9)

fOut.write(str(sfcp)+"\n"+str(mup)+"\n"+str(mflp))

import pylab as plt

fig = plt.figure(1)

host = fig.add_subplot(111)

host.set_xlabel("Distance")

par1 = host.twinx()

p1, = host.plot(mup[0], sfcp[0], "b-", label="SFC")
p2, = par1.plot(mup[0], mflp[0], "g-", label="eta_tot")

mupl=mup[0]
sfcpl=sfcp[0]
mflpl=mflp[0]
for n in range(len(mup)-1):
	host.plot(mup[n+1], sfcp[n+1], "b--", label="SFC")
	par1.plot(mup[n+1], mflp[n+1], "g--", label="eta_tot")
	mupl=mupl+mup[n+1]
	sfcpl=sfcpl+sfcp[n+1]
	mflpl=mflpl+mflp[n+1]


host.set_xlim(min(mupl), max(mupl))
host.set_ylim(min(sfcpl), max(sfcpl))
par1.set_ylim(min(mflpl), max(mflpl))

host.set_xlabel("Bypass Ratio")
host.set_ylabel("SFC")
par1.set_ylabel("eta_tot")

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())

lines = [p1, p2]
host.legend(lines, [l.get_label() for l in lines])
plt.show()








