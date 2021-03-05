import os
import pathlib
from oldModules.notchSpectrum import NotchSpectrum
from oldModules.cfgSpectrum import CfgSpectrum
from dataset import Dataset
import iPlot
import iProcess
import numpy as np

DIR = pathlib.Path(os.path.dirname(__file__))
ASSETS_DIR = DIR / 'assets'


def extractData(folderName):
    folderPath = ASSETS_DIR / folderName
    dataset = Dataset(folderPath)
    controlSpectrum = CfgSpectrum(folderPath / dataset.__next__()[0])
    data = []
    for fileName, info in dataset:
        if info['tag'] != 'bad':
            notchSpectrum = NotchSpectrum(folderPath / fileName, controlSpectrum)
            info.update(notchSpectrum.notchParams)
            data.append(info)
    return data


def plotAll(folderName):
    folderPath = ASSETS_DIR / folderName
    dataset = Dataset(folderPath)
    controlSpectrum = CfgSpectrum(folderPath / dataset.__next__()[0])

    for fileName, info in dataset:
        notchSpectrum = NotchSpectrum(folderPath / fileName, controlSpectrum)
        print(info)
        print(notchSpectrum.notchParams)
        print()
        notchSpectrum.plotNotch()


def transitionHwhmVsFpDistance(data, doFit=True):
    x, y = [], []
    for info in data:
        if info['fiberConfig'].isdigit() and info['verticalPosition'] == 0:
            x.append(info['fpDistance'])
            y.append(info['transitionHwhm'])
            print(info)

    plot = iPlot.Plot()
    plot.line(x, y, format_='.')
    if doFit:
        def gaussBeam(z, A, zR):
            return A * np.sqrt(1 + (z / zR) ** 2)

        parameters, errors, chi2 = iProcess.fit(gaussBeam, x, y, np.full((len(x)), 0.01), guess=[0.065, 1])
        print(f'\nχ²: {chi2:.1E}\n'
              f'A: {parameters[0]:.3f} ± {errors[0]:.0E} THz\n'
              f'zR: {parameters[1]:.2f} ± {errors[1]:.0E} mm')
        xFit = np.linspace(min(x), max(x), 100)
        plot.line(xFit, gaussBeam(xFit, *parameters), format_='--')
    plot.show(xlabel='FP Distance (mm)', ylabel='Transition HWHM (THz)', legend=['Data', 'Fit'] if doFit else None, grid=True)


def depthVsVerticalPosition(data):
    x, y = [], []
    for info in data:
        if info['fiberConfig'] == '1' and info['fpDistance'] == 0:
            x.append(info['verticalPosition'])
            y.append(info['depth'])
            print(info)

    plot = iPlot.Plot()
    plot.line(x[::-1], y, format_='.', markerSize=8)
    plot.show(xlabel='Vertical Position', ylabel='Depth (0-1)', grid=True)


def fwhmVsVerticalPosition(data):
    x, y = [], []
    for info in data:
        if info['fiberConfig'] == '1' and info['fpDistance'] == 0:
            x.append(info['verticalPosition'])
            y.append(info['fwhm'])
            print(info)

    p2 = iPlot.Plot()
    p2.line(x[::-1], y, format_='.', markerSize=8)
    p2.show(xlabel='Vertical Position', ylabel='FWHM (THz)', grid=True)


def fwhmVsFiberCount(data, doFit=True):
    x, y = [], []
    for info in data:
        if all([info['fiberConfig'].isdigit(), info['fpDistance'] == 0, info['verticalPosition'] == 0]):
            x.append(int(info['fiberConfig']))
            y.append(info['fwhm'])
            print(info)

    p = iPlot.Plot()
    p.line(x, y, format_='.', markerSize=8)
    if doFit:
        parameters, errors, chi2 = iProcess.fit(iProcess.Function.line, x, y, np.full((len(x)), 0.01))
        print(f'\nχ²: {chi2:.1E}\n'
              f'slope: {parameters[0]:.3f} ± {errors[0]:.0E} THz\n'
              f'y-intercept: {parameters[1]:.3f} ± {errors[1]:.0E} THz')
        xFit = np.array([min(x), max(x)])
        p.line(xFit, iProcess.Function.line(xFit, *parameters), format_='--')
    p.show(xlabel='Fiber Count', ylabel='FWHM (THz)', legend=['Data', 'Fit'] if doFit else None, grid=True)


if __name__ == '__main__':
    plotAll('2021-01-21')
    # data = extractData('2021-01-21')
    # transitionHwhmVsFpDistance(data)
    # depthVsVerticalPosition(data)
    # fwhmVsVerticalPosition(data)
    # fwhmVsFiberCount(data)
