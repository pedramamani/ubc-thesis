import myplot
from constants import PRE
import numpy as np
import spectrum

BG_COUNT = 10
DIVIDE_REL_FACTOR = 0.1


class SpectrumRel:
    def __init__(self, filePath, filePathCtrl):
        self.spectrum = spectrum.Spectrum(filePath)
        self.spectrumCtrl = spectrum.Spectrum(filePathCtrl)
        self.wavelengths = self.spectrum.wavelengths.copy()
        self.removeBackground()
        self.intensities = self.divideRel(self.spectrum.intensities, self.spectrumCtrl.intensities)

    def zoom(self, lowerWavelength, upperWavelength):
        self.spectrum.zoom(lowerWavelength, upperWavelength)
        self.spectrumCtrl.zoom(lowerWavelength, upperWavelength)
        indexLower = np.argmin(np.abs(self.wavelengths - lowerWavelength * PRE.n))
        indexUpper = np.argmin(np.abs(self.wavelengths - upperWavelength * PRE.n))
        self.intensities = self.intensities[indexLower: indexUpper + 1]
        self.wavelengths = self.wavelengths[indexLower: indexUpper + 1]
        return self

    def removeBackground(self, backgroundIndices=None):
        self.spectrum.remove_bg(bg_indices=backgroundIndices)
        self.spectrumCtrl.remove_bg(bg_indices=backgroundIndices)

    def plot(self, title=''):
        plot = myplot.Plot()
        plot.line(self.spectrumCtrl.wavelengths / PRE.n, self.intensities)
        plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', title=title, grid=True)
        return self

    @staticmethod
    def divideRel(values, valuesCtrl):
        maxCtrl = np.max(valuesCtrl)
        return np.where(valuesCtrl / maxCtrl > DIVIDE_REL_FACTOR, np.divide(valuesCtrl - values, valuesCtrl), 0)
