import pathlib
import os
import myextract
import myprocess
import myplot
from constants import PRE, c
import numpy as np

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / f'{NAME}_assets'

ERROR_NORM = 0.05
CENTER_WL = 790 * PRE.n


class Spectrum:
    def __init__(self, file, control_file):
        wl, I = myextract.extract(ASSETS_DIR / file)
        _, I_ctrl = myextract.extract(ASSETS_DIR / control_file)

        self.I_ctrl, start, end = myprocess.trim_zeros(I_ctrl)
        self.I = I[start: end]
        self.wl = wl[start: end] * PRE.n

        i = np.argmin(np.abs(self.wl - CENTER_WL))
        i_peak = myprocess.index_peaks(self.I, distance=len(self.wl))[0]
        if i_peak < i:
            indices = np.arange(i, -1, -1)
        else:
            indices = np.arange(i, len(self.wl))
        self.norm = np.divide(self.I_ctrl - self.I, self.I_ctrl)[indices]
        self.fcfg = self._calc_fcfg()[indices]
        self.params = self._calc_notch_params()  # w, h, m, x0

    def plot_raw(self):
        p = myplot.Plot()
        p.line(self.wl / PRE.n, self.I_ctrl)
        p.line(self.wl / PRE.n, self.I)
        p.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', legend=['Control', 'Pierced'])

    def plot_norm(self):
        p = myplot.Plot()
        p.line(self.fcfg / PRE.T, self.norm)
        p.line(self.fcfg / PRE.T, self._notch(self.fcfg / PRE.T, *self.params))
        p.show(xlabel='CFG Frequency (THz)', ylabel='Normalized Intensity (0-1)', legend=['Data', 'Fit'])

    def _calc_fcfg(self):
        fcfg = np.zeros_like(self.wl)
        for i, wl in enumerate(self.wl):
            fcfg[i] = np.abs(c / CENTER_WL - c / wl)
        return fcfg

    def _calc_notch_params(self):
        h_mid = np.max(self.norm) / 2
        n = len(self.norm)

        for i_left in range(n):
            if self.norm[i_left] > h_mid:
                break
        for i_right in range(n - 1, -1, -1):
            if self.norm[i_right] > h_mid:
                break

        i = (i_right + i_left) // 2
        width = (self.fcfg[i_right] - self.fcfg[i_left]) / PRE.T
        guess = np.array([width, self.norm[i], 1, self.fcfg[i] / PRE.T])
        params, errors, r2 = myprocess.fit(self._notch, self.fcfg / PRE.T, self.norm, np.full_like(self.fcfg, ERROR_NORM), guess=guess)
        return params

    @staticmethod
    def _notch(x, w, h, m, x0):
        x = np.abs(x - x0)
        leq = np.less_equal(x, w / 2 - h / (2 * m))
        geq = np.greater_equal(x, w / 2 + h / (2 * m))

        y = h / 2 - m * (x - w / 2)
        y[leq] = h
        y[geq] = 0
        return y
