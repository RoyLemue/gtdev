from PyQt4.QtCore import *
from PyQt4.QtGui import *
import bladeDesignerXML


class BladeDesignerThread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self, parent)
        self.exiting = False
         
    def __del__(self):
        self.exiting = True
        self.wait()
        
    def startCalculating(self,_stagelist,_ident):
        self.stagelist = _stagelist
        self.identification = _ident
        self.start()
        
    def run(self):
        xml=bladeDesignerXML.BdXML(self.stagelist)
        xml.writeTurboMachineXML(self.identification)
        try:
            from bladedesigner import turboMachine
            import os
            compbd=turboMachine.turboMachine(os.path.abspath(self.identification))
            compbd.computeTurboMachine()
            compbd.displayViewer()
        except:
            print "Ein Fehler ist aufgetreten. Ist der BladeDesigner installiert und richtig importiert?"
