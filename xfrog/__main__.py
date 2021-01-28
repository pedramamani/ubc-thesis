import os
import pathlib
from xfrog import Xfrog
from xfrog_rel import XfrogRel
from constants import PRE
import myprocess
import myplot
import spectrum

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / f'{NAME}_assets'

if __name__ == '__main__':
    probe_zero_mm = 160
    xfrog = Xfrog(ASSETS_DIR / 'run_2/3', probe_zero_mm, ASSETS_DIR / 'run_2/bg_cfg.xls', ASSETS_DIR / 'run_2/bg_probe.xls')
    xfrog_ctrl = Xfrog(ASSETS_DIR / 'run_2/4', probe_zero_mm, ASSETS_DIR / 'run_2/bg_cfg.xls', ASSETS_DIR / 'run_2/bg_probe.xls')

    plot = myplot.Plot()
    plot.line(xfrog.delays / PRE.p, xfrog_ctrl.peak_intensities, format_='--')
    plot.line(xfrog.delays / PRE.p, xfrog.peak_intensities)
    plot.show(xlabel='Delay (ps)', ylabel='Peak Intensity (a.u.)', legend=['Full', 'Pierced'], grid=True)

    # xfrog_rel = XfrogRel(xfrog, xfrog_ctrl)
    # xfrog_rel.zoom(399, 403)
    # xfrog_rel.plot_peak_intensities()
    # xfrog_rel.cmap_raw()
    # xfrog.plot_peak_wavelengths()

    # spec = spectrum.Spectrum(ASSETS_DIR / 'run_2/3/176-00.xls')
    # spec.remove_bg().zoom(398, 402)  #.zoom(797.5, 804)
    # spec.plot()
