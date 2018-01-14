"""
Pyprika

Author: Benjamin E. S. Hall, Jul 2017

Purpose: Functions to calculate spacecraft ephemerides using the
         NASA NAIF SPICE library.


pyVersion: 3.5.2
SpiceyPy Version: 2.0.0
SPICE TOOLKIT Version: CSPICE_N0066

Comments:
    Requires the brilliant Python implementation of NASA NAIF SPICE toolkit
    called spiceypy package by Andrew Annex.
    (see https://github.com/AndrewAnnex/SpiceyPy for source)
    (see http://spiceypy.readthedocs.io/en/master/ for docs)
    (MAKE SURE TO CITE THEM!)

Contains:

TODO:
    Complete basic documentation

Version History:
    v0.1 -> Creation -> Jul 2017
    v0.1branch -> Minimisation for SolBirthday -> Jan 2018

"""

## Future import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


## Module Dunders
__package__ = "spice"
__name__ = "Pyprika"
__author__ = "Benjamin E. S. Hall"
__copyright__ = "Copyright 2017, Benjamin E. S. Hall"
__version__ = "0.1branch"


## Imports
import time
import sys
import spiceypy as spice

import pkg_resources

import numpy as np
import matplotlib.pyplot as plt

import datetime as dt

# Base spice class for kernel management
class SpiceBase(object):
    """class docstring"""
    def __init__(self):
        super(SpiceBase, self).__init__()

        # Set SpiceyPy version number being used
        self.versions = dict(SpiceyPy = pkg_resources.get_distribution("spiceypy").version,
                    NAIF = spice.tkvrsn('TOOLKIT'))

    # Method for checking what kernels are loaded
    @staticmethod
    def loadedKernels(kType=None, print_or_return="p"):
        """function description"""
        if not kType: kType = "all"

        # Get number of kernels loaded
        ktot = spice.ktotal(kType)

        # Now print them all
        kerns = []
        if ktot > 0:
            kerns = [spice.kdata(k,kType,255,255,255)[0] for k in range(ktot)]

        if print_or_return == "p":
            print ('{:d} {:s} kernels loaded:'.format(ktot,kType.upper()))
            for k in kerns: print(k)
        elif print_or_return == "r":
            return kerns

    # Method for checking if specific kernel loaded
    @staticmethod
    def checkKernelLoad(kern):
        """docstring"""
        try:
            #a = 1./num
            spice.kinfo(kern)
            return True
        except spice.stypes.SpiceyError:
            return False

    # Method for clearing the loaded kernel pool
    @staticmethod
    def clearKernPool():
        spice.kclear()

    # Method for checking for duplicate kernels
    @classmethod
    def checkDuplicates(cls, kern):
        # One-liner below (-1 to not include the `original`)
        return cls.loadedKernels("all", print_or_return="r").count(kern) - 1

    # Method for removing specific/duplicate kernels
    @classmethod
    def removeKernel(cls, kern, rmDupsOnly=False):
        # Determine number of times kernel is loaded
        nDups = cls.checkDuplicates(kern)
        if rmDupsOnly:
            # only want to remove duplicates
            if nDups > 0:
                # recursively remove
                # NOTE: I wouldn't like to say where in the full kernel last
                # the last one remaining will be
                spice.unload(kern)
                cls.removeKernel(kern, rmDupsOnly=rmDupsOnly)
        else:
            if nDups >= 0:
                # recursively remove
                spice.unload(kern)
                cls.removeKernel(kern)

    # Method for loading/reloading specific kernels
    @classmethod
    def loadKernel(cls, kern=None, reloadKern=False):
        # Check if input kernel is loaded already
        isLoaded = cls.checkKernelLoad(kern)

        # Do some checks and clean up if it is loaded
        if not isLoaded:
            # not loaded, load kernel
            spice.furnsh(kern)
        else:
            # kernel already lodade
            # - check for duplcites
            # - remove all instances of kernel and reload (reloadKern)
            # - remove all but one instance of kernel (not reloadKern)
            if reloadKern:
                # all instances, dups or otherwise will be removed
                cls.removeKernel(kern, rmDupsOnly=False)
                # reload
                spice.furnsh(kern)
            else:
                # Kernel will not be reloaded, but its final position in
                # the kernel list is uncertain.
                cls.removeKernel(kern, rmDupsOnly=True)

    # method for getting the NAID ID for a body
    @staticmethod
    def naifID(bodyStr):
        try:
            naifID = spice.bodn2c(bodyStr.upper())
            return naifID
        except spice.stypes.SpiceyError as e:
            print("ERROR: INVALID SPICE NAIF NAME ENTERED")
            raise e

    # method for getting the NAIF name of a body
    @staticmethod
    def naifName(bodyInt):
        try:
            naifName = spice.bodc2n(bodyInt)
            return naifName
        except spice.stypes.SpiceyError as e:
            print("ERROR: INVALID SPICE NAIF ID ENTERED")
            raise e

