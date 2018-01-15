#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===============================================================================
# Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines
# Institute for Flight Propulsion, TU Munich
# Author: Sebastian G. Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl
# Published under the Terms of GNU public licence v3
# ===============================================================================

import math
import sys
from gtdev import helper_methods

if sys.version_info[0] == 2:
    from ConfigParser import ConfigParser, RawConfigParser
elif sys.version_info[0] == 3:
    from configparser import ConfigParser, RawConfigParser


# abstract class for any turbomachine object - provides methods for communication and initialization
# Inheritated by any system-defining class
class AbstractTurbo(object):
    def __init__(self, ident_):
        # Name of the object (e.g. Projectname, component name.. )

        self.type = 'AbstractTurbo'
        self.identification = ident_

        # Parameter-Lists:
        # Each List-Entry is defined by a List of 3 Strings:
        # ["Variable Name","Unit","Description"]

        # List of parameters relevant for calcThermo()
        self.thermoInputParams = []
        self.thermoOuputParams = []

        # List of parameters relevant for calcAero()
        self.aeroInputParams = []
        self.aeroOutputParams = []

        # Dictionary of sub components (AbstractTurbo-objects)
        self.subcomponentList = []
        self.modularSubfunctionList = []

    # returns the program header as a string
    def getHeader(self):
        header = \
            " Gas Turbine Developer (c) Hummingbird - TUM Gas Turbines\n" + \
            " Institute for Flight Propulsion, TU Munich\n" + \
            " Authors: Sebastian Barthmes, Sebastian Brehm, Jan Matheis, Peter Schöttl\n" + \
            " Published under the Terms of GNU Public Licence v3\n"
        return header

    def printEverything(self):
        print(self.getHeader())
        self.printThermo()
        self.printAero()

    def printThermo(self):
        helper_methods.logHeader("Thermodynamics")
        helper_methods.logModule(self.identification)
        helper_methods.logPlain(" * Input :")
        self.printDict(self.getThermoInputDict())
        helper_methods.logPlain(" | * Output :")
        self.printDict(self.getThermoOutputDict())
        for component in self.subcomponentList:
            # TODO insert Values?
            helper_methods.logPlain(" * Input :")
            self.printDict(component[1].getThermoInputDict())
            helper_methods.logPlain(" | * Output :")
            self.printDict(component[1].getThermoOutputDict())

    def printAero(self):
        helper_methods.logHeader("Aerodynamics")
        helper_methods.logModule(self.identification)
        helper_methods.logPlain(" * Input :")
        self.printDict(self.getAeroInputDict())
        helper_methods.logPlain(" | * Output :")
        self.printDict(self.getAeroOutputDict())
        for component in self.subcomponentList:
            helper_methods.logger.info("" + component[1].identification, ":")
            helper_methods.logPlain(" * Input :")
            self.printDict(component[1].getAeroInputDict())
            helper_methods.logPlain(" | * Output :")
            self.printDict(component[1].getAeroOutputDict())

    # Converts any dictionary to a string (useful for output)
    def getDictAsString(self, dict_):
        dictstring = ""
        for key in sorted(dict_):
            if dict_[key][1] == "rad":
                if dict_[key][0] != None:
                    value = str(180.0 / math.pi * dict_[key][0])
                else:
                    value = "None"
                unit = "deg"
            else:
                value = str(dict_[key][0])
                unit = dict_[key][1]
            dictstring += " |--" + (key + " = ").rjust(15) + value + " " + unit + "\n"
        dictstring = dictstring[:-1]
        # for i in range(len(dict_.keys())):
        # if dict_.values()[i][1]=="rad":
        # if dict_.values()[i][0]!=None:
        # value=str(180.0/math.pi*dict_.values()[i][0])
        # else:
        # value="None"
        # unit="deg"
        # else:
        # value=str(dict_.values()[i][0])
        # unit=dict_.values()[i][1]
        # dictstring+=" |--"+(dict_.keys()[i]+" = ").rjust(15)+value+" "+unit+"\n"
        # dictstring=dictstring[:-1]
        return dictstring

    # Set-Method for setting up global variables from any dictionary
    def setVariablesFromDict(self, dict_):
        for n in range(len(dict_.keys())):
            try:
                setattr(self, dict_.keys()[n], dict_.values()[n][0])
            except TypeError:
                setattr(self, dict_.keys()[n], dict_.values()[n])

    # Set-Method for setting up global variables from 2d-lists
    def setVariablesFromList(self, list_):
        for n in range(len(list_)):
            setattr(self, list_[n][0], list_[n][1])

    # modifies In- and Output of any AbstractTurbo-Object by removing parameters from input lists and adding it to the output list (useful for subcomponent handling)
    def removeComputedParams(self, obj, thermop, aerop):
        for rparam in thermop:
            for item in obj.thermoInputParams:
                if rparam in item:
                    obj.thermoOutputParams.append(item)
                    obj.thermoInputParams.remove(item)
                    break
        for rparam in aerop:
            for item in obj.aeroInputParams:
                if rparam in item:
                    obj.aeroOutputParams.append(item)
                    obj.aeroInputParams.remove(item)
                    break

    # prints a dictionary in a better way
    def printDict(self, dict_):
        if dict_ != {}:  # and not [k for k, v in dict_.iteritems() if v == None]:
            helper_methods.logPlain(self.getDictAsString(dict_))
        else:
            helper_methods.logPlain(" |\n |--\tN/A")

    # gets the subcomponent dictionary and returns False in case of empty
    def getSubcomponentList(self):
        if self.subcomponentList == []:
            return False
        else:
            return self.subcomponentList

    # builds a dictionary from global variables which names are saved in a given list
    def buildDictFromList(self, list_):
        d = {}
        for i in range(len(list_)):
            value = getattr(self, list_[i][0])
            unit = list_[i][1]
            desc = list_[i][2]
            d.update({
                "'" + list_[i][0] + "'": [str(value), "'" + unit + "'", "'" + desc + "'"]
            })
        setattr(self, "bdict", d)
        return d

    # initializes a list of strings to global variables with type None
    def initialize(self, list_):
        for n in range(len(list_)):
            setattr(self, list_[n][0], None)

    # checks the type of global variables given in a list
    def check(self, list_):
        fails = ""
        for n in range(len(list_)):
            a = getattr(self, list_[n][0], None)
            if a == None:
                fails += " " + list_[n][0]
            elif math.isnan(a):
                raise Exception(list_[n][0] \
                                + " has wrong result 'nan'! Probably there is no solution for the given boundary conditions.")
        if fails != "":
            raise Exception("The following parameters were not set/computed in " + self.identification + ":" + fails)

    ## Get-methods for dictionaries

    def getThermoInputDict(self):
        tdict = self.buildDictFromList(self.thermoInputParams)
        return tdict

    def getThermoOutputDict(self):
        tdict = self.buildDictFromList(self.thermoOutputParams)
        return tdict

    def getAeroInputDict(self):
        tdict = self.buildDictFromList(self.aeroInputParams)
        return tdict

    def getAeroOutputDict(self):
        tdict = self.buildDictFromList(self.aeroOutputParams)
        return tdict

    def saveObject(self, _filename):
        configparser = ConfigParser()
        configparser.optionxform = str
        configparser.add_section('general')
        configparser.set('general', 'type', self.type)
        configparser.set('general', 'identification', self.identification)
        configparser.add_section(self.identification)
        for k, l in self.getThermoInputDict().iteritems():
            configparser.set(self.identification, k, l[0])
        for k, l in self.getAeroInputDict().iteritems():
            configparser.set(self.identification, k, l[0])
        for k, l in self.getThermoOutputDict().iteritems():
            configparser.set(self.identification, k, l[0])
        for k, l in self.getAeroOutputDict().iteritems():
            configparser.set(self.identification, k, l[0])
        for i in self.subcomponentList:
            dummy = getattr(self, i[0])
            configparser.add_section(dummy.identification)
            for k, l in dummy.getThermoInputDict().iteritems():
                configparser.set(dummy.identification, k, l[0])
            for k, l in dummy.getAeroInputDict().iteritems():
                configparser.set(dummy.identification, k, l[0])
            for k, l in dummy.getThermoOutputDict().iteritems():
                configparser.set(dummy.identification, k, l[0])
            for k, l in dummy.getAeroOutputDict().iteritems():
                configparser.set(dummy.identification, k, l[0])
        with open(_filename, 'wb') as configfile:
            configparser.write(configfile)

    def loadObject(self, _filename):
        configparser = RawConfigParser()
        configparser.optionxform = str
        configparser.read(_filename)

        for i in self.thermoInputParams + self.thermoOutputParams + self.aeroInputParams + self.aeroOutputParams:
            try:
                setattr(self, i[0], configparser.get(self.identification, i[0]))
            except configparser.NoSectionError as detail:
                helper_methods.logger.error(detail)
            except configparser.NoOptionError as detail:
                helper_methods.logger.error(detail)
        for i in self.subcomponentList:
            dummy = getattr(self, i[0])
            for k in dummy.thermoInputParams + dummy.thermoOutputParams + dummy.aeroInputParams + dummy.aeroOutputParams:
                try:
                    setattr(dummy, k[0], configparser.get(dummy.identification, k[0]))
                    setattr(self, i[0], dummy)
                except configparser.NoSectionError as detail:
                    helper_methods.logger.error(detail)
                except configparser.NoOptionError as detail:
                    helper_methods.logger.error(detail)
