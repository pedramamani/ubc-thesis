from types import SimpleNamespace
from cfg.cfgFunctions import *
from sharedFunctions import *
from cfg.cfgControl import CfgControl
from scipy.optimize import minimize


class CfgNotch:
    def __init__(self, filePath: str, control: CfgControl, rescale=True):
        _, self.rawIntensities, self.dataMetrics = extractData(filePath)
        self.rawIntensities = self.rawIntensities[control.thresholdSlice]

        self.control = control
        self.cfgMetrics = SimpleNamespace(**control.cfgMetrics.__dict__)
        self.intensities = findIntensities(self.rawIntensities, self.control.blueSlice, self.control.redSlice, self.cfgMetrics)
        if rescale:
            self.intensities = self._findRescaledIntensities()

        self.attenuations = findRelativeDifference(self.intensities, control.intensities, 0.1)
        self.notchMetrics, self.notchSlice = self._findNotchMetrics()

    def plotRaw(self, title=None, name=None):
        plotRaw(self.control.rawWavelengths, self.rawIntensities, title=title, name=name)
        return self

    def plotCfg(self, title=None, name=None):
        plotCfg(self.control.rawWavelengths, self.intensities, self.control.blueSlice, self.control.redSlice, self.cfgMetrics, title=title, name=name)
        return self

    def plotArms(self, title=None, name=None):
        plotArms(self.control.frequencies, self.intensities, self.control.blueSlice, self.control.redSlice, title=title, name=name)
        return self

    def plotAttenuation(self, title=None, name=None):
        plot = iPlot.Plot()
        isBlue = (self.notchMetrics.arm == 'blue')
        thresholdSlice = sliceThreshold(self.attenuations, relativeThreshold=0.01)
        viewSlice = np.intersect1d(thresholdSlice, self.control.blueSlice if isBlue else self.control.redSlice)
        plot.line(self.control.frequencies[viewSlice], self.attenuations[viewSlice], format_='tab:blue' if isBlue else 'tab:red')
        plot.line(self.control.frequencies[self.notchSlice], self.attenuations[self.notchSlice], format_='k')
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Attenuation (0-1)', grid=True, title=title, name=name)
        return self

    def plotNotch(self, title=None, name=None):
        frequencies = self.control.frequencies[self.notchSlice]
        fitFrequencies = frequencies if len(frequencies) >= 100 else np.linspace(np.min(frequencies), np.max(frequencies), 100)
        parameters = self.notchMetrics.depth, self.notchMetrics.centerFrequency, self.notchMetrics.fwhm, self.notchMetrics.transitionHwhm
        plot = iPlot.Plot()
        plot.line(frequencies, self.attenuations[self.notchSlice], format_=f"tab:{self.notchMetrics.arm}")
        plot.line(fitFrequencies, self._joinedGaussians(fitFrequencies, *parameters), format_='k--')
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Attenuation (0-1)', grid=True, title=title, name=name)
        return self

    def _findNotchMetrics(self):
        guess, peakIndex = self._guessNotchMetrics()
        arm = 'blue' if peakIndex in self.control.blueSlice else 'red'
        armSlice = self.control.blueSlice if (arm == 'blue') else self.control.redSlice

        notchSlice = np.array([armSlice[i] for i in sliceCenter(
            self.control.frequencies[armSlice], self.control.frequencies[peakIndex], 6 * guess[2], includeStop=True)])
        frequencies = self.control.frequencies[notchSlice]

        parameters, *_ = iProcess.fit(self._joinedGaussians, frequencies, self.attenuations[notchSlice],
                                      np.full_like(frequencies, self.cfgMetrics.intensityNoise), guess=guess)
        # parameters = guess
        notchMetrics = SimpleNamespace(arm=arm, depth=parameters[0], centerFrequency=parameters[1], fwhm=parameters[2], transitionHwhm=np.abs(parameters[3]))
        notchSlice = np.array([armSlice[i] for i in sliceCenter(
            self.control.frequencies[armSlice], notchMetrics.centerFrequency, 4 * notchMetrics.fwhm, includeStop=True)])
        return notchMetrics, notchSlice

    def _guessNotchMetrics(self):
        peakIndex = np.argmax(self.attenuations)
        peakAttenuation = self.attenuations[peakIndex]
        left = right = peakIndex
        while self.attenuations[left] > peakAttenuation / 2: left -= 1
        while self.attenuations[right] > peakAttenuation / 2: right += 1
        fwhm = np.abs(self.control.frequencies[right] - self.control.frequencies[left])
        return [peakAttenuation, self.control.frequencies[peakIndex], fwhm, 0.1], peakIndex

    def _findRescaledIntensities(self):
        redRescaleSlice = self.control.redSlice[:30]
        blueRescaleSlice = self.control.blueSlice[:30]
        self.cfgMetrics.redAmplitude /= self._findRescaleFactor(self.intensities[redRescaleSlice],
                                                                self.control.intensities[redRescaleSlice])
        self.cfgMetrics.blueAmplitude /= self._findRescaleFactor(self.intensities[blueRescaleSlice],
                                                                 self.control.intensities[blueRescaleSlice])
        return findIntensities(self.rawIntensities, self.control.blueSlice, self.control.redSlice, self.cfgMetrics)

    @staticmethod
    def _findRescaleFactor(values, controlValues):
        def rescale(factor): return np.mean(np.abs(np.subtract(controlValues, factor * values)))
        return minimize(rescale, np.array([1])).x[0]

    @staticmethod
    def _joinedGaussians(values: np.ndarray, amplitude: float, center: float, fwhm: float, transitionHwhm: float):
        values = np.abs(values - center)
        halfSeparation = fwhm / 2 - transitionHwhm
        threshold = np.less(values, halfSeparation)
        return np.where(threshold, amplitude, amplitude * np.exp(-(values - halfSeparation) ** 2 / (1.4425 * transitionHwhm ** 2)))


if __name__ == '__main__':
    controlFile = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-02-11 OCS N2/notch/0.xls'
    notchFile = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-02-11 OCS N2/notch/10.xls'

    control = CfgControl(controlFile)
    notch = CfgNotch(notchFile, control, rescale=True)
    print(notch.notchMetrics)
    notch.plotArms()
    notch.plotAttenuation()
    notch.plotNotch()
