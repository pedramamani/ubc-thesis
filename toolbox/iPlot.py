import matplotlib.pyplot as plt
import matplotlib
import datetime
import numpy as np
import seaborn
import pathlib

PALETTE = 'husl'
GRID_COLOR = (0.85, 0.85, 0.85)
SHADE_OPACITY = 0.2
TITLE_FONT_SIZE = 16
LABEL_FONT_SIZE = 12

ASPECT_RATIO = 'auto'
LINE_COLOR = 'k'
Z_ORDER = 3
LINE_WIDTH = 1.0
MARKER_SIZE = 5
FIGURE_SIZE = (6, 4)
MARGINS = (0, 0.1)


class Plot:
    def __init__(self, figureSize=FIGURE_SIZE, titleFontSize=TITLE_FONT_SIZE, labelFontSize=LABEL_FONT_SIZE, gridColor=GRID_COLOR):
        plt.figure(figsize=figureSize)
        self.number = plt.gcf().number
        self.titleFontSize = titleFontSize
        self.labelFontSize = labelFontSize
        self.gridColor = gridColor
        self.lastPlot = None

    def line(self, x, y, format_=None, lineWidth=LINE_WIDTH, markerSize=MARKER_SIZE, zOrder=Z_ORDER):
        plt.figure(self.number)
        if format_ is None:
            self.lastPlot = plt.plot(x, y, linewidth=lineWidth, markersize=markerSize, zorder=zOrder)
        else:
            self.lastPlot = plt.plot(x, y, format_, linewidth=lineWidth, markersize=markerSize, zorder=zOrder)
        return self

    def bar(self, x, y, width=None, zOrder=Z_ORDER, color=LINE_COLOR):
        plt.figure(self.number)
        width = 1 if width is None else width
        width *= np.mean(x[1:] - x[:-1])
        self.lastPlot = plt.bar(x, y, width=width, zorder=zOrder, color=color)
        return self

    def shade(self, x, yLow, yHigh, color=None):
        plt.figure(self.number)
        if color is None:
            color = matplotlib.colors.to_rgba(self.lastPlot[0].get_color())
            color = (*color[0:3], SHADE_OPACITY)
        self.lastPlot = plt.fill_between(x, yLow, yHigh, color=color)
        return self

    def errbar(self, x, y, yerr, format_=None, lineWidth=LINE_WIDTH, markerSize=MARKER_SIZE, zOrder=Z_ORDER):
        plt.figure(self.number)
        if format_ is None:
            plt.errorbar(x, y, yerr, linewidth=lineWidth, markersize=markerSize, zorder=zOrder)
        else:
            plt.errorbar(x, y, yerr, fmt=format_, linewidth=lineWidth, markersize=markerSize, zorder=zOrder)
        return self

    def cmap(self, data, label=None, flip=False, extent=None, aspectRatio=ASPECT_RATIO):
        plt.figure(self.number)
        if flip:
            data = np.flip(data, axis=0)
        with seaborn.color_palette(PALETTE):
            plt.imshow(data, extent=extent, aspect=aspectRatio, interpolation='none')
            cb = plt.colorbar()
            cb.set_label(label, fontsize=self.labelFontSize)
            cb.ax.tick_params(labelsize=self.labelFontSize)
        return self

    def xticks(self, x, labels):
        plt.figure(self.number)
        plt.xticks(x, labels)
        return self

    def yticks(self, y, labels):
        plt.figure(self.number)
        plt.yticks(y, labels)
        return self

    def annotate(self, labels, x, y, offset=(0, 0), rotation=0, fontSize=8):  # offset in pixels
        plt.figure(self.number)
        for label, x_, y_ in zip(labels, x, y):
            plt.annotate(label, (x_, y_), xytext=offset, textcoords='offset points', ha='center', va='center', rotation=rotation, size=fontSize)

    def show(self, legend=None, xlabel=None, ylabel=None, xrange=None, yrange=None, xscale='linear', yscale='linear',
             title=None, margins=MARGINS, grid=False, name=None):
        plt.figure(self.number)
        self._formatLegend(legend)
        if legend is not None:
            plt.legend(legend, fontsize=self.labelFontSize)
        if yrange is not None:
            plt.ylim(yrange)
        if xrange is not None:
            plt.xlim(xrange)
        if grid:
            plt.grid(color=self.gridColor, zorder=0)
        plt.xlabel(xlabel, fontsize=self.labelFontSize)
        plt.ylabel(ylabel, fontsize=self.labelFontSize)
        plt.xticks(fontsize=self.labelFontSize)
        plt.yticks(fontsize=self.labelFontSize)
        plt.xscale(xscale)
        plt.yscale(yscale)

        plt.title(title, fontsize=self.titleFontSize)
        plt.gcf().canvas.set_window_title(self._windowTitle() if name is None else name)
        plt.margins(*margins)
        plt.tight_layout()
        plt.show()

    def save(self, name, path=None):
        plt.figure(self.number)
        path = pathlib.Path(path)
        plt.savefig(path / f'{name}.png', bbox_inches='tight')

    def _formatLegend(self, legend):
        if (legend is None) or (type(legend) is str):
            return None
        for i, entry in enumerate(legend):
            if entry is None:
                legend[i] = '_nolegend_'
        return legend

    @staticmethod
    def _windowTitle():
        return f'Figure {datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")}'
