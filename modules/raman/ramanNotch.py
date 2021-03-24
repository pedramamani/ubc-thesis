from raman.ramanFunctions import *
from sharedFunctions import *
from raman.ramanControl import RamanControl


class RamanNotch:
    def __init__(self, filePath: str, control: RamanControl):
        _, self.rawIntensities = extractData(filePath)
        self.rawIntensities[control.maskSlice] = 0
        self.intensities = self.rawIntensities[control.stokesSlice].copy()
        self.control = control

        self.populations = findPopulations(self.intensities, control.boundIndices, control.js, control.constants)
        self.populationChange = np.subtract(self.populations, self.control.populations)

    def plotRaw(self, title=None, name=None):
        plotRaw(self.control.rawWavelengths, self.rawIntensities, title=title, name=name)
        return self

    def plotRaman(self, title=None, name=None):
        plotRaman(self.control.frequencies, self.intensities, self.control.bounds, self.control.js, title=title, name=name)
        return self

    def plotRamanComparison(self, title=None, name=None):
        labelPositions = [(a + b) / 2 for a, b in zip(self.control.bounds, self.control.bounds[1:])]
        plot = iPlot.Plot()
        plot.line(self.control.frequencies, self.control.intensities, format_='lightcoral')
        plot.line(self.control.frequencies, self.intensities, format_='k')
        plot.line(self.control.bounds, np.full_like(self.control.bounds, 0), format_='|g', markerSize=10)
        plot.annotate(self.control.js, labelPositions, np.zeros_like(self.control.js), offset=(0.6, -9), rotation=90, fontSize=6)
        plot.show(xlabel='Centrifuge Frequency (THz)', ylabel='Intensity (a.u.)', grid=True, title=title, name=name)
        return self

    def plotPopulation(self, title=None, name=None):
        plotPopulation(self.control.js, self.populations, title=title, name=name)
        return self

    def plotPopulationComparison(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.bar(self.control.js, self.populations, width=0.8, color='dimgray')
        for controlJ, controlPopulation in zip(self.control.js, self.control.populations):
            plot.line(np.array([controlJ, controlJ]), np.array([0, controlPopulation]), format_='lightcoral', markerSize='6', zOrder=5)
        plot.show(xlabel='J State', ylabel='Population (a.u.)', grid=True, title=title, name=name)

    def plotChange(self, title=None, name=None):
        plot = iPlot.Plot()
        plot.bar(self.control.js, self.populationChange, width=0.8)
        plot.show(xlabel='J State', ylabel='Population Difference (a.u.)', grid=True, title=title, name=name)
        return self

    def meanPopulation(self, meanJs):
        return meanPopulation(self.populations, self.control.js, meanJs)


if __name__ == '__main__':
    controlFile = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-03-03 OCS N2/raman/0.txt'
    notchFile = 'C:/Users/amani/PycharmProjects/ubc-thesis/raman/assets/2021-03-03 OCS N2/raman/3.txt'

    control = RamanControl(controlFile, 'N2-20210303')
    notch = RamanNotch(notchFile, control)
    notch.plotRamanComparison()
    notch.plotPopulationComparison()
    notch.plotChange()
