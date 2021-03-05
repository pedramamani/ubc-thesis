import regex
import os
import numpy as np
import iPlot

FORMAT = '(?:(?P<wavelength>[0-9.]*)\t(?P<intensity>[0-9.-]*)\n)+$'


class Raman:
    def __init__(self, filePath: str):
        filePath = str(filePath)
        assert all([os.path.exists(filePath), os.path.isfile(filePath), filePath.endswith('.txt')]), \
            f'Path "{filePath}" does not exist or is not a ".txt" file.'
        with open(filePath, 'r') as file:
            content = file.read()
        match = regex.match(FORMAT, content)
        assert match is not None, f'Data file "{filePath}" contents have an unknown format.'

        self.rawWavelengths = np.array([float(v) for v in match.captures('wavelength')])
        self.rawIntensities = np.array([float(v) for v in match.captures('intensity')])

    def plotRaw(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.line(self.rawWavelengths, self.rawIntensities, format_='k')
        plot.show(xlabel='Wavelength (nm)', ylabel='Intensity (a.u.)', title=title, grid=True, name=name)
        return self

    def _getSlice(self, startWavelength: float = None, stopWavelength: float = None) -> slice:
        startIndex = None if startWavelength is None else np.argmin(np.abs(self.rawWavelengths - startWavelength))
        stopIndex = None if stopWavelength is None else np.argmin(np.abs(self.rawWavelengths - stopWavelength))
        return slice(startIndex, stopIndex)

    def _getCenteredSlice(self, centerWavelength: float, wavelengthSpan: float) -> slice:
        return self._getSlice(centerWavelength - wavelengthSpan / 2, centerWavelength + wavelengthSpan / 2)


if __name__ == '__main__':
    raman = Raman('C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-03-03 OCS N2/raman/0.txt')
    raman.plotRaw()
