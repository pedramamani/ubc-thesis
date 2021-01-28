import os
import pathlib
from spectrumNotch import SpectrumNotch
from spectrum import Spectrum
import myplot
import myprocess
import numpy as np

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / f'assets'

# data = [arrangement, FP distance (mm), vertical pos, width (THz), depth (0-1), onset width (THz)]
# vertical position # is 0 for full
data = [
    ['1', 0, 3, 0.096, 0.158, 0.0564],
    ['1', 0, 2, 0.119, 0.299, 0.0573],
    ['1', 0, 1, 0.134, 0.438, 0.0571],
    ['1', 0, 0, 0.204, 0.557, 0.0515],
    ['1', 2, 2, 0.136, 0.267, 0.0708],
    ['1', 2, 1, 0.154, 0.434, 0.0728],
    ['1', 2, 0, 0.208, 0.540, 0.0710],
    ['1', 5, 1, 0.239, 0.278, 0.1163],
    ['1', 5, 0, 0.250, 0.437, 0.1214],
    ['1(1)1', 0, 9, 0.786, 0.289, 0.1842],
    ['3', 0, 1, 0.556, 0.574, 0.0602],
    ['3', 0, 0, 0.694, 0.662, 0.0836],
    ['3', 2, 1, 0.551, 0.514, 0.0689],
    ['3', 2, 0, 0.617, 0.579, 0.0770],
    ['3', 5, 2, 0.595, 0.202, 0.1064],
    ['3', 5, 1, 0.571, 0.404, 0.1422],
    ['3', 5, 0, 0.617, 0.565, 0.1562],
    ['1(1)1(1)1', 5, 0, 1.103, 0.309, 0.0926],
    ['1(1)1(1)1', 17, 0, 1.192, 0.296, 0.4562],
    ['6', 0, 0, 1.316, 0.659, 0.0718],
    ['6', 2, 0, 1.317, 0.666, 0.1037],
    ['6', 5, 0, 1.189, 0.587, 0.1598],
    ['6', 17, 0, 1.201, 0.566, 0.4809]
]

def plotAll():
    for fileName in os.listdir(ASSETS_DIR):
        print(f'\n----------------------\n{fileName}')
        s = SpectrumNotch(ASSETS_DIR / fileName, ASSETS_DIR / 'no-notch.xls')
        s.print_params()
        # s.plot_raw()
        s.plot_norm()

def onsetWidthVsFPDistance():
    x, y = [], []
    # [arrangement, FP distance(mm), vertical pos, width (THz), depth (0-1), onset width (THz)]
    for point in data:
        if point[0] in {'1', '3', '6'}:
            y.append(point[5])
            x.append(point[1])
    xrange = max(x) - min(x)
    padding = 0.1
    xMin = min(x) - padding * xrange
    xMax = max(x) + padding * xrange

    def gaussBeam(z, df0, zR):
        return df0 * np.sqrt(1 + (z / zR) ** 2)

    params, errors, r2 = myprocess.fit(gaussBeam, x, y, np.full((len(x)), 0.004), guess=[0.065, 1])
    print(f'w0: {params[0]} +- {errors[0]} THz\n'
          f'zR: {params[1]} +- {errors[1]} mm')

    p = myplot.Plot()
    p.line(x, y, format_='.')
    xFit = np.linspace(xMin, xMax, 100)
    p.line(xFit, gaussBeam(xFit, *params))
    p.show(xlabel='Distance from FP (mm)', ylabel='Onset width (THz)', xrange=[xMin, xMax], legend=['Data', 'Fit'], grid=True)


def depthWidthVsVerticalPos():
    x, y1, y2 = [], [], []
    # [arrangement, FP distance(mm), vertical pos, width (THz), depth (0-1), onset width (THz)]
    for point in data:
        if point[0] in {'1'} and point[1] == 0:
            y1.append(point[4])
            y2.append(point[3])
            x.append(point[2])
    xrange = max(x) - min(x)
    padding = 0.1
    xMin = min(x) - padding * xrange
    xMax = max(x) + padding * xrange

    p1 = myplot.Plot()
    p1.line(x[::-1], y1, format_='.', marker_size=8)
    p1.show(xlabel='Vertical position', ylabel='Depth (0-1)', xrange=[xMin, xMax], grid=True)

    p2 = myplot.Plot()
    p2.line(x[::-1], y2, format_='.', marker_size=8)
    p2.show(xlabel='Vertical position', ylabel='Width (THz)', xrange=[xMin, xMax], grid=True)


def depthVsFPDistance():
    x, y= [], []
    # [arrangement, FP distance(mm), vertical pos, width (THz), depth (0-1), onset width (THz)]
    for point in data:
        if point[0] in {'1'} and point[2] == 0:
            y.append(point[4])
            x.append(point[1])
    xrange = max(x) - min(x)
    padding = 0.1
    xMin = min(x) - padding * xrange
    xMax = max(x) + padding * xrange

    p = myplot.Plot()
    p.line(x, y, format_='.', marker_size=8)
    p.show(xlabel='Distance from FP (mm)', ylabel='Depth (0-1)', xrange=[xMin, xMax], grid=True)


def widthVsFiberCount():
    x, y= [], []
    # [arrangement, FP distance(mm), vertical pos, width (THz), depth (0-1), onset width (THz)]
    for point in data:
        if point[0] in {'1', '3', '6'}:
            y.append(point[3])
            x.append(int(point[0]))
    xrange = max(x) - min(x)
    padding = 0.1
    xMin = min(x) - padding * xrange
    xMax = max(x) + padding * xrange

    params, errors, r2 = myprocess.fit(myprocess.Function.line, x, y, np.full((len(x)), 0.004))
    print(f'slope: {params[0]} +- {errors[0]} THz\n'
          f'y-intercept: {params[1]} +- {errors[1]} THz')

    p = myplot.Plot()
    p.line(x, y, format_='.', marker_size=8)
    xFit = np.array([xMin, xMax])
    p.line(xFit, myprocess.Function.line(xFit, *params))
    p.show(xlabel='Fiber count', ylabel='Width (THz)', xrange=[xMin, xMax], grid=True, legend=['Data', 'Fit'])


if __name__ == '__main__':
    # widthVsFiberCount()
    s = Spectrum(ASSETS_DIR / 'no-notch.xls')
    s.remove_bg()
    s.plot()



