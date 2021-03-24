from iConstants import *
from raman.ramanFunctions import *
from sharedFunctions import *


class RamanControl:
    def __init__(self, filePath: str, molecule: str):
        self.rawWavelengths, self.rawIntensities = extractData(filePath)
        self.constants = RAMAN_CONSTANTS[molecule]
        self.maskSlice = sliceCenter(self.rawWavelengths, self.constants.probeWavelength, self.constants.maskSpan)
        self.rawIntensities[self.maskSlice] = 0

        trimSlice = sliceThreshold(self.rawIntensities, relativeThreshold=0.01, padding=20)
        redSlice = sliceRange(self.rawWavelengths, startValue=self.constants.probeWavelength)
        self.stokesSlice = np.arange(redSlice[0], trimSlice[-1])

        self.intensities = self.rawIntensities[self.stokesSlice].copy()
        self.frequencies = PHYS.c * (1 / self.constants.probeWavelength - 1 / self.rawWavelengths[self.stokesSlice]) / (PRE.n * PRE.T) / 2

        self.rotationalEnergies = {}
        self.bounds, self.js = self._findBounds()

        self.boundIndices = np.array([np.argmin(np.abs(self.frequencies - b)) for b in self.bounds])
        self.populations = findPopulations(self.intensities, self.boundIndices, self.js, self.constants)

    def plotRaw(self, title=None, name=None):
        plotRaw(self.rawWavelengths, self.rawIntensities, title=title, name=name)
        return self

    def plotRaman(self, title=None, name=None):
        plotRaman(self.frequencies, self.intensities, self.bounds, self.js, title=title, name=name)
        return self

    def plotPopulation(self, title=None, name=None):
        plotPopulation(self.js, self.populations, title=title, name=name)
        return self

    def meanPopulation(self, meanJs):
        return meanPopulation(self.populations, self.js, meanJs)

    def _findBounds(self):
        maxFrequency = np.max(self.frequencies)
        j = self.constants.jStart
        step = self.constants.jStep
        bounds = []

        while True:
            bound = (self._rotationalEnergy(j + 2) - self._rotationalEnergy(j) +
                     self._rotationalEnergy(j + 2 + step) - self._rotationalEnergy(j + step)) / 4
            if bound > maxFrequency:
                break
            bounds.append(bound)
            j += step
        return np.array(bounds), np.arange(self.constants.jStart + step, j, step)

    def _rotationalEnergy(self, j):
        if j not in self.rotationalEnergies:
            self.rotationalEnergies[j] = (self.constants.b * j * (j + 1) - self.constants.d * j ** 2 * (
                        j + 1) ** 2) / PRE.c * PHYS.c / PRE.T
        return self.rotationalEnergies[j]


if __name__ == '__main__':
    file = '/raman/assets/2021-03-03 OCS N2/raman/0.txt'
    otherFile = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2020-08-27 O2/0.txt'
    raman = RamanControl(file, 'N2')
    raman.plotRaman()
    raman.plotPopulation()
