from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gtdev.bladeDesignerXML import *
from gtdev.helper_methods import logger

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
        xml = BdXML(self.stagelist)
        xml.writeTurboMachineXML(self.identification)
        try:
            from bladedesigner import turboMachine
            import os
            compbd=turboMachine.turboMachine(os.path.abspath(self.identification))
            compbd.computeTurboMachine()
            compbd.displayViewer()
        except Exception as e:
            logger.error(e)
