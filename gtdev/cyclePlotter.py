#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
#===============================================================================


from helper_methods import *
from scipy.optimize import fsolve
import numpy


class HsPlotter(object):
	def __init__(self,label,m,Tstart,Sstart,pstart):
		self.pWidget=MplCanvas()
		self.pWidget.PlotTitle="H-S Plot"
		self.pWidget.xtitle="S [J/K]"
		self.pWidget.ytitle="dH/dt [J/s]"
		self.pWidget.format_labels()
		self.pyl=self.pWidget.ax
		self.fx=5
		self.fy=10
		
		self.R=287.15
		
		self.addnewStart(label,m,Tstart,Sstart,pstart)
		
		
	def addnewStart(self,label,m,Tstart,Sstart,pstart):
		self.T=Tstart
		self.S=Sstart
		self.p=pstart
		
		kappa=getKappa(self.T)
		self.H=kappa*self.R/(kappa-1.0)*m*self.T
		self.pyl.plot([self.S],[self.H],'ko',zorder=10000)
		self.pyl.text(self.S+self.fx,self.H+self.fy,label,size=9,clip_on=True,zorder=10000)
		
	def isentrope(self,label,m,Tend=None,pend=None):
		if pend!=None and Tend==None:
			pi_alt=self.p
			T=self.T
			for pi in numpy.linspace(self.p,pend,100):
				kappa=getKappa(T)
				T=T*(pi/pi_alt)**((kappa-1.0)/kappa)
				pi_alt=pi
			Tend=T
		if pend==None and Tend!=None:
			Ti_alt=self.T
			p=self.p
			for Ti in numpy.linspace(self.T,Tend,100):
				kappa=getKappa(Ti)
				p=p*(Ti/Ti_alt)**(kappa/(kappa-1))
				Ti_alt=Ti
			pend=p
		
		kappa=getKappa(Tend)
		Hend=kappa*self.R/(kappa-1.0)*m*Tend
		self.pyl.plot([self.S,self.S],[self.H,Hend],'b')
		self.pyl.plot([self.S],[Hend],'ko',zorder=10000)
		self.pyl.text(self.S+self.fx,Hend+self.fy,label,size=9,clip_on=True,zorder=10000)
		self.T=Tend
		self.H=Hend
		self.p=pend
		
	def isobare(self,label,m,Tend):
		isoT=[self.T]
		isoS=[self.S]
		isoH=[self.H]
		for Ti in numpy.linspace(self.T,Tend,1000):
			kappa=getKappa(Ti)
			isoT.append(Ti)
			isoS.append(isoS[-1]+m*kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2]))
			isoH.append(kappa*self.R/(kappa-1.0)*m*isoT[-1])
		self.pyl.plot(isoS,isoH,'r')
		self.pyl.plot([isoS[-1]],[isoH[-1]],'ko',zorder=10000)
		self.pyl.text(isoS[-1]+self.fx,isoH[-1]+self.fy,label,size=9,clip_on=True,zorder=10000)
		self.S=isoS[-1]
		self.H=isoH[-1]
		self.T=Tend
		
	def isochore(self,label,m,Tend):
		isoT=[self.T]
		isoS=[self.S]
		isoH=[self.H]
		for Ti in numpy.linspace(self.T,Tend,1000):
			kappa=getKappa(Ti)
			isoT.append(Ti)
			isoS.append(isoS[-1]+m*(kappa*self.R/(kappa-1.0)-self.R)*math.log(isoT[-1]/isoT[-2]))
			isoH.append(kappa*self.R/(kappa-1.0)*m*isoT[-1])
		self.pyl.plot(isoS,isoH,'g')
		self.pyl.plot([isoS[-1]],[isoH[-1]],'ko',zorder=10000)
		self.pyl.text(isoS[-1]+self.fx,isoH[-1]+self.fy,label,size=9)
		
		self.p=Tend/self.T*self.p
		self.S=isoS[-1]
		self.H=isoH[-1]
		self.T=Tend
		
	def isotherme(self,label,m,pend):
		S=self.S-self.R*math.log(pend/self.p)*m
		
		self.pyl.plot([self.S,S],[self.H,self.H],'k')
		self.pyl.plot([S],[self.H],'ko',zorder=10000)
		self.pyl.text(S+self.fx,self.H+self.fy,label,size=9,clip_on=True,zorder=10000)
		
		self.S=S
		self.p=pend
		
		
	def polytrope(self,label,m,eta_pol,Tend=None,pend=None):
		if pend!=None and Tend==None:
			if pend<self.p:
				eta_pol=1.0/eta_pol
			pi_alt=self.p
			isoT=[self.T]
			isoS=[self.S]
			isoH=[self.H]
			for pi in numpy.linspace(self.p,pend,100):
				kappa=getKappa(isoT[-1])
				isoT.append(isoT[-1]*(pi/pi_alt)**((kappa-1.0)/kappa/eta_pol))
				isoS.append(isoS[-1]+m*kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2])-m*self.R*math.log(pi/pi_alt))
				isoH.append(kappa*self.R/(kappa-1.0)*m*isoT[-1])
				pi_alt=pi
			Tend=isoT[-1]
		if pend==None and Tend!=None:
			if Tend<self.T:
				eta_pol=1.0/eta_pol
			p_alt=self.p
			isoT=[self.T]
			isoS=[self.S]
			isoH=[self.H]
			for Ti in numpy.linspace(self.T,Tend,100):
				kappa=getKappa(isoT[-1])
				isoT.append(Ti)
				p=p_alt*(isoT[-1]/isoT[-2])**(kappa*eta_pol/(kappa-1.0))
				isoS.append(isoS[-1]+m*kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2])-m*self.R*math.log(p/p_alt))
				isoH.append(kappa*self.R/(kappa-1.0)*m*isoT[-1])
				p_alt=p
			pend=p
			
		
		self.pyl.plot(isoS,isoH,'b')
		self.pyl.plot([isoS[-1]],[isoH[-1]],'ko',zorder=10000)
		self.pyl.text(isoS[-1]+self.fx,isoH[-1]+self.fy,label,size=9,clip_on=True,zorder=10000)
		
		self.T=Tend
		self.p=pend
		self.H=isoH[-1]
		self.S=isoS[-1]