# Planet class that inherits kernel management
class Planet(SpiceBase):
    """class docstring"""
    def __init__(self, mk, planetName=None, planetID=None,
                 radiusInKilometers=None,
                 orbPeriodInEarthYears=None, plotSymbolColor=None, customLabel=None):
        super(Planet, self).__init__()

        # Construct proper NAIF IDs and NAMES
        if (planetName == None) and (planetID == None):
            raise TypeError("Please initialise with a NAIF planetName (string)"
                            "**OR** NAIF planetID (int)\n"
                            "e.g. planetName = 'MARS' OR planetID = '499'")
        elif (planetName != None) and (planetID != None):
                raise TypeError("Please only enter a NAIF planetName **OR**"
                                " a NAIF planetID")
        elif planetName != None:
            self.ID = self.naifID(planetName)
            self.Name = self.naifName(self.ID)
        elif planetID != None:
            self.Name = self.naifName(planetID)
            self.ID = self.naifID(self.Name)

        # Store radius and orbPeriod
        self.radiusInKilometers = radiusInKilometers
        self.orbPeriodInEarthYears = orbPeriodInEarthYears

        # Load some base SPICE kernels to be able to do some useful stuff
        # TODO: Catch error but could be more cleanly
        # dealt with
        try:
            self.loadKernel(mk, reloadKern=True)
        except spice.stypes.SpiceyError:
            print('Spice metakernal cannot be located or contents failed to load')
            print('Exiting...')
            sys.exit()

        # Calculate orbit positions about sun in HCI frame
        self.orbitPosInAU = self.getOrbit()

        # Set plot icon colour and custom label
        # ternary a = b if True else c
        self.plotSymbolColor = plotSymbolColor if not plotSymbolColor == None else 'k'
        self.customLabel = customLabel if not customLabel == None else self.Name


    # Method for getting position for input
    # datetime (converted internally to ephermeris)
    # Return tuple with position in frames and distance from Sun
    def getPos(self, time, frame='HCI', obs='SUN'):
        # TODO: Error checking for valid observer name, frame name, input time is a datetime

        # Convert input datetime to string and parse to ephemeris time
        et = self.__convertDateToET(time)
        return (spice.spkpos(targ=str(self.ID), et=et,
                            ref=frame, abcorr='NONE',
                            obs=str(self.naifID(obs)))[0] / 149.6e+6, self.__solDistanceInAU(et)/149.6e+6)

    # Method for calculating orbital geometry
    # requires correct spice kernels covering
    # long enough period of orbital body
    def getOrbit(self):

        # Start time (set early enough to account for
        # long period orbits such as outer planets)
        ts = dt.datetime(1850,1,1)

        # End time
        te = (ts +
              dt.timedelta(days=self.orbPeriodInEarthYears * 365.26))

        # Calculate time step in terms of fractional days
        # to give 1000 steps throughout orbit
        tDelta = (te - ts).days/1000.

        # Calculate orbital period from ts->te in tDelta
        # time steps.
        year = np.arange(ts, te, dt.timedelta(days=tDelta))

        # Now get orbital positions throughout year in
        # terms of Astronomical units
        return self.getPos(time=year, frame='HCI',
                           obs='SOLAR SYSTEM BARYCENTER')

    # Private method for converting datetime to
    # spice ephemeris time
    # TODO: Check for datetime as input
    def __convertDateToET(self, time):
        return [spice.str2et(t) for t in np.array(time, dtype='|S26', ndmin=1)]

    # Private method for calculating the distance
    # from the sun in AU. Method used as part of getPos
    def __solDistanceInAU(self, et):
        return np.sqrt(np.sum(spice.spkezr(str(self.ID), et[0],
                                           'J2000','NONE','SUN')[0][0:3]**2.))
