import os
import iPlot
import iProcess
import numpy as np
from sharedFunctions import *
from types import SimpleNamespace


FORMAT = '''Model Number: (?P<modelNumber>.*)   
Serial Number: (?P<serialNumber>.*)
Firmware Version: (?P<firmwareVersion>.*)
Exposure Time: (?P<exposureTime>.*)
Data Taken on: (?P<dataTakenOn>.*)
Wavelength\tAmplitude
(?:(?P<wavelength>[0-9.]*)\t(?P<intensity>[0-9.-]*)\n)*$'''


def extractData(filePath: str):
    filePath = str(filePath)
    assert all([os.path.exists(filePath), os.path.isfile(filePath), filePath.endswith('.xls')]), \
        f'Path "{filePath}" does not exist or is not a ".xls" file.'
    match = matchDataFile(filePath, FORMAT)
    dataMetrics = match.groupdict()
    dataMetrics.pop('wavelength')
    dataMetrics.pop('intensity')
    wavelengths = np.array([float(v) for v in match.captures('wavelength')])
    intensities = np.array([float(v) for v in match.captures('intensity')])
    return wavelengths, intensities, SimpleNamespace(**dataMetrics)


def findIntensities(rawIntensities, blueSlice, redSlice, cfgMetrics):
    intensities = rawIntensities - cfgMetrics.bgIntensity
    intensities[blueSlice] /= cfgMetrics.blueAmplitude
    intensities[redSlice] /= cfgMetrics.redAmplitude
    intensities[np.intersect1d(blueSlice, redSlice)] = 0
    return intensities


def plotRaw(wavelengths, rawIntensities, title=None, name=None):
    plot = iPlot.Plot()
    plot.line(wavelengths, rawIntensities, format_='k')
    plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)


def plotArms(frequencies, intensities, blueSlice, redSlice, title=None, name=None):
    plot = iPlot.Plot()
    plot.line(frequencies[redSlice], intensities[redSlice], format_='tab:red')
    plot.line(frequencies[blueSlice], intensities[blueSlice], format_='tab:blue')
    plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)


def plotCfg(wavelengths, intensities, blueSlice, redSlice, cfgMetrics, title=None, name=None):
    plot = iPlot.Plot()
    plot.line(wavelengths[redSlice], intensities[redSlice], format_='tab:red')
    plot.line(wavelengths[blueSlice], intensities[blueSlice], format_='tab:blue')
    parameters = cfgMetrics.centerWavelength, 0, 1, cfgMetrics.blueFwhm, 1, cfgMetrics.redFwhm
    plot.line(wavelengths, halfGaussians(wavelengths, *parameters), format_='--k')
    plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)


def halfGaussians(values: np.ndarray, center, offset, amplitudeLeft, fwhmLeft, amplitudeRight, fwhmRight):
    leftSide = np.where(values <= center, amplitudeLeft * np.exp(-(values - center) ** 2 / (0.36062 * fwhmLeft ** 2)), 0)
    rightSide = np.where(values > center, amplitudeRight * np.exp(-(values - center) ** 2 / (0.36062 * fwhmRight ** 2)), 0)
    return leftSide + rightSide + offset
