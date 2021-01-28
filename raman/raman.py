import pathlib
import os
import myextract
import myprocess
import myplot
from constants import PRE, c, h
import numpy as np

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / f'{NAME}_assets'

B_O2_WL = PRE.c / 1.43768  # (m) rotational constant for O2

PROBE_WL = 398.1 * PRE.n
PEAK_DIST = 6
PEAK_PROM = 0.002

BOUNDS = [9, 30]


class Raman:
    def __init__(self, file, control_file):
        wl, I = myextract.extract(ASSETS_DIR / file)
        _, I_ctrl = myextract.extract(ASSETS_DIR / control_file)

        i = np.argmin(np.abs(wl - PROBE_WL / PRE.n))
        self.wl = wl[i:] * PRE.n
        self.I = I[i:]
        self.I_ctrl = I_ctrl[i:]

        self.divs = self._unify_list(myprocess.index_peaks(-self.I_ctrl, prominence=PEAK_PROM, distance=PEAK_DIST))
        self.pops = self._calc_pops(self.I)
        self.pops_ctrl = self._calc_pops(self.I_ctrl)
        self.ratios = self._calc_ratios(self.pops)
        self.ratios_ctrl = self._calc_ratios(self.pops_ctrl)
        self.fcfg = self._calc_fcfg()
        # E_hc = 1 / PROBE_WL - 1 / B_O2_WL * (4 * np.arange(30) + 6)
        # wl_transitions = (1 / E_hc) / PRE.n

    def plot_raw(self):
        p = myplot.Plot()
        p.line(self.wl / PRE.n, self.I_ctrl)
        p.line(self.wl / PRE.n, self.I)
        p.errbar(self.wl[self.divs] / PRE.n, np.zeros_like(self.divs), 100, format_='.k', marker_size=0, z_order=10)
        p.errbar(self.wl[self.divs][BOUNDS] / PRE.n, np.zeros_like(BOUNDS), 200, format_='.r', marker_size=0, z_order=10)
        p.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', legend=['Control', 'Pierced', 'Dividers'])

    def plot_pops(self):
        width = 0.4 * (self.fcfg[self.divs[1]] - self.fcfg[self.divs[0]]) / PRE.T
        p = myplot.Plot()
        p.bar(self.fcfg[self.divs] / PRE.T - width / 2, self.pops_ctrl, width=width)
        p.bar(self.fcfg[self.divs] / PRE.T + width / 2, self.pops, width=width)
        p.show(xlabel='CFG Frequency (THz)', ylabel='Population (a.u.)', legend=['Control', 'Pierced'])

    def plot_ratios(self):
        width = 0.4
        p = myplot.Plot()
        p.bar(np.arange(3) - width / 2, self.ratios_ctrl, width=width)
        p.bar(np.arange(3) + width / 2, self.ratios, width=width)
        p.xticks(np.arange(3), ['Thermal', 'Lost', 'Super'])
        p.show(ylabel='Ratios', legend=['Control', 'Pierced'], grid=True)

    def _calc_ratios(self, pops):
        i1, i2 = BOUNDS[0], BOUNDS[1]
        ratios = np.array([np.sum(pops[0: i1]), np.sum(pops[i1: i2]), np.sum(pops[i2:])]) / np.sum(pops[0: i1])
        return ratios

    def _calc_fcfg(self):
        fcfg = np.zeros_like(self.wl)
        for i, wl in enumerate(self.wl):
            fcfg[i] = (c / PROBE_WL - c / wl) / 2
        return fcfg

    def _calc_pops(self, values):
        pops = np.zeros_like(self.divs)
        for i in range(len(self.divs) - 1):
            pops[i] = np.sum(values[self.divs[i]: self.divs[i+1]])
        return pops

    @staticmethod
    def _unify_list(values):
        steps = values[1:] - values[:-1]
        steps = steps[np.abs(steps - np.mean(steps)) < np.std(steps)]
        step = np.average(steps)

        values = list(values)
        for i in range(len(values) - 1):
            diff = values[i + 1] - values[i]
            if diff > step * 1.5:
                n = round(diff / step)
                values[i + 1: i + 1] = [round(values[i] + j * step) for j in range(1, n)]
        return values
