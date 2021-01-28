import pathlib
import os
import spectrum
import myplot
import myprocess
import numpy as np
from constants import PRE, c

WAVELENGTH_RANGE_NM = (395, 405)


class Xfrog:
    def __init__(self, data_folder, probe_zero_position_mm, cfg_bg_file, probe_bg_file, wavelength_range_nm=WAVELENGTH_RANGE_NM):
        base_path = pathlib.Path(data_folder)
        file_names = os.listdir(data_folder)
        delays, intensities, peak_wavelengths, peak_intensities = [], [], [], []

        spec_cfg_bg = spectrum.Spectrum(cfg_bg_file)
        spec_cfg_bg.remove_bg()
        spec_probe_bg = spectrum.Spectrum(probe_bg_file)
        spec_probe_bg.remove_bg()
        bg_intensities = np.add(spec_cfg_bg.intensities, spec_probe_bg.intensities)

        for file_name in file_names:
            position_mm = self._file_name_to_position_mm(file_name)
            delay = 2 * (position_mm - probe_zero_position_mm) * PRE.m / c
            spec = spectrum.Spectrum(base_path / file_name)
            spec.remove_bg()
            spec.intensities = np.subtract(spec.intensities, bg_intensities)
            spec.zoom(*wavelength_range_nm)

            peak_index = myprocess.index_peaks(spec.intensities, prominence=0.8)[0]
            peak_intensity = spec.intensities[peak_index]

            delays.append(delay)
            intensities.append(spec.intensities)
            peak_wavelengths.append(spec.wavelengths[peak_index])
            peak_intensities.append(peak_intensity)

        self.wavelengths = spec.wavelengths.copy()
        self.delays = np.array(delays)
        self.intensities = np.array(intensities).T
        self.peak_wavelengths = np.array(peak_wavelengths)
        self.peak_intensities = np.array(peak_intensities)

    def cmap_raw(self, title=None):
        plot = myplot.Plot()
        extent = [self.delays[0] / PRE.p, self.delays[-1] / PRE.p, self.wavelengths[0] / PRE.n, self.wavelengths[-1] / PRE.n]
        plot.cmap(self.intensities, label='Intensity (a.u.)', extent=extent, flip=True)
        plot.show(xlabel='Delay (ps)', ylabel='Wavelength (nm)', title=title)
        return self

    def plot_peak_wavelengths(self, title=None):
        plot = myplot.Plot()
        plot.line(self.delays / PRE.p, self.peak_wavelengths / PRE.n, format_='o-')
        plot.show(xlabel='Delay (ps)', ylabel='Peak Wavelength (nm)', title=title)
        return self

    def plot_peak_intensities(self, title=None):
        plot = myplot.Plot()
        plot.line(self.delays / PRE.p, self.peak_intensities)
        plot.show(xlabel='Delay (ps)', ylabel='Peak Intensity (a.u.)', title=title, grid=True)
        return self

    @staticmethod
    def _file_name_to_position_mm(name):
        stripped_name = '.'.join(name.split('.')[:-1])
        position = stripped_name.replace('-', '.')
        try:
            position = float(position)
        except ValueError:
            raise RuntimeError(f'File name "{name}" is not a valid position (e.g. "130-25.xls")')
        return position

