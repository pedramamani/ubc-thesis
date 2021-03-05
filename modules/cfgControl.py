import numpy as np
from funcCfg import *
from funcShared import *


class CfgControl:
    def __init__(self, filePath: str):
        self.wavelengths, self.rawIntensities, self.dataMetrics = extractData(filePath)
        self.thresholdSlice = sliceThreshold(self.rawIntensities, relativeThreshold=0.01)
        self.wavelengths = self.wavelengths[self.thresholdSlice]
        self.rawIntensities = self.rawIntensities[self.thresholdSlice]

        intensityNoise = np.std(np.concatenate((self.rawIntensities[:20], self.rawIntensities[-20:])))
        self.cfgMetrics = SimpleNamespace(intensityNoise=intensityNoise, centerWavelength=self._findCenterWavelength())
        self.redSlice = slice_(self.wavelengths, startValue=self.cfgMetrics.centerWavelength)
        self.blueSlice = slice_(self.wavelengths, stopValue=self.cfgMetrics.centerWavelength)
        self.frequencies, self.cfgMetrics.centerFrequency = self._findFrequencies()
        self.cfgMetrics.__dict__.update(self._findFitMetrics())

        self.intensities = self.rawIntensities - self.cfgMetrics.bgIntensity
        self.intensities[self.blueSlice] /= self.cfgMetrics.blueAmplitude
        self.intensities[self.redSlice] /= self.cfgMetrics.redAmplitude

    def plotRaw(self, title=None, name=None):
        plotRaw(self.wavelengths, self.rawIntensities, title=title, name=name)
        return self

    def plotArms(self, title=None, name=None):
        plotArms(self.frequencies, self.intensities, self.blueSlice, self.redSlice, title=title, name=name)
        return self

    def plotCfg(self, title=None, name=None):
        plotCfg(self.wavelengths, self.intensities, self.blueSlice, self.redSlice, self.cfgMetrics, title=title, name=name)
        return self

    def _findCenterWavelength(self):
        centerWavelength = self.wavelengths[np.argmax(self.rawIntensities)]
        centerSlice = sliceCenter(self.wavelengths, centerWavelength, np.ptp(self.wavelengths) / 20)
        centerIntensities = self.rawIntensities[centerSlice]
        valleyIndices = iProcess.indexPeaks(-centerIntensities, distance=len(centerIntensities), prominence=0.01)
        centerWavelength = self.wavelengths[valleyIndices[0] + centerSlice.start]
        return centerWavelength

    def _findFrequencies(self):
        factor = iConstants.PHYS.c / (iConstants.PRE.n * iConstants.PRE.T)
        centerFrequency = factor / self.cfgMetrics.centerWavelength
        frequencies = np.abs(factor / self.wavelengths - centerFrequency)
        return frequencies, centerFrequency

    def _findFitMetrics(self):
        samplingStep = len(self.wavelengths) // 50
        wavelengths, intensities = self.wavelengths[::samplingStep], self.rawIntensities[::samplingStep]
        guess = [np.min(intensities)] + [np.ptp(intensities), np.ptp(wavelengths) / 4] * 2
        parameters, *_ = iProcess.fit(self._centeredHalfGaussians(), wavelengths, intensities,
                                      np.full_like(intensities, self.cfgMetrics.intensityNoise), guess=guess)
        fitMetrics = {
            'bgIntensity': parameters[0],
            'blueAmplitude': parameters[1],
            'blueFwhm': np.abs(parameters[2]),
            'redAmplitude': parameters[3],
            'redFwhm': np.abs(parameters[4])}
        return fitMetrics

    def _centeredHalfGaussians(self):
        return lambda vs, o, aL, wL, aR, fR: halfGaussians(vs, self.cfgMetrics.centerWavelength, o, aL, wL, aR, fR)


if __name__ == '__main__':
    file = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-03-03 OCS N2/notch/3.xls'
    cfgControl = CfgControl(file)
    cfgControl.plotRaw()
    cfgControl.plotCfg()
    cfgControl.plotArms()