class TsPlotter(object):
	def __init__(self,label,Tstart,sstart,pstart):
		self.pWidget=MplCanvas()
		self.pyl=self.pWidget.ax
		self.fx=5
		self.fy=10
		
		self.R=287.15
		
		self.addnewStart(label,Tstart,sstart,pstart)
		
		
	def addnewStart(self,label,Tstart,sstart,pstart):
		self.T=Tstart
		self.s=sstart
		self.p=pstart
		self.pyl.plot([self.s],[self.T],'ko',zorder=10000)
		self.pyl.text(self.s+self.fx,self.T+self.fy,label,size=9,clip_on=True,zorder=10000)
		
	def isentrope(self,label,Tend=None,pend=None):
		if pend!=None and Tend==None:
			pi_alt=self.p
			T=self.T
			for pi in numpy.linspace(self.p,pend,100):
				kappa=getKappa(T)
				T=T*(pi/pi_alt)**((kappa-1.0)/kappa)
				pi_alt=pi
			Tend=T
		if pend==None and Tend!=None:
			Ti_alt=self.T
			p=self.p
			for Ti in numpy.linspace(self.T,Tend,100):
				kappa=getKappa(Ti)
				p=p*(Ti/Ti_alt)**(kappa/(kappa-1))
				Ti_alt=Ti
			pend=p
		self.pyl.plot([self.s,self.s],[self.T,Tend],'b')
		self.pyl.plot([self.s],[Tend],'ko',zorder=10000)
		self.pyl.text(self.s+self.fx,Tend+self.fy,label,size=9,clip_on=True,zorder=10000)
		self.T=Tend
		self.p=pend
		
	def isobare(self,label,Tend):
		isoT=[self.T]
		isos=[self.s]
		for Ti in numpy.linspace(self.T,Tend,100):
			kappa=getKappa(Ti)
			isoT.append(Ti)
			isos.append(isos[-1]+kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2]))
			
		self.pyl.plot(isos,isoT,'r')
		self.pyl.plot([isos[-1]],[Tend],'ko',zorder=10000)
		self.pyl.text(isos[-1]+self.fx,Tend+self.fy,label,size=9,clip_on=True,zorder=10000)
		self.s=isos[-1]
		self.T=Tend
		
	def isochore(self,label,Tend):
		isoT=[self.T]
		isos=[self.s]
		for Ti in numpy.linspace(self.T,Tend,100):
			kappa=getKappa(Ti)
			isoT.append(Ti)
			isos.append(isos[-1]+(kappa*self.R/(kappa-1.0)-self.R)*math.log(isoT[-1]/isoT[-2]))
		
		self.pyl.plot(isos,isoT,'g')
		self.pyl.plot([isos[-1]],[Tend],'ko',zorder=10000)
		self.pyl.text(isos[-1]+self.fx,Tend+self.fy,label,size=9)
		
		self.p=Tend/self.T*self.p
		self.s=isos[-1]
		self.T=Tend
		
	def isotherme(self,label,pend):
		s=self.s-self.R*math.log(pend/self.p)
		
		self.pyl.plot([self.s,s],[self.T,self.T],'k')
		self.pyl.plot([s],[self.T],'ko',zorder=10000)
		self.pyl.text(s+self.fx,self.T+self.fy,label,size=9,clip_on=True,zorder=10000)
		
		self.s=s
		self.p=pend
		
		
	def polytrope(self,label,eta_pol,Tend=None,pend=None):
		if pend!=None and Tend==None:
			if pend<self.p:
				eta_pol=1.0/eta_pol
			pi_alt=self.p
			isoT=[self.T]
			isos=[self.s]
			for pi in numpy.linspace(self.p,pend,100):
				kappa=getKappa(isoT[-1])
				isoT.append(isoT[-1]*(pi/pi_alt)**((kappa-1.0)/kappa/eta_pol))
				isos.append(isos[-1]+kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2])-self.R*math.log(pi/pi_alt))
				pi_alt=pi
			Tend=isoT[-1]
		if pend==None and Tend!=None:
			if Tend<self.T:
				eta_pol=1.0/eta_pol
			p_alt=self.p
			isoT=[self.T]
			isos=[self.s]
			for Ti in numpy.linspace(self.T,Tend,100):
				kappa=getKappa(isoT[-1])
				isoT.append(Ti)
				p=p_alt*(isoT[-1]/isoT[-2])**(kappa*eta_pol/(kappa-1.0))
				isos.append(isos[-1]+kappa*self.R/(kappa-1.0)*math.log(isoT[-1]/isoT[-2])-self.R*math.log(p/p_alt))
				p_alt=p
			pend=p
		self.pyl.plot(isos,isoT,'b')
		self.pyl.plot([isos[-1]],[Tend],'ko',zorder=10000)
		self.pyl.text(isos[-1]+self.fx,Tend+self.fy,label,size=9,clip_on=True,zorder=10000)
		
		self.T=Tend
		self.p=pend
		self.s=isos[-1]




