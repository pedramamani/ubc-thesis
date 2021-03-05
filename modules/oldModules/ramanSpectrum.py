import regex
import os
import numpy as np
import iPlot
import iProcess
from iConstants import *

FORMAT = '(?:(?P<wavelength>[0-9.]*)\t(?P<intensity>[0-9.-]*)\n)+$'

ROTATIONAL_CONSTS = {'N2': 1.98, 'O2': 1.427}  # cm⁻¹
CENTRIFUGAL_CONSTS = {'N2': 6E-6, 'O2': 5E-6}  # cm⁻¹
THERMAL_RANGES = {'N2': (4, 21), 'O2': (5, 20)}  # J state

PROBE_WL = 398  # nm
CENTER_MASK_EXTENT = 1.1  # nm
TRIM_PADDING = 20  # count
INTENSITY_SCALING = 1E4


class RamanSpectrum:
    def __init__(self, filePath: str, molecule: str = None, control: 'RamanSpectrum' = None):
        filePath = str(filePath)
        assert all([os.path.exists(filePath), os.path.isfile(filePath), filePath.endswith('.txt')]), \
            f'Provided path "{filePath}" does not exist or is not a ".txt" file.'
        assert (molecule is not None) or (control is not None), 'Need Raman molecule or control spectrum.'
        with open(filePath, 'r') as file:
            content = file.read()
        match = regex.match(FORMAT, content)
        assert match is not None, f'Data file "{filePath}" contents have an unknown format.'

        self.wavelengths = np.array([float(v) for v in match.captures('wavelength')])
        self.intensities = np.array([float(v) for v in match.captures('intensity')]) / INTENSITY_SCALING
        self.intensities[self._sliceCenter(PROBE_WL, CENTER_MASK_EXTENT)] = 0

        if control is None:
            self.params = {'molecule': molecule}
            self._trimSlice = self._calcTrimSlice()
            self.wavelengths = self.wavelengths[self._trimSlice]
            self.intensities = self.intensities[self._trimSlice]
            self._blueSlice = self._slice(upperWavelength=PROBE_WL)
            self._redSlice = self._slice(lowerWavelength=PROBE_WL)

            self.freqs = PHYS.c * (1 / self.wavelengths - 1 / PROBE_WL) / (PRE.n * PRE.T) / 2
            self.rotFreqsTheory = self._calcRotFreqsTheory()
            self.rotJs, self.rotFreqs, self.rotIntensities, self.rotPops = self._calcRots()

            self.params['thermal'] = self.meanPop(range(*THERMAL_RANGES[self.params['molecule']]))
        else:
            self.params = control.params.copy()
            self.wavelengths = self.wavelengths[control._trimSlice]
            self.intensities = self.intensities[control._trimSlice]
            self._blueSlice = control._blueSlice
            self._redSlice = control._redSlice

            self.freqs = PHYS.c * (1 / self.wavelengths - 1 / PROBE_WL) / (PRE.n * PRE.T) / 2
            self.rotFreqsTheory = control.rotFreqsTheory
            self.rotJs, self.rotFreqs, self.rotIntensities, self.rotPops = self._calcRots()

            self.params['thermal'] = self.meanPop(range(*THERMAL_RANGES[self.params['molecule']]))

            scaleFactor = control.params['thermal'] / self.params['thermal']
            self.intensities *= scaleFactor
            self.rotIntensities *= scaleFactor

    def plot(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.line(self.wavelengths, self.intensities, format_='-k')
        plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', title=title, grid=True, name=name)
        return self

    def plotSides(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.line(np.abs(self.freqs[self._redSlice]), self.intensities[self._redSlice], format_='tab:red')
        plot.line(self.freqs[self._blueSlice], self.intensities[self._blueSlice], format_='tab:blue')
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', legend=['Stokes', 'anti-Stokes'], title=title, grid=True, name=name)
        return self

    def plotPops(self, title=None, name=None, showTheory=False):
        plot = iPlot.Plot()
        plot.line(np.abs(self.freqs[self._redSlice]), self.intensities[self._redSlice], format_='tab:red')
        plot.annotate(self.rotJs, self.rotFreqs, self.rotIntensities, offset=(0, 3), fontSize=5)
        if showTheory:
            plot.line(self.rotFreqsTheory, np.full_like(self.rotFreqsTheory, 0), format_='|g', markerSize=10)
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', title=title, grid=True, name=name)
        return self

    def meanPop(self, js):
        inRange = [j in js for j in self.rotJs]
        indices = np.where(inRange)
        return np.mean(self.rotPops[indices])

    def _calcRotFreqsTheory(self):
        b, d = ROTATIONAL_CONSTS[self.params['molecule']] / PRE.c, CENTRIFUGAL_CONSTS[self.params['molecule']] / PRE.c
        jMax = (np.max(np.abs(self.freqs)) * PRE.T / (b * PHYS.c) - 6) / 2 + 3
        js = np.arange(jMax)
        energiesTheory = (b * js * (js + 1) - d * js ** 2 * (js + 1) ** 2) * PHYS.c / PRE.T
        return -(energiesTheory[:-2] - energiesTheory[2:]) / 2

    def _calcRots(self):
        freqs, intensities = -self.freqs[self._redSlice], self.intensities[self._redSlice]
        peakIndices = iProcess.indexPeaks(intensities, distance=3, prominence=0.004)
        rotJs, rotFreqs, rotIntensities, rotPops = [], [], [], []

        for peakIndex in peakIndices:
            j = np.argmin(np.abs(self.rotFreqsTheory - freqs[peakIndex]))
            if j not in rotJs:
                rotJs.append(j)
                rotFreqs.append(freqs[peakIndex])
                rotIntensities.append(intensities[peakIndex])
                rotPops.append(np.mean(self.intensities[peakIndex - 1: peakIndex + 2]))
        return np.array(rotJs), np.array(rotFreqs), np.array(rotIntensities), np.array(rotPops)

    def _calcTrimSlice(self):
        threshold = np.max(self.intensities) / 1E2
        startIndex, endIndex = 0, len(self.wavelengths)
        while self.intensities[startIndex] < threshold: startIndex += 1
        while self.intensities[endIndex - 1] < threshold: endIndex -= 1

        centerIndex = np.argmin(np.abs(self.wavelengths - PROBE_WL))
        startIndex = np.clip(startIndex - TRIM_PADDING, 0, centerIndex)
        endIndex = np.clip(endIndex + TRIM_PADDING, centerIndex, len(self.wavelengths))
        return slice(startIndex, endIndex)

    def _slice(self, lowerWavelength: float = None, upperWavelength: float = None) -> slice:
        startIndex = None if lowerWavelength is None else np.argmin(np.abs(self.wavelengths - lowerWavelength))
        endIndex = None if upperWavelength is None else np.argmin(np.abs(self.wavelengths - upperWavelength))
        return slice(startIndex, endIndex)

    def _sliceCenter(self, centerWavelength: float, wavelengthSpan: float) -> slice:
        return self._slice(centerWavelength - wavelengthSpan / 2, centerWavelength + wavelengthSpan / 2)


if __name__ == '__main__':
    raman = RamanSpectrum('C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-01-28 N2/0.txt', 'N2')
    raman.plotPops()
