import numpy as np
import os
import iPlot
from types import SimpleNamespace
from sharedFunctions import *

FORMAT = '(?:(?P<wavelength>[0-9.]*)\t(?P<intensity>[0-9.-]*)\n)+$'
RAMAN_CONSTANTS = {
    'O2': SimpleNamespace(probeWavelength=398.09, maskSpan=1, b=1.423, d=4.7E-6, jStart=3, jStep=2, thermalRange=(5, 21)),
    'N2-20210303': SimpleNamespace(probeWavelength=398, maskSpan=1.2, b=1.98, d=6E-6, jStart=3, jStep=1, thermalRange=(4, 21)),
    'N2-20210211': SimpleNamespace(probeWavelength=397.97, maskSpan=1.2, b=1.97, d=6E-6, jStart=3, jStep=1, thermalRange=(4, 21)),
    'N2-20210128': SimpleNamespace(probeWavelength=397.96, maskSpan=1.2, b=1.96, d=5E-6, jStart=3, jStep=1, thermalRange=(4, 21)),
    'N2-20210310': SimpleNamespace(probeWavelength=398.04, maskSpan=1.2, b=1.96, d=5E-6, jStart=3, jStep=1, thermalRange=(4, 21)),
    'N2-20210320': SimpleNamespace(probeWavelength=398, maskSpan=1.2, b=1.962, d=5E-6, jStart=3, jStep=1, thermalRange=(4, 21))
}


def extractData(filePath: str):
    filePath = str(filePath)
    assert all([os.path.exists(filePath), os.path.isfile(filePath), filePath.endswith('.txt')]), \
        f'Provided path "{filePath}" does not exist or is not a ".txt" file.'
    match = matchDataFile(filePath, FORMAT)
    wavelengths = np.array([float(v) for v in match.captures('wavelength')])
    intensities = np.array([float(v) for v in match.captures('intensity')])
    return wavelengths, intensities


def findPopulations(intensities, boundIndices, js, constants):
    populations = np.array(
        [np.trapz(intensities[boundIndices[i]: boundIndices[i + 1]]) for i in range(len(js))])
    meanThermalPopulation = meanPopulation(populations, js, range(*constants.thermalRange))
    populations /= meanThermalPopulation
    return np.maximum(populations, 0)


def meanPopulation(populations, js, meanJs):
    indices = np.where([j in meanJs for j in js])
    return np.mean(populations[indices])


def plotRaw(rawWavelengths, rawIntensities, title=None, name=None):
    plot = iPlot.Plot()
    plot.line(rawWavelengths, rawIntensities, format_='k')
    plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)


def plotRaman(frequencies, intensities, bounds, js, title=None, name=None):
    labelPositions = [(a + b) / 2 for a, b in zip(bounds, bounds[1:])]
    plot = iPlot.Plot()
    plot.line(frequencies, intensities, format_='k')
    plot.line(bounds, np.full_like(bounds, 0), format_='|g', markerSize=10)
    plot.annotate(js, labelPositions, np.zeros_like(js), offset=(0.6, -9), rotation=90, fontSize=6)
    plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)


def plotPopulation(js, populations, title=None, name=None):
    plot = iPlot.Plot()
    plot.bar(js, populations, width=0.8)
    plot.show(xlabel='J State', ylabel='Population (a.u.)', grid=True, title=title, name=name)
