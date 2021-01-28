import os
import pathlib
from spectrum import Spectrum

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / f'{NAME}_assets'

if __name__ == '__main__':
    spec = Spectrum(ASSETS_DIR / 'control.xls')
    spec.remove_bg().plot()
    # spec.plot_norm()
    # rmn = Raman(f'{run_name}.txt', 'control.txt')
    # rmn.plot_raw()
    # rmn.plot_pops()
    # rmn.plot_ratios()