import sys
from PyQt4.QtCore import QSize, SIGNAL, SLOT
import PyQt4.QtXml
from PyQt4.QtGui import QApplication,QDialog,QWidget, QVBoxLayout, QComboBox, QSizePolicy, QHBoxLayout, QIcon, QPixmap
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class MplCanvas(FigureCanvas):
	def __init__(self, pParent=None, width = 10, height = 12, dpi = 100, sharex = None, sharey = None):
		## @brief Graphic to be shown<br><em>Grafik die angezeigt wird</em>
		self.fig = Figure(figsize = (width, height), dpi=dpi, facecolor = '#FFFFFF')
		## @brief Subgraphic<br><em>Untergrafik</em>
		self.ax = self.fig.add_subplot(111, sharex = sharex, sharey = sharey)
		self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
		## @brief Labeling of x-axis<br><em>Beschriftungen der X-Achse</em>
		self.xtitle="s [J/(K kg)]"
		## @brief Labeling of y-axis<br><em>Beschriftungen der Y-Achse</em>
		self.ytitle="T [K]"
		## @brief Header of the graphical window<br><em>Titel des Zeichenfenster</em>
		self.PlotTitle = "T-s Plot"
		## @brief State of the grid<br><em>Status des Gitters</em>
		self.grid_status = True
		## @brief Type of x-axis<br><em>Art der X-Achse</em>
		self.xaxis_style = 'linear'
		## @brief Type of y-axis<br><em>Art der Y-Achse</em>
		self.yaxis_style = 'linear'
		self.format_labels()
		self.ax.hold(True)
		FigureCanvas.__init__(self, self.fig)
		#self.fc = FigureCanvas(self.fig)
		FigureCanvas.setSizePolicy(self,
			QSizePolicy.Expanding,
			QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def format_labels(self):
		self.ax.set_title(self.PlotTitle)
		self.ax.title.set_fontsize(10)
		self.ax.set_xlabel(self.xtitle, fontsize = 9)
		self.ax.set_ylabel(self.ytitle, fontsize = 9)
		labels_x = self.ax.get_xticklabels()
		labels_y = self.ax.get_yticklabels()

		for xlabel in labels_x:
			xlabel.set_fontsize(8)
		for ylabel in labels_y:
			ylabel.set_fontsize(8)
			ylabel.set_color('b')
			
	def sizeHint(self):
		w, h = self.get_width_height()
		return QSize(w, h)

	def minimumSizeHint(self):
		return QSize(100 , 100)
		




if __name__=="__main__":
	#Qt-Application erstellen
	pApp = QApplication([])
	
	
	
	#Umgebung
	test=TsPlotter("Tt0",288.15,100.,101325.)
	#Einlauf
	test.isentrope("",pend=test.p*0.95)
	#Verdichter
	test.polytrope("Tt3",0.8,pend=test.p*3.0)
	#Diffusor
	test.isentrope("",pend=test.p*0.95)
	#Brennkammer
	test.isochore("Tt4",1000.)
	#Turbine
	test.polytrope("Tt5",0.8,Tend=880.)
	#Düse
	test.isotherme("",test.p*0.95)
	#Entspannung
	test.isentrope("Tt9",pend=101325.)
	test.isobare("",288.15)
		
	toolbar=NavigationToolbar(test.pWidget,test.pWidget)	
	l=QVBoxLayout()
	l.addWidget(test.pWidget)
	l.addWidget(toolbar)
	widget=QDialog()
	widget.setLayout(l)
	
	widget.show()
	
	sys.exit(pApp.exec_())
	
	