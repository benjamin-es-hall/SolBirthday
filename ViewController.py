#! /Users/benhall/anaconda/envs/py35/bin/python
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu,
                             QSizePolicy, QGridLayout, QWidget,
                             QMessageBox, QPushButton, QCalendarWidget,
                             QFileDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from model import Pyprika
import numpy as np
import datetime as dt

print('LOADING VIEW...')

#class App(QMainWindow):
class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Your Sol Birthday - Developed by @BeshBashBosh'
        self.left, self.top = 10, 10
        self.width, self.height = 1600, 900

        # Initialise date to current date
        self.date = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)

        # Initialise the UI
        self.initUI()
        print('LOADED')

    def initUI(self):
        # Window size + Title
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        # Grid Layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Plot Canvas
        m = PlotCanvas(self)
        self.m = m

        # Load solar system
        print("PLOTTING ORBITS")
        self.sol = SolSystem()
        m.planetOrbit(self.sol)

        # Calendar selection
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.setDateRange(QtCore.QDate(1850,1,1), QtCore.QDate(2100,1,1))
        cal.clicked[QtCore.QDate].connect(self.selectDate)

        # Confirm, Exit, Save buttons
        confirmButton = QPushButton('Confirm', self)
        exitButton = QPushButton('Exit', self)
        saveButton = QPushButton('Save', self)

        # (widget, rowNo, colNo, GridRowSpan, GridColSpan)
        grid.addWidget(m, 0, 0, 100, 90)
        grid.addWidget(cal, 0, 90, 60, 10)
        grid.addWidget(confirmButton, 60, 91, 3,3)
        grid.addWidget(saveButton, 60, 94, 3,3)
        grid.addWidget(exitButton, 60, 97, 3,3)

        # Connect button to events
        confirmButton.clicked.connect(self.confirm)
        exitButton.clicked.connect(self.quit)
        saveButton.clicked.connect(self.save)

        # Show UI
        self.show()

    def confirm(self):
        print("Plotting position of planets on the date: {0}".format(self.date))
        self.m.resetFigure(self.sol)
        self.m.planetPositions(self.sol, self.date)

    def save(self):
        name, ext = QFileDialog.getSaveFileName(self, 'Save File',
                                           filter=self.tr('.png'))
        fn = name + ext
        self.m.saveFig(fn)
        print('File saved as: {0}'.format(fn))

    def quit(self):
         sys.exit()

    def selectDate(self, date):
        self.date = date.toString(QtCore.Qt.ISODate)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None):
        # Create figure instance
        self.figure = Figure()
        # Initialise FigureCanvas widget with figure
        FigureCanvas.__init__(self, self.figure)
        # Set parent widget
        self.setParent(parent)

        # Set up basic axes
        self.decorateAxes()

    # Set Up plotting canvas
    def decorateAxes(self):
        # Set figure canvas to black
        self.figure.set_facecolor('black')

        # Style axis for inner solar system bodies
        self.innerSystem = self.figure.add_subplot(111, projection='3d')
        self.plot3dEqualAspect(self.innerSystem, xlim=(-0.75,1),
                               ylim=(-0.75,1.5), zlim=(-1,1))
        self.innerSystem.view_init(25, 10)
        self.innerSystem.patch.set_facecolor('Black')
        self.innerSystem.set_axis_off()

        # Style axis for outer solar system bodies
        self.outerSystem = self.figure.add_subplot(326, projection='3d')
        self.plot3dEqualAspect(self.outerSystem, xlim=(-12,30),
                               ylim=(-26,18), zlim=(-40,40))
        self.outerSystem.view_init(25, 10)
        self.outerSystem.patch.set_facecolor('None')
        self.outerSystem.set_axis_off()

        # Reduce margins between axes
        self.figure.tight_layout()

        # Style axis for planet legend
        self.scaleLegend = self.figure.add_axes((0,0.92,1,0.08))
        self.scaleLegend.set_ylim(0,1)
        self.scaleLegend.patch.set_facecolor('None')
        self.scaleLegend.set_axis_off()

    # Method for plotting Planet orbits
    def planetOrbit(self, SolarSystem):
        for bodyLab, body in SolarSystem.bodies.items():
            ax = self.innerSystem if bodyLab in ['MERCURY', 'VENUS', 'EARTH', 'MARS'] else self.outerSystem

            ax.plot(body.orbitPosInAU[0][:,0], body.orbitPosInAU[0][:,1],
                    body.orbitPosInAU[0][:,2], '--', lw=1,
                    c=body.plotSymbolColor)

    # Method for plotting planet's positions at some selected date
    def planetPositions(self, SolarSystem, date):

        # Loop through bodies in the SolarSystem helper class
        for bodyLab, body in SolarSystem.bodies.items():
            # Treat Sun's position as unique case
            if bodyLab == 'SUN':
                # To scale Sun for inner system
                self.innerSystem.scatter(0, 0, 0, c=body.plotSymbolColor,
                                        s=SolarSystem.scaledPlotSymbol[bodyLab],
                                        label=body.customLabel)

                # Add label for Sun to inner solar system axis
                self.innerSystem.text(0.08,0.08,0.08, 'The Sun (Sol)',
                                      color=body.plotSymbolColor,
                                      fontweight='heavy')

                # Smaller Sun for outer solar system
                self.outerSystem.scatter(0, 0, 0, c=body.plotSymbolColor,
                                        s=SolarSystem.scaledPlotSymbol[bodyLab]*0.25)

            else:
                # Aside from selecting inner/outer system axis (done below)
                # can treat plotting of planetary bodies the same
                ax = self.innerSystem if bodyLab in ['MERCURY', 'VENUS', 'EARTH', 'MARS'] else self.outerSystem

                # Get position
                planetPos = body.getPos(time=date, frame='HCI',
                                        obs='SOLAR SYSTEM BARYCENTER')

                # Plot position
                ax.scatter(planetPos[0][:,0], planetPos[0][:,1],
                           planetPos[0][:,2],
                           c=body.plotSymbolColor,
                           s=SolarSystem.scaledPlotSymbol[bodyLab],
                           label=body.customLabel)

                # Add symbol to legend
                self.scaleLegend.scatter(np.log10(planetPos[1]), 0.5,
                                         c=body.plotSymbolColor,
                                         s=SolarSystem.scaledPlotSymbol[bodyLab]*0.5)

                # Add label to go with legend symbol for planets
                self.scaleLegend.text(np.log10(planetPos[1]), 0.05,
                                      body.customLabel,
                                      color=body.plotSymbolColor,
                                      fontweight='heavy', ha='center',
                                      va='center', rotation=40, )

        # Add symbol for the Sun last when axis limits have been
        # dynamically determined
        self.scaleLegend.scatter(self.scaleLegend.get_xlim()[0],0.5,
                                 c=SolarSystem.sun.plotSymbolColor,
                                 s=SolarSystem.scaledPlotSymbol['SUN'])


        # Add text to plot describing the date
        dateString = dt.datetime.strptime(date, '%Y-%m-%d').strftime('%a %B %d %Y')
        txtStr = 'The Solar System on:\n{0}'.format(dateString)
        txt = self.figure.text(0.05,0.05,txtStr, color='w',
                          fontsize=25, fontweight='heavy',ha='left')

        # Update the figure
        self.figure.canvas.draw()

    # Method for making an equal aspect ratio for 3D axes
    @staticmethod
    def plot3dEqualAspect(ax3D, xlim=(4,-4), ylim=(4,-4), zlim=(-4,4)):
        ax3D.set_xlim(xlim)
        ax3D.set_ylim(ylim)
        ax3D.set_zlim(zlim)
        scaling = np.array([getattr(ax3D, 'get_{}lim'.format(dim))()
                            for dim in 'xyz'])
        ax3D.auto_scale_xyz(*[[np.min(scaling), np.max(scaling)]]*3)

    # Method to reset figure canvas to starting condition
    def resetFigure(self, SolarSystem):
        self.figure.clf()
        self.decorateAxes()
        self.planetOrbit(SolarSystem)

    # Method for saving figure
    def saveFig(self, name):
        self.figure.savefig(name, dpi=300)

