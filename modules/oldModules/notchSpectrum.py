from oldModules.cfgSpectrum import CfgSpectrum
import numpy as np
import iPlot
import iProcess


class NotchSpectrum(CfgSpectrum):
    def __init__(self, filePath: str, control: CfgSpectrum):
        super().__init__(filePath, control)
        threshold = 20 * self.cfgParams['intensityNoise'] / self.cfgParams['amplitudeBlue']
        self.attenuations = normDifference(self.intensities, control.intensities, threshold)
        self.notchParams = self._calcNotchParams()

    def plotNotch(self, title=None, name=None, showFit=True):
        slice_ = self._redSlice if self.notchParams['arm'] == 'red' else self._blueSlice
        freqs = np.abs(self.freqs[slice_])
        start = np.argmin(np.abs(freqs - (self.notchParams['centerFrequency'] + self.notchParams['fwhm'] * 2)))
        end = np.argmin(np.abs(freqs - (self.notchParams['centerFrequency'] - self.notchParams['fwhm'] * 2)))
        start, end = min(start, end), max(start, end)
        freqs = freqs[start: end + 1]
        attenuations = self.attenuations[slice_][start: end + 1]

        plot = iPlot.Plot()
        plot.line(freqs, attenuations, format_=f"tab:{self.notchParams['arm']}")
        if showFit:
            params = self.notchParams['depth'], self.notchParams['centerFrequency'], self.notchParams['fwhm'], self.notchParams['transitionHwhm']
            fitFreqs = freqs if len(freqs) >= 100 else np.linspace(np.min(freqs), np.max(freqs), 100)
            plot.line(fitFreqs, joinedGaussians(fitFreqs, *params), format_='k--')
            legend = ['Data', 'Fit']
        else:
            legend = None
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Attenuation (0-1)', title=title, legend=legend, grid=True, name=name)
        return self

    def _calcNotchParams(self):
        maxIndex = np.argmax(self.attenuations)
        arm = 'red' if self.freqs[maxIndex] < 0 else 'blue'

        guess = [self.attenuations[maxIndex], self.freqs[maxIndex], self._guessNotchWidth(maxIndex), 0.1]
        parameters, *_ = iProcess.fit(joinedGaussians, self.freqs, self.attenuations, np.full_like(self.attenuations, self.cfgParams['intensityNoise']), guess=guess)
        return {
            'arm': arm,
            'depth': parameters[0],
            'centerFrequency': np.abs(parameters[1]),
            'fwhm': parameters[2],
            'transitionHwhm': np.abs(parameters[3])
        }

    def _guessNotchWidth(self, centerIndex: int) -> float:
        halfMaxAttenuation = self.attenuations[centerIndex] / 2
        startIndex = centerIndex
        endIndex = centerIndex
        while self.attenuations[startIndex] > halfMaxAttenuation: startIndex -= 1
        while self.attenuations[endIndex] > halfMaxAttenuation: endIndex += 1
        return np.abs(self.freqs[endIndex] - self.freqs[startIndex])


def normDifference(values: np.ndarray, controlValues: np.ndarray, threshold: float):
    return np.where(controlValues > threshold, np.divide(controlValues - values, controlValues, where=(controlValues != 0)), 0)


def joinedGaussians(values: np.ndarray, amplitude: float, center: float, fwhm: float, transitionHwhm: float):
    values = np.abs(values - center)
    halfSeparation = fwhm / 2 - transitionHwhm
    threshold = np.less(values, halfSeparation)
    return np.where(threshold, amplitude, amplitude * np.exp(-(values - halfSeparation) ** 2 / (1.4425 * transitionHwhm ** 2)))
