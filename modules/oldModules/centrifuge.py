import numpy as np
from iConstants import *

WL_CENTER_CFG = 800 * PRE.n
WL_PROBE = 400 * PRE.n


class Centrifuge:
    # rad/ps², THz, mm, °, mm⁻¹, cm, cm
    def __init__(self, chirpRate, fFwhm, xFwhm, thetaIn, gratingDensity, gratingDistance, focalLength, tag=''):
        self.lambda0 = WL_CENTER_CFG
        self.f0 = PHYS.c / self.lambda0
        self.fw = fFwhm * PRE.T

        self.xw = xFwhm * PRE.m
        self.gs = PRE.m / gratingDensity
        self.gd = gratingDistance * PRE.c
        self.fl = focalLength * PRE.c
        self.tag = tag

        self.thetai = np.deg2rad(thetaIn)
        self.theta0 = -np.arcsin(np.sin(self.thetai) - self.lambda0 / self.gs)
        self.beta = chirpRate / PRE.p ** 2

    def specs(self):
        xw = self.freqToPos(self.f0 - self.fw / 2) - self.freqToPos(self.f0 + self.fw / 2)
        w0 = 2 * (PHYS.c / self.f0) * self.fl * np.cos(self.thetai) / (np.pi * self.xw * np.cos(self.theta0))
        zR = np.pi * w0 ** 2 / self.lambda0
        chirp = np.pi * self.gs ** 2 * self.f0 ** 3 * np.cos(self.theta0) ** 2 / (2 * self.gd * PHYS.c)

        print(f'{self.tag}CFG specs\n'
              f'Grating angle (°): {np.rad2deg(self.theta0):.1f}\n'
              f'Wavelength FWHM (nm): {(PHYS.c / (self.f0 - self.fw / 2) - PHYS.c / (self.f0 + self.fw / 2)) / PRE.n:.1f}\n'
              f'Focused beam x FWHM (mm): {xw / PRE.m:.1f}\n'
              f'Focused beam y FWHM (µm): {2 * w0 / PRE.u:.0f}\n'
              f'Rayleigh length (mm): {zR / PRE.m:.1f}\n'
              f'Input chirp (rad/ps²): {(self.beta - chirp) * PRE.p ** 2:.4f}\n')

    def notch(self, x0, width):  # mm, mm
        x1, x2 = (x0 - width / 2) * PRE.m, (x0 + width / 2) * PRE.m
        if x1 * x2 < 0:
            raise RuntimeError('Cannot pierce both arms at the same time.')
        if abs(x2) < abs(x1):  # make sure x1 is closer to the center
            x1, x2 = x2, x1

        arm = 'blue' if x0 < 0 else 'red'
        f1, f2 = self.posToFreq(x1), self.posToFreq(x2)
        wl1, wl2 = PHYS.c / max(f1, f2), PHYS.c / min(f1, f2)
        fcfg1, fcfg2 = np.abs(f1 - self.f0), np.abs(f2 - self.f0)
        t1, t2 = np.pi * fcfg1 / self.beta, np.pi * fcfg2 / self.beta
        wlr1, wlr2 = WL_PROBE / (1 - 2 * fcfg1 * WL_PROBE / PHYS.c), WL_PROBE / (1 - 2 * fcfg2 * WL_PROBE / PHYS.c)

        print(f'Notch on {arm} arm\n'
              f'Position (mm): {self._statText(x1, x2, scale=PRE.m)}\n'
              f'Wavelength (nm): {self._statText(wl1, wl2, scale=PRE.n, precision=3)}\n'
              f'CFG frequency (THz): {self._statText(fcfg1, fcfg2, scale=PRE.T, precision=3)}\n'
              f'Time (ps): {self._statText(t1, t2, scale=PRE.p, precision=3)}\n'
              f'Raman spectrum (nm): {self._statText(wlr1, wlr2, scale=PRE.n)}\n')

    def posToFreq(self, x):
        theta = np.arctan(x / self.fl) + self.theta0
        lambda_ = (np.sin(theta) + np.sin(self.thetai)) * self.gs
        f = PHYS.c / lambda_
        return f

    def freqToPos(self, f):
        lambda_ = PHYS.c / f
        theta = -np.arcsin(np.sin(self.thetai) - lambda_ / self.gs)
        pos = self.fl * np.tan(theta - self.theta0)
        return pos

    @staticmethod
    def _statText(x1, x2, scale=1, precision=2):
        x1, x2 = x1 / scale, x2 / scale
        avg = (x1 + x2) / 2
        diff = abs(x2 - x1)
        text = '{:.{p}f} [{:.{p}f}] {:.{p}f} => {:.{p}f}'.format(x1, avg, x2, diff, p=precision)
        return text


if __name__ == '__main__':
    sCFG = Centrifuge(chirpRate=0.017, fFwhm=7, xFwhm=3, thetaIn=78, gratingDensity=2400, gratingDistance=30,
                      focalLength=50, tag='s')
    fCFG = Centrifuge(chirpRate=0.31, fFwhm=29, xFwhm=10, thetaIn=44, gratingDensity=1500, gratingDistance=30,
                      focalLength=20, tag='f')
    sCFG.specs()
    fCFG.notch(-5, 0.3)
