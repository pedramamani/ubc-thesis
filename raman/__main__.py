import os
import pathlib
from oldModules.notchSpectrum import NotchSpectrum
from oldModules.cfgSpectrum import CfgSpectrum
from oldModules.ramanSpectrum import RamanSpectrum
from dataset import Dataset
import iPlot
import numpy as np
from raman.cache import *

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / 'assets'


def processAll(folderName, doPlot=False):
    data = {}
    notchFolder = ASSETS_DIR / folderName / 'notch'
    ramanFolder = ASSETS_DIR / folderName / 'raman'
    datasetNotch = Dataset(notchFolder)
    datasetRaman = Dataset(ramanFolder)
    controlNotch = CfgSpectrum(notchFolder / datasetNotch.__next__()[0])
    controlRaman = RamanSpectrum(ramanFolder / datasetRaman.__next__()[0], molecule=folderName.split()[-1])

    print(controlNotch.cfgParams)

    for (notchFile, notchInfo), (ramanFile, ramanInfo) in zip(datasetNotch, datasetRaman):
        notch = NotchSpectrum(notchFolder / notchFile, control=controlNotch)
        raman = RamanSpectrum(ramanFolder / ramanFile, control=controlRaman)
        lastNotchJ = ramanInfo['lastNotchJ']

        slice_ = notch._redSlice if notch.notchParams['arm'] == 'red' else notch._blueSlice
        freqs = np.abs(notch.freqs[slice_])
        start = np.argmin(np.abs(freqs - (notch.notchParams['centerFrequency'] + notch.notchParams['fwhm'] * 1.5)))
        end = np.argmin(np.abs(freqs - (notch.notchParams['centerFrequency'] - notch.notchParams['fwhm'] * 1.5)))
        start, end = min(start, end), max(start, end)
        freqs = freqs[start: end + 1]
        attenuations = notch.attenuations[slice_][start: end + 1]

        relIntensities = []
        for j, intensity in zip(raman.rotJs, raman.rotIntensities):
            if j == lastNotchJ:
                lastNotchIndex = len(relIntensities)
            if j in controlRaman.rotJs:
                controlIntensity = controlRaman.rotIntensities[controlRaman.rotJs.index(j)]
                relIntensity = intensity / controlIntensity
                relIntensities.append(relIntensity)
        relIntensities = np.array(relIntensities)
        relIntensities /= np.mean(relIntensities[2:15])

        lostPop = np.sum(relIntensities[lastNotchIndex - 2: lastNotchIndex + 1])
        superPop = np.sum(relIntensities[lastNotchIndex + 1:])
        data[notchInfo['number']] = {'depth': notch.notchParams['depth'], 'fwhm': notch.notchParams['fwhm'], 'lost': lostPop, 'super': superPop}

        if doPlot:
            relIntensities = [f'{v:.1f}' for v in relIntensities]
            print(notchInfo)
            print(notch.notchParams)
            print()

            # notch.plotArms()
            # raman.plot()

            plot = iPlot.Plot()
            plot.line(np.abs(raman.freqs[raman._redSlice]), raman.intensities[raman._redSlice], format_='tab:red')
            plot.line(np.abs(raman.freqs[raman._blueSlice]), raman.intensities[raman._blueSlice], format_='tab:blue')
            plot.line(raman.rotFreqs, raman.rotIntensities, format_='.b')
            plot.annotate(raman.rotJs, raman.rotFreqs, raman.rotIntensities, offset=(0, 8), fontSize=7)
            plot.annotate(relIntensities, raman.rotFreqs, raman.rotIntensities, offset=(0, 2), fontSize=7)
            plot.line(freqs, attenuations, format_='g')
            plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (0-1)', legend=['Signal', 'J State', 'Notch'], grid=True)
    return data


def viewData(folderName):
    notchFolder = ASSETS_DIR / folderName / 'notch'
    ramanFolder = ASSETS_DIR / folderName / 'raman'
    datasetNotch = Dataset(notchFolder)
    datasetRaman = Dataset(ramanFolder)
    controlNotch = CfgSpectrum(notchFolder / datasetNotch.__next__()[0]).plotCfg(name='control-notch')
    controlRaman = RamanSpectrum(ramanFolder / datasetRaman.__next__()[0], molecule='N2').plotPops(name='control-raman', showTheory=True)
    controlRamanIntensities = controlRaman.rawIntensities

    for (notchFile, notchInfo), (ramanFile, ramanInfo) in zip(datasetNotch, datasetRaman):
        if notchInfo['tag'] in {'ignore', 'control'}:
            continue
        notch = NotchSpectrum(notchFolder / notchFile, control=controlNotch)
        raman = RamanSpectrum(ramanFolder / ramanFile, control=controlRaman)
        print(' '.join(f'{n}:{v}' for n, v in notchInfo.items()))
        print(' '.join(f'{n}:{v:.3f}' for n, v in list(notch.notchParams.items())[1:]))
        print(' '.join(f'{n}:{v:.3f}' for n, v in list(raman.params.items())[1:]))
        print()
        # notch.plotNotch(name=f"{notchInfo['number']}-notch-{notch.notchParams['depth']:.2f}-"
        #                      f"{notch.notchParams['fwhm']:.3f}-{notch.notchParams['centerFrequency']:.3f}")
        raman.plotPops(name=f"{ramanInfo['number']}-raman", showTheory=True)

        # plot = iPlot.Plot()
        # plot.line(np.abs(raman.freqs), controlRamanIntensities, format_='-k')
        # plot.line(np.abs(raman.freqs), raman.intensities, format_='tab:red')
        # plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (0-1)',
        #           legend=['Control', 'Pierced'], grid=True)


if __name__ == '__main__':
    # print(processAll('2021-01-28 N2', doPlot=True))
    viewData('2021-03-03 OCS N2')

    # data = data20210128N2
    # depths = np.array([d['depth'] for d in data.values()])
    # fwhms = np.array([d['fwhm'] for d in data.values()])
    # losts = np.array([d['lost'] for d in data.values()])
    # supers = np.array([d['super'] for d in data.values()])
    # ratios = np.divide(supers, losts)
    #
    # plot = iPlot.Plot()
    # plot.line(fwhms, ratios, format_='.k')
    # plot.show(xlabel='Notch FWHM (THz)', ylabel='Super/Lost Ratio', grid=True)

    # interpRatio = interp2d(fwhms, depths, ratios, kind='cubic')
    # plotFwhms = np.linspace(0, 1, 100)
    # plotDepths = np.linspace(0, 1, 100)
    # plotRatios = interpRatio(plotFwhms, plotDepths)
    # plot = iPlot.Plot()
    # plot.cmap(plotRatios, extent=[0, 1, 0, 1], label='Super/Lost Ratio')
    # plot.show(xlabel='Notch FWHM (THz)', ylabel='Notch Depth (0-1)')

    # plt.scatter(fwhms, depths, c=ratios, s=100, marker='o')
    # cb = plt.colorbar()
    # cb.set_label('Super/Lost Ratio')
    # plt.xlabel('Notch FWHM (THz)')
    # plt.ylabel('Notch Depth (0-1)')
    # plt.show()
