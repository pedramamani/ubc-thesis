import myextract
import myprocess
import myplot
from constants import PRE
import numpy as np

BG_COUNT = 10


class Spectrum:
    def __init__(self, file_path):
        wavelength, intensity = myextract.extract(file_path)
        self.intensities, start, end = myprocess.trim_zeros(intensity)
        self.wavelengths = wavelength[start: end] * PRE.n

    def zoom(self, lower_wavelength_nm, upper_wavelength_nm):
        index_lower = np.argmin(np.abs(self.wavelengths - lower_wavelength_nm * PRE.n))
        index_upper = np.argmin(np.abs(self.wavelengths - upper_wavelength_nm * PRE.n))
        self.intensities = self.intensities[index_lower: index_upper + 1]
        self.wavelengths = self.wavelengths[index_lower: index_upper + 1]
        return self

    def remove_bg(self, bg_indices=None):
        if bg_indices is None:
            count_points = len(self.wavelengths)
            bg_indices = np.concatenate((np.arange(0, BG_COUNT + 1), np.arange(count_points - BG_COUNT, count_points)))
        bg_value = np.mean(self.intensities[bg_indices])
        self.intensities -= bg_value
        return self

    def plot(self, title=''):
        plot = myplot.Plot()
        plot.line(self.wavelengths / PRE.n, self.intensities)
        plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', title=title, grid=True)
        return self
