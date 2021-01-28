import numpy as np
from scipy.special import erf
from myplot import Plot
from constants import PRE
from myprocess import fit

POSITIONS = [30, 35, 37, 39, 41, 43, 45, 47, 48, 49, 50, 51, 53, 55, 57, 59, 61, 63, 68]
INTENSITIES = [[225.7, 225.5, 226.0],
               [225.2, 224.3, 225.6],
               [225.9, 225.5, 225.3],
               [224.3, 225.1, 224.1],
               [221.5, 222.3, 221.8],
               [218.4, 218.9, 218.3],
               [211.8, 210.8, 212.4],
               [200.6, 202.4, 201.0],
               [196.0, 196.0, 195.4],
               [187.9, 187.7, 188.9],
               [182.1, 183.0, 182.8],
               [176.1, 176.2, 177.3],
               [167.2, 167.9, 167.7],
               [160.9, 160.4, 160.5],
               [157.3, 157.5, 157.0],
               [155.1, 154.5, 154.6],
               [153.0, 153.0, 153.2],
               [152.3, 152.2, 153.2],
               [153.3, 152.8, 153.5]]
INTENSITY_ERROR = 0.1
POSITION_ERROR = 0.5
INTENSITY_SCALE = 1E-2  # scaling close to 1, for fit to converge
POSITIONS_SCALE = 10 * PRE.u

if __name__ == '__main__':
    xs, Is, err_Is = [], [], []

    for position, intensities in zip(POSITIONS, INTENSITIES):
        n = len(intensities)
        Is += [np.sum(intensities) / n * INTENSITY_SCALE]
        err_Is += [max(np.std(intensities), INTENSITY_ERROR / np.sqrt(n - 1)) * INTENSITY_SCALE]
        xs += [position * POSITIONS_SCALE]
    xs, Is, err_Is = np.array(xs), np.array(Is), np.array(err_Is)

    def erf_func(x, sigma, A, x0, y0):
        return A * erf(-(x - x0) / sigma) + y0
    params, errors, r2 = fit(erf_func, xs, Is, err_Is)

    title = f'r² = {r2:.4f}, w0 = {params[0] * np.sqrt(2) / PRE.u:.0f} ± {errors[0] * np.sqrt(2) / PRE.u:.0E} µm'
    p = Plot()
    p.errbar(xs / PRE.m, Is, err_Is, format_='.k')
    ax = np.linspace(np.min(xs), np.max(xs), 100)
    p.line(ax / PRE.m, erf_func(ax, *params), format_='b')
    p.show(xlabel='Position (mm)', ylabel='Intensity (a.u.)', legend=['Fit', 'Data'], title=title, grid=True)
