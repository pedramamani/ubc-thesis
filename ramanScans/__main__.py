import pathlib
import os
import numpy as np
import iPlot
import json
import matplotlib.pyplot as plt
from scipy.interpolate import interp2d
from cfg.cfgControl import CfgControl
from iConstants import *
import regex
from cfg.cfgNotch import CfgNotch
from raman.ramanControl import RamanControl
from raman.ramanNotch import RamanNotch
from dataset import Dataset
from raman.cache import *

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / 'assets'

PROBE_WAVELENGTH = 398


def extractScan(filePath):
    filePath = str(filePath)
    with open(filePath, 'r') as file:
        content = file.read()
    wavelengths, intensities = [], []
    delays = np.arange(0, 201, 2)
    for line in content.splitlines():
        values = [float(v) for v in line.split('\t')]
        wavelengths.append(values.pop(0))
        intensities.append(values)
    return np.array(intensities), np.array(wavelengths), delays


if __name__ == '__main__':
    folder = ASSETS_DIR / '2021-03-20 OCS'
    controlNotch = CfgControl(folder / '0.xls')

    probeIntensities, wavelengths, delays = extractScan(folder / 'probe.dat')
    frequencies = PHYS.c * (1 / PROBE_WAVELENGTH - 1 / wavelengths) / (PRE.n * PRE.T) / 2
    extent = [np.min(delays), np.max(delays), np.min(frequencies), np.max(frequencies)]
    # controlIntensities = extractScan(folder / f'0.dat')[0] - probeIntensities

    for i in range(1, 4):
        notch = CfgNotch(folder / f'{i}.xls', control=controlNotch, rescale=True)
        print(notch.notchMetrics)

    for i in range(4):
        intensities, *_ = extractScan(folder / f'{i}.dat')
        intensities -= probeIntensities

        plot = iPlot.Plot()
        plot.cmap(np.log2(np.clip(intensities, 1, 10000)), extent=extent, label='log$_{2}$ (Intensity)', flip=True)
        plot.show(xlabel='Delay (ps)', ylabel='Frequency (THz)')
