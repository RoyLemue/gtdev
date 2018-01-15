#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
#===============================================================================


#bladeDesignerXML.py
#imports:

from xml.dom import minidom
import os

class BdXML(object):
	def __init__(self,stagelist):
		## Liste der Stufenobjekte (z.b. [compressor.AxialCompressor(),...])
		self.stagelist=stagelist
	
	#XML-Funktion. Erwartet den Projektnamen und das Verzeichnis in dem der neue Projektordner erzeugt werden soll
	def writeTurboMachineXML(self,projectname,path=""):
		if path=="":
			path=os.path.abspath(".")
		if not os.path.exists(path+"/"+projectname):
			print "Creating Directory",path+"/"+projectname
			os.mkdir(path+"/"+projectname)
			
		filename = path+"/"+projectname+"/"+projectname+'.xml'
		
		xml_doc = """<?xml version="1.0" encoding="UTF-8"?>
		<turboMachine/>""".encode("utf-8")
		
		#Hier wird das XML-Objekt erzeugt
		dom_object = minidom.parseString(xml_doc)
		elementTurb = dom_object.getElementsByTagName("turboMachine")[0]
		
		#Hier wird von jedem Objekt in der Liste die "writeXML"-Funktion aufgerufen. Hat sie keines, gibts ne Exception.
		try:
			for stagenumber,stage in enumerate(self.stagelist):
				stage.writeXML(dom_object,stagenumber)
		except AttributeError:
			print "Component has no xml output."
			
		#Nun wird alles in die Datei geschrieben
		f = open(filename, "w")
		dom_object.writexml(f, "", "\t", "\n","utf-8")
		f.close()
		
		print "BladeDesigner XML File written to",filename