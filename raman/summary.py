import json
import pathlib
import os
import matplotlib.pyplot as plt
import numpy as np

DIR = pathlib.Path(os.path.dirname(__file__))
NAME = os.path.basename(DIR)
ASSETS_DIR = DIR / 'assets'


if __name__ == '__main__':
    # with open(ASSETS_DIR / '2021-03-10 N2' / 'summary.json', 'r') as file:
    #     assets = json.load(file)
    #
    # depths = np.array([d['depth'] for d in assets])
    # fwhms = np.array([d['fwhm'] for d in assets])
    # n2Populations = np.array([d['n2Population'] for d in assets])
    #
    # plt.scatter(fwhms, depths, c=np.log(n2Populations + 0.001) / np.log(2), s=100, marker='o', zorder=3, vmin=-5, vmax=0)
    # cb = plt.colorbar()
    # cb.set_label('log2 (N2 Population)')
    # plt.xlabel('Notch FWHM (THz)')
    # plt.ylabel('Notch Depth (0-1)')
    # plt.grid(color=(0.85, 0.85, 0.85))
    # plt.show()

    with open(ASSETS_DIR / '2021-03-10 OCS' / 'summary.json', 'r') as file:
        data = json.load(file)

    depths = np.array([d['depth'] for d in data])
    fwhms = np.array([d['fwhm'] for d in data])
    ocsPopulations = np.array([d['ocsPopulation'] for d in data])

    plt.scatter(fwhms, depths, c=np.log(ocsPopulations + 0.001), s=100, marker='o', zorder=3, vmin=-5, vmax=0)
    cb = plt.colorbar()
    cb.set_label('log2 (OCS Population)')
    plt.xlabel('Notch FWHM (THz)')
    plt.ylabel('Notch Depth (0-1)')
    plt.grid(color=(0.85, 0.85, 0.85))
    plt.show()
