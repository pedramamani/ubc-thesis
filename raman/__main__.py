import pathlib
import os
import numpy as np
import iPlot
import json
import matplotlib.pyplot as plt
from scipy.interpolate import interp2d
from cfg.cfgControl import CfgControl
from cfg.cfgNotch import CfgNotch
from raman.ramanControl import RamanControl
from raman.ramanNotch import RamanNotch
from dataset import Dataset
from raman.cache import *

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / 'assets'


def plotAll(folderName):
    notchFolder = ASSETS_DIR / folderName / 'notch'
    ramanFolder = ASSETS_DIR / folderName / 'raman'
    datasetNotch = Dataset(notchFolder)
    datasetRaman = Dataset(ramanFolder)
    controlNotch = CfgControl(notchFolder / datasetNotch.__next__()[0]).plotCfg(name='control-notch')
    controlRaman = RamanControl(ramanFolder / datasetRaman.__next__()[0], molecule='N2-20210320').plotRaman(name='control-raman')
    dataSummary = []
    js = [40, 42, 44, 46, 48, 50, 52]
    jsOther = [41, 43, 45, 47, 49, 51]

    for (notchFile, notchInfo), (ramanFile, ramanInfo) in zip(datasetNotch, datasetRaman):
        if notchInfo.tag in {'faulty', 'error', 'control'}:
            print(f'Data number {notchInfo.number} was skipped due to "{notchInfo.tag}" tag.')
            print()
            continue
        notch = CfgNotch(notchFolder / notchFile, control=controlNotch, rescale=True)
        raman = RamanNotch(ramanFolder / ramanFile, control=controlRaman)
        dataSummary.append({**notch.notchMetrics.__dict__, 'ocsPopulation': raman.meanPopulation(js) / controlRaman.meanPopulation(js)})

        print(notchInfo)
        print(notch.notchMetrics)
        print(f'js Relative Strength: {raman.meanPopulation(js) / controlRaman.meanPopulation(js)}')
        print(f'jsOther Relative Strength: {raman.meanPopulation(jsOther) / controlRaman.meanPopulation(jsOther)}')
        print()
        # notch.plotNotch(name=f'{notchInfo.number}-notch-{notch.notchMetrics.depth:.2f}-'
        #                      f'{notch.notchMetrics.fwhm:.3f}-{notch.notchMetrics.centerFrequency:.3f}')
        raman.plotRamanComparison(name=f'raman-{notch.notchMetrics.depth:.2f}-{notch.notchMetrics.fwhm:.3f}')

    # with open(ASSETS_DIR / folderName / 'summary.json', 'w+') as file:
    #     json.dump(dataSummary, file, indent=2)


if __name__ == '__main__':
    plotAll('2021-03-20 N2')

    # with open('./temp.json', 'r') as file:
    #     assets = json.load(file)['ramanPopulations']
    # image = []
    # for i in range(17, 31):
    #     image.append(assets[str(i)])
    # image = np.array(image)
    # plot = iPlot.Plot()
    # plot.cmap(np.log(0.1 + image[:, 27:]), extent=[30, 51, 18.10, 18.23], flip=True, label='Population (a.u.)')
    # plot.show(xlabel='J State', ylabel='Lateral Position (mm)')

    # assets = data20210303
    # depths = np.array([d.depth for d in assets.values()])
    # fwhms = np.array([d.fwhm for d in assets.values()])
    # n2OcsRatios = np.array([d.n2OcsRatio for d in assets.values()])
    #
    # plt.scatter(fwhms, depths, c=np.log(n2OcsRatios), s=100, marker='o', zorder=3)
    # cb = plt.colorbar()
    # cb.set_label('log(N2/OCS Population)')
    # plt.xlabel('Notch FWHM (THz)')
    # plt.ylabel('Notch Depth (0-1)')
    # plt.grid(color=(0.85, 0.85, 0.85))
    # plt.show()
