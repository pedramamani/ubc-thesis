import regex
import os
import numpy as np
import iPlot
import iProcess
from iConstants import *
from raman import Raman

ROTATIONAL_CONSTS = {'N2': 1.98, 'O2': 1.427}  # cm⁻¹
CENTRIFUGAL_CONSTS = {'N2': 6E-6, 'O2': 5E-6}  # cm⁻¹
THERMAL_RANGES = {'N2': (4, 21), 'O2': (5, 20)}  # J state

PROBE_WL = 398  # nm
CENTER_MASK_EXTENT = 1.1  # nm
TRIM_PADDING = 20  # count
TRIM_THRESHOLD_FACTOR = 1E-2


class RamanControl:
    def __init__(self, filePath: str, molecule: str):
        Raman(filePath)

        self._b, self._d, self._thermalRange = ROTATIONAL_CONSTS[molecule] / PRE.c, CENTRIFUGAL_CONSTS[molecule] / PRE.c, THERMAL_RANGES[molecule]
        self._centerSlice = self._getCenteredSlice(PROBE_WL, CENTER_MASK_EXTENT)
        self._trimmedSlice = self._getTrimmedSlice()

        self.intensities[self._centerSlice] = 0
        self.wavelengths = self.wavelengths[self._trimmedSlice]
        self.intensities = self.intensities[self._trimmedSlice]
        self._blueSlice = self._getSlice(stopWavelength=PROBE_WL)
        self._redSlice = self._getSlice(startWavelength=PROBE_WL)

        self.freqs = PHYS.c * (1 / self.wavelengths - 1 / PROBE_WL) / (PRE.n * PRE.T) / 2
        self.rotFreqsTheory = self._calcRotFreqsTheory()

        self.rotJs, self.rotFreqs, self.rotIntensities, self.rotPops = self._calcRots()
        scaleFactor = self.meanPop(range(*self._thermalRange))
        self.intensities /= scaleFactor
        self.rotIntensities /= scaleFactor
        self.rotPops /= scaleFactor

    def plotSides(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.line(np.abs(self.freqs[self._redSlice]), self.intensities[self._redSlice], format_='tab:red')
        plot.line(self.freqs[self._blueSlice], self.intensities[self._blueSlice], format_='tab:blue')
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', legend=['Stokes', 'anti-Stokes'], title=title, grid=True, name=name)
        return self

    def plotPops(self, title=None, name=None, showTheory=False):
        plot = iPlot.Plot()
        plot.line(np.abs(self.freqs[self._redSlice]), self.intensities[self._redSlice], format_='tab:red')
        plot.annotate(self.rotJs, self.rotFreqs, self.rotIntensities, offset=(0, 3), fontSize=6)
        if showTheory:
            plot.line(self.rotFreqsTheory, np.full_like(self.rotFreqsTheory, 0), format_='|g', markerSize=10)
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', title=title, grid=True, name=name)
        return self

    def meanPop(self, js):
        contained = [j in js for j in self.rotJs]
        indices = np.where(contained)
        return np.mean(self.rotPops[indices])

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
                rotPops.append(np.mean(self.intensities[peakIndex - 3: peakIndex + 4]))  # average 7 intensities around peak
        return np.array(rotJs), np.array(rotFreqs), np.array(rotIntensities), np.array(rotPops)

    def _calcRotFreqsTheory(self):
        jMax = (np.max(np.abs(self.freqs)) * PRE.T / (self._b * PHYS.c) - 6) / 2 + 3
        js = np.arange(jMax)
        energiesTheory = (self._b * js * (js + 1) - self._d * js ** 2 * (js + 1) ** 2) * PHYS.c / PRE.T
        return -(energiesTheory[:-2] - energiesTheory[2:]) / 2

    def _getTrimmedSlice(self):
        threshold = np.max(self.intensities) * TRIM_THRESHOLD_FACTOR
        startIndex, stopIndex = 0, len(self.wavelengths)
        while self.intensities[startIndex] < threshold: startIndex += 1
        while self.intensities[stopIndex - 1] < threshold: stopIndex -= 1

        centerIndex = np.argmin(np.abs(self.wavelengths - PROBE_WL))
        startIndex = np.clip(startIndex - TRIM_PADDING, 0, centerIndex)
        stopIndex = np.clip(stopIndex + TRIM_PADDING, centerIndex, len(self.wavelengths))
        return slice(startIndex, stopIndex)


if __name__ == '__main__':
    raman = RamanControl('C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-01-28 N2/raman/0.txt', 'N2')
    raman.plotSides()