# Helper class for managing solar system of bodies
class SolSystem(object):

    def __init__(self, mkFile=None):
        # Set expected location for spice metakernel if custom not entered
        # TODO: Catch errors related to this kernel not being found
        if mkFile == None:
            mkFile = './assets/spice/metakernel.mk'

        # Generate planets
        self.sun = Pyprika.Planet(mk=mkFile,
                                  planetName='SUN',
                                  radiusInKilometers=695700,
                                  orbPeriodInEarthYears=1,
                                  plotSymbolColor='#ffd000')

        self.mercury = Pyprika.Planet(mk=mkFile,
                                      planetName='MERCURY BARYCENTER',
                                      radiusInKilometers=2440.,
                                      orbPeriodInEarthYears=87.97/365.26,
                                      plotSymbolColor='#aa9e91',
                                      customLabel='MERCURY')

        self.venus = Pyprika.Planet(mk=mkFile,
                                    planetName='VENUS BARYCENTER',
                                    radiusInKilometers=6052.,
                                    orbPeriodInEarthYears=224.7/365.26,
                                    plotSymbolColor='#f2b94f',
                                    customLabel='VENUS')

        self.earth = Pyprika.Planet(mk=mkFile,
                                    planetName='EARTH BARYCENTER',
                                    radiusInKilometers=6378.,
                                    orbPeriodInEarthYears=1.,
                                    plotSymbolColor='#02721e',
                                    customLabel='EARTH')

        self.mars = Pyprika.Planet(mk=mkFile,
                                   planetName='MARS BARYCENTER',
                                   radiusInKilometers=3396.,
                                   orbPeriodInEarthYears=1.88,
                                   plotSymbolColor='#cc2504',
                                   customLabel='MARS')

        self.jupiter = Pyprika.Planet(mk=mkFile,
                                      planetName='JUPITER BARYCENTER',
                                      radiusInKilometers=71492.,
                                      orbPeriodInEarthYears=11.86,
                                      plotSymbolColor='#c18503',
                                      customLabel='JUPITER')

        self.saturn = Pyprika.Planet(mk=mkFile,
                                     planetName='SATURN BARYCENTER',
                                     radiusInKilometers=60268.,
                                     orbPeriodInEarthYears=29.46,
                                     plotSymbolColor='#e0c147',
                                     customLabel='SATURN')

        self.uranus = Pyprika.Planet(mk=mkFile,
                                     planetName='URANUS BARYCENTER',
                                     radiusInKilometers=25559.,
                                     orbPeriodInEarthYears=84.01,
                                     plotSymbolColor='#2dc49c',
                                     customLabel='URANUS')

        self.neptune = Pyprika.Planet(mk=mkFile,
                                      planetName='NEPTUNE BARYCENTER',
                                      radiusInKilometers=24764.,
                                      orbPeriodInEarthYears=164.79,
                                      plotSymbolColor='#1ebfdb',
                                      customLabel='NEPTUNE')

        self.pluto = Pyprika.Planet(mk=mkFile,
                                    planetName='PLUTO BARYCENTER',
                                    radiusInKilometers=1195.,
                                    orbPeriodInEarthYears=248.59,
                                    plotSymbolColor='#f1c9a2',
                                    customLabel='PLUTO')

        # Store solar system bodies in look-up dictionary
        self.bodies = {self.sun.customLabel: self.sun,
                        self.mercury.customLabel: self.mercury,
                        self.venus.customLabel: self.venus,
                        self.earth.customLabel: self.earth,
                        self.mars.customLabel: self.mars,
                        self.jupiter.customLabel: self.jupiter,
                        self.saturn.customLabel: self.saturn,
                        self.uranus.customLabel: self.uranus,
                        self.neptune.customLabel: self.neptune,
                        self.pluto.customLabel: self.pluto}

        # Create dictionary lookup table for scaled plot symbols
        # Pluto will be made not to scale since it is so tiny.

        # Define 'private' function for min-max scaling
        def __scale(ps, top=200):
            ps = np.log10(ps)
            ps = top*((ps - ps.min()) / (ps.max() - ps.min()))
            ps[ps == 0] = ps[ps > 0].min() * (2./3.)
            return ps

        # Scale size of planets using min-max scaler
        sizes = __scale(np.array([self.sun.radiusInKilometers,
                          self.mercury.radiusInKilometers,
                          self.venus.radiusInKilometers,
                          self.earth.radiusInKilometers,
                          self.mars.radiusInKilometers,
                          self.jupiter.radiusInKilometers,
                          self.saturn.radiusInKilometers,
                          self.uranus.radiusInKilometers,
                          self.neptune.radiusInKilometers,
                          self.pluto.radiusInKilometers]), top=200)

        # Add sizes to look-up disctionary
        self.scaledPlotSymbol = {self.sun.customLabel: sizes[0],
                                 self.mercury.customLabel: sizes[1],
                                 self.venus.customLabel: sizes[2],
                                 self.earth.customLabel: sizes[3],
                                 self.mars.customLabel: sizes[4],
                                 self.jupiter.customLabel: sizes[5],
                                 self.saturn.customLabel: sizes[6],
                                 self.uranus.customLabel: sizes[7],
                                 self.neptune.customLabel: sizes[8],
                                 self.pluto.customLabel: sizes[9]}


def run():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
