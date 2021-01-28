import myplot
import numpy as np
from constants import PRE, c

REL_NORM_FACTOR = 2


class XfrogRel:
    def __init__(self, xfrog, xfrog_ctrl):
        self.wavelengths = xfrog_ctrl.wavelengths.copy()
        self.delays = xfrog_ctrl.delays.copy()
        self.peak_wavelengths = xfrog_ctrl.peak_wavelengths.copy()

        self.intensities_rel = self._rel_norm(xfrog.intensities, xfrog_ctrl.intensities)
        # self.intensities_rel = xfrog_ctrl.intensities - xfrog.intensities
        self.peak_intensities_rel = self._rel_norm(xfrog.peak_intensities, xfrog_ctrl.peak_intensities)

    def zoom(self, lower_wavelength_nm, upper_wavelength_nm):
        index_lower = np.argmin(np.abs(self.wavelengths - lower_wavelength_nm * PRE.n))
        index_upper = np.argmin(np.abs(self.wavelengths - upper_wavelength_nm * PRE.n))
        self.intensities_rel = self.intensities_rel[index_lower: index_upper + 1]
        self.wavelengths = self.wavelengths[index_lower: index_upper + 1]
        return self

    def cmap_raw(self):
        plot = myplot.Plot()
        extent = [self.delays[0] / PRE.p, self.delays[-1] / PRE.p, self.wavelengths[0] / PRE.n, self.wavelengths[-1] / PRE.n]
        plot.cmap(self.intensities_rel, label='Intensity Difference (a.u.)', extent=extent, flip=True)
        plot.show(xlabel='Delay (ps)', ylabel='Wavelength (nm)')
        return self

    def plot_peak_intensities(self, title=None):
        plot = myplot.Plot()
        plot.line(self.delays / PRE.p, self.peak_intensities_rel)
        plot.show(xlabel='Delay (ps)', ylabel='Relative Peak Intensity (a.u.)', title=title, grid=True)
        return self

    @staticmethod
    def _rel_norm(data, ctrl, factor=REL_NORM_FACTOR):
        return np.where(np.abs(data) < factor * np.abs(ctrl), data / np.abs(ctrl), 0)
