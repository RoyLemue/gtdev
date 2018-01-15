#!/usr/bin/env python
# -*- coding: utf-8 -*-

#===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
#===============================================================================

## @package gtdev
#  The main module for the gas turbine developer

import sys, os, numpy
import argparse

#try:
	#sys.path.append(sys.path[0] + '/src')
	#sys.path.append(sys.path[0] + '/gui')
#except:
	#pass
#if sys.platform == 'linux2':
	#sys.path.append(sys.path[0] + '/src')
	#sys.path.append(sys.path[0] + '/gui')
#elif sys.platform == 'win32':
	#sys.path.append(sys.path[0] + '\src')
	#sys.path.append(sys.path[0] + '\gui')
#else:
	#print 'Please define the path for src and gui manually'

from gtdev import turbofan,turbojet,compressor,turbine,combChamber,bladeDesignerXML

## Entry point for each gtdev instance
#
#  Tasks:
#  - Parsing the options supplied to the application using OptionParser
#  - Initializing the GUI or non-interactive text mode appropriately
def main():
	
	
	# @deprecated parsing given options (using the OptionParser from optparse)
	#from optparse import OptionParser
	#usage = "usage: %prog [options] arg"
	#parser = OptionParser(usage=usage)
	#parser.add_option("-f", "--file", dest="filename",
	#				help="noniteractive text mode: initialise computation by FILE", metavar="FILE")
	#parser.add_option("-g", "--gui", action="store_true" ,dest="gui", default=False,
	#				help="start gtdev in interactive GUI mode (default)")
	#(options, args) = parser.parse_args()

	argparser = argparse.ArgumentParser(
		prog = 'Gas Turbine Developer',
		description = 'open source utility for designing gas turbines',
		epilog = '\
=============================================================================\n\
| Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines                  |\n\
| Institute for Flight Propulsion, Technical University Munich, Germany     |\n\
|                                                                           |\n\
| Authors:                                                                  |\n\
|  Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl       |\n\
|                                                                           |\n\
| Published under the Terms of GNU public licence v3                        |\n\
=============================================================================\n',
		formatter_class = argparse.RawDescriptionHelpFormatter)
		
	argparser.add_argument('-f', '--file', dest='filename',
		help='initialize computation with file FILE', metavar='FILE')
		
	argparser.add_argument('-t', '--text', dest='text', action='store_true', default=False,
		help='start in non-interactive text mode')
	
	args = argparser.parse_args()
	
	# start graphical mode
	if not args.text and not args.filename:
		from PyQt4 import QtGui, QtCore
		from gtdev.gui import GUIControl

		app = QtGui.QApplication(sys.argv)
		gui = GUIControl.GUIControl()
		desktop = app.desktop()

		# positioning the widget on the screen
		dheight = desktop.screenGeometry(desktop.primaryScreen()).height()
		dwidth = desktop.screenGeometry(desktop.primaryScreen()).width()
		if dwidth >= 1280:
			fac = 0.6
		else:
			fac = 0.9
		x = desktop.screenGeometry(desktop.primaryScreen()).x()
		y = desktop.screenGeometry(desktop.primaryScreen()).y()
		gui.move(x+(1.-fac)/2.*dwidth,y+(1.-fac)/2.*dheight)
		gui.resize(numpy.floor(dwidth*fac),numpy.floor(dheight*fac))

		# show the GUI
		gui.show()
		
		# if file supplied, open it
		if args.filename:
		 	if os.path.exists(args.filename):
				gui.loadObj(args.filename)
			else:
				argparser.error('Specified input file doesn\'t exist!')
				
		sys.exit(app.exec_())

	# start text mode
	else: 
	
		# text mode necessitates an input file
		if (not args.filename) or (not os.path.exists(args.filename)) :
			argparser.error('No input file supplied or specified file doesn\'t exist.')
			

		execfile(args.filename)


if __name__ == "__main__":
    main()
