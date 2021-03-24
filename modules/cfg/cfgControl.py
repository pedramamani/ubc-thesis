from iConstants import *
from cfg.cfgFunctions import *
from sharedFunctions import *


class CfgControl:
    def __init__(self, filePath: str):
        self.rawWavelengths, self.rawIntensities, self.dataMetrics = extractData(filePath)
        self.thresholdSlice = sliceThreshold(self.rawIntensities, relativeThreshold=0.01)
        self.rawWavelengths = self.rawWavelengths[self.thresholdSlice]
        self.rawIntensities = self.rawIntensities[self.thresholdSlice]

        intensityNoise = np.std(np.concatenate((self.rawIntensities[:20], self.rawIntensities[-20:])))
        self.cfgMetrics = SimpleNamespace(intensityNoise=intensityNoise, centerWavelength=self._findCenterWavelength())
        self.cfgMetrics.__dict__.update(self._findCfgFitMetrics())
        self.redSlice = sliceRange(self.rawWavelengths, startValue=self.cfgMetrics.centerWavelength)
        self.blueSlice = sliceRange(self.rawWavelengths, stopValue=self.cfgMetrics.centerWavelength)[::-1]
        self.frequencies, self.cfgMetrics.centerFrequency = self._findFrequencies()
        self.intensities = findIntensities(self.rawIntensities, self.blueSlice, self.redSlice, self.cfgMetrics)

    def plotRaw(self, title=None, name=None):
        plotRaw(self.rawWavelengths, self.rawIntensities, title=title, name=name)
        return self

    def plotCfg(self, title=None, name=None):
        plotCfg(self.rawWavelengths, self.intensities, self.blueSlice, self.redSlice, self.cfgMetrics, title=title, name=name)
        return self

    def plotArms(self, title=None, name=None):
        plotArms(self.frequencies, self.intensities, self.blueSlice, self.redSlice, title=title, name=name)
        return self

    def _findCenterWavelength(self):
        centerWavelength = self.rawWavelengths[np.argmax(self.rawIntensities)]
        centerSlice = sliceCenter(self.rawWavelengths, centerWavelength, np.ptp(self.rawWavelengths) / 20)
        centerIntensities = self.rawIntensities[centerSlice]
        valleyIndices = iProcess.indexPeaks(-centerIntensities, distance=len(centerIntensities), prominence=0.01)
        centerWavelength = self.rawWavelengths[valleyIndices[0] + centerSlice[0]]
        return centerWavelength

    def _findFrequencies(self):
        factor = PHYS.c / (PRE.n * PRE.T)
        centerFrequency = factor / self.cfgMetrics.centerWavelength
        frequencies = np.abs(factor / self.rawWavelengths - centerFrequency)
        return frequencies, centerFrequency

    def _findCfgFitMetrics(self):
        samplingStep = len(self.rawWavelengths) // 50
        wavelengths, intensities = self.rawWavelengths[::samplingStep], self.rawIntensities[::samplingStep]
        guess = [np.min(intensities)] + [np.ptp(intensities), np.ptp(wavelengths) / 4] * 2
        parameters, *_ = iProcess.fit(self._centeredHalfGaussians(), wavelengths, intensities,
                                      np.full_like(intensities, self.cfgMetrics.intensityNoise), guess=guess)
        return {
            'bgIntensity': parameters[0],
            'blueAmplitude': parameters[1],
            'blueFwhm': np.abs(parameters[2]),
            'redAmplitude': parameters[3],
            'redFwhm': np.abs(parameters[4])
        }

    def _centeredHalfGaussians(self):
        return lambda vs, o, aL, wL, aR, fR: halfGaussians(vs, self.cfgMetrics.centerWavelength, o, aL, wL, aR, fR)


if __name__ == '__main__':
    file = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-02-11 OCS N2/notch/0.xls'
    cfg = CfgControl(file)
    print(cfg.cfgMetrics)
    cfg.plotRaw()
    cfg.plotCfg()
    cfg.plotArms()
