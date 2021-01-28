import numpy as np
from constants import PRE, c, pi

WL_CENTER_CFG = 800 * PRE.n
WL_PROBE = 400 * PRE.n
RED = 'Red'
BLUE = 'Blue'


class CFG:
    # rad/ps², THz, mm, °, mm⁻¹, cm, cm
    def __init__(self, chirp_rate, f_fwhm, x_fwhm, theta_in, grating_density, grating_distance, focal_length, tag=''):
        self.lambda0 = WL_CENTER_CFG
        self.f0 = c / self.lambda0
        self.fw = f_fwhm * PRE.T

        self.xw = x_fwhm * PRE.m
        self.gs = PRE.m / grating_density
        self.gd = grating_distance * PRE.c
        self.fl = focal_length * PRE.c
        self.tag = tag

        self.thetai = np.deg2rad(theta_in)
        self.theta0 = -np.arcsin(np.sin(self.thetai) - self.lambda0 / self.gs)
        self.beta = chirp_rate / PRE.p ** 2

    def specs(self):
        xw = self.freq_to_pos(self.f0 - self.fw / 2) - self.freq_to_pos(self.f0 + self.fw / 2)
        w0 = 2 * (c / self.f0) * self.fl * np.cos(self.thetai) / (pi * self.xw * np.cos(self.theta0))
        zR = pi * w0 ** 2 / self.lambda0
        chirp = pi * self.gs ** 2 * self.f0 ** 3 * np.cos(self.theta0) ** 2 / (2 * self.gd * c)

        print(f'{self.tag}CFG Specs\n'
              f'Grating Angle (°): {np.rad2deg(self.theta0):.1f}\n'
              f'Wavelength FWHM (nm): {(c / (self.f0 - self.fw / 2) - c / (self.f0 + self.fw / 2)) / PRE.n:.1f}\n'
              f'Focused beam x FWHM (mm): {xw / PRE.m:.1f}\n'
              f'Focused beam y FWHM (µm): {2 * w0 / PRE.u:.0f}\n'
              f'Rayleigh length (mm): {zR / PRE.m:.1f}\n'
              f'Input chirp (rad/ps²): {(self.beta - chirp) * PRE.p ** 2:.4f}\n')

    def notch(self, x0, width):  # mm, mm
        x1, x2 = (x0 - width / 2) * PRE.m, (x0 + width / 2) * PRE.m
        if x1 * x2 < 0:
            raise RuntimeError('Both arms cannot be notched at the same time.')
        if abs(x2) < abs(x1):  # make sure x1 is closer to the center
            x1, x2 = x2, x1

        arm = BLUE if x0 < 0 else RED
        f1, f2 = self.pos_to_freq(x1), self.pos_to_freq(x2)
        wl1, wl2 = c / max(f1, f2), c / min(f1, f2)
        fcfg1, fcfg2 = np.abs(f1 - self.f0), np.abs(f2 - self.f0)
        t1, t2 = pi * fcfg1 / self.beta, pi * fcfg2 / self.beta
        wlr1, wlr2 = WL_PROBE / (1 - 2 * fcfg1 * WL_PROBE / c), WL_PROBE / (1 - 2 * fcfg2 * WL_PROBE / c)

        print(f'Notch on {arm} Arm\n'
              f'Position (mm): {self._stat_text(x1, x2, scale=PRE.m)}\n'
              f'Wavelength (nm): {self._stat_text(wl1, wl2, scale=PRE.n, precision=3)}\n'
              f'CFG Frequency (THz): {self._stat_text(fcfg1, fcfg2, scale=PRE.T, precision=3)}\n'
              f'Time (ps): {self._stat_text(t1, t2, scale=PRE.p, precision=3)}\n'
              f'Raman Spectrum (nm): {self._stat_text(wlr1, wlr2, scale=PRE.n)}\n')

    def pos_to_freq(self, x):
        theta = np.arctan(x / self.fl) + self.theta0
        lambda_ = (np.sin(theta) + np.sin(self.thetai)) * self.gs
        f = c / lambda_
        return f

    def freq_to_pos(self, f):
        lambda_ = c / f
        theta = -np.arcsin(np.sin(self.thetai) - lambda_ / self.gs)
        pos = self.fl * np.tan(theta - self.theta0)
        return pos

    @staticmethod
    def _stat_text(x1, x2, scale=1, precision=2):
        x1, x2 = x1 / scale, x2 / scale
        avg = (x1 + x2) / 2
        diff = abs(x2 - x1)
        text = '{:.{p}f} [{:.{p}f}] {:.{p}f} => {:.{p}f}'.format(x1, avg, x2, diff, p=precision)
        return text


if __name__ == '__main__':
    sCFG = CFG(chirp_rate=0.017, f_fwhm=7, x_fwhm=3, theta_in=78, grating_density=2400, grating_distance=30,
               focal_length=50, tag='s')
    fCFG = CFG(chirp_rate=0.31, f_fwhm=29, x_fwhm=10, theta_in=44, grating_density=1500, grating_distance=30,
               focal_length=20, tag='f')
    sCFG.specs()
    sCFG.notch(6, 0.4)  # -4.6, 0.2 AND -5, 1.6
    fCFG.notch(-5, 0.3)
