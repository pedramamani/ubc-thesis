import matplotlib.pyplot as plt
import matplotlib
import datetime
import numpy as np
import seaborn

PALETTE = 'husl'
GRID_COLOR = (0.85, 0.85, 0.85)
SHADE_OPACITY = 0.2
TITLE_FONT_SIZE = 16
LABEL_FONT_SIZE = 12

ASPECT_RATIO = 'auto'
LINE_COLOR = 'k'
Z_ORDER = 0
LINE_WIDTH = 1.4
MARKER_SIZE = 5
FIGURE_SIZE = (6, 4)
MARGINS = (0, 0.1)


class Plot:
    def __init__(self, figure_size=FIGURE_SIZE, title_font_size=TITLE_FONT_SIZE, label_font_size=LABEL_FONT_SIZE, grid_color=GRID_COLOR):
        plt.figure(figsize=figure_size)
        self.number = plt.gcf().number
        self.title_font_size = title_font_size
        self.label_font_size = label_font_size
        self.grid_color = grid_color
        self.last_plot = None

    def line(self, x, y, format_=None, line_width=LINE_WIDTH, marker_size=MARKER_SIZE):
        plt.figure(self.number)
        if format_ is None:
            self.last_plot = plt.plot(x, y, linewidth=line_width, markersize=marker_size)
        else:
            self.last_plot = plt.plot(x, y, format_, linewidth=line_width, markersize=marker_size)
        return self

    def bar(self, x, y, width=None, z_order=Z_ORDER):
        plt.figure(self.number)
        if width is None:
            width = np.mean(x[1:] - x[:-1])
        self.last_plot = plt.bar(x, y, width=width, zorder=z_order)
        return self

    def shade(self, x, y_low, y_high, color=None):
        plt.figure(self.number)
        if color is None:
            color = matplotlib.colors.to_rgba(self.last_plot[0].get_color())
            color = (*color[0:3], SHADE_OPACITY)
        self.last_plot = plt.fill_between(x, y_low, y_high, color=color)
        return self

    def errbar(self, x, y, yerr, format_=None, line_width=LINE_WIDTH, marker_size=MARKER_SIZE, z_order=Z_ORDER):
        plt.figure(self.number)
        if format_ is None:
            plt.errorbar(x, y, yerr, linewidth=line_width, markersize=marker_size, zorder=z_order)
        else:
            plt.errorbar(x, y, yerr, fmt=format_, linewidth=line_width, markersize=marker_size, zorder=z_order)
        return self

    def cmap(self, data, label=None, flip=False, extent=None, aspect_ratio=ASPECT_RATIO):
        plt.figure(self.number)
        if flip:
            data = np.flip(data, axis=0)
        with seaborn.color_palette(PALETTE):
            plt.imshow(data, extent=extent, aspect=aspect_ratio, interpolation='none')
            cb = plt.colorbar()
            cb.set_label(label, fontsize=self.label_font_size)
            cb.ax.tick_params(labelsize=self.label_font_size)
        return self

    def xticks(self, x, labels):
        plt.figure(self.number)
        plt.xticks(x, labels)
        return self

    def yticks(self, y, labels):
        plt.figure(self.number)
        plt.yticks(y, labels)
        return self

    def show(self, legend=None, xlabel=None, ylabel=None, xrange=None, yrange=None, title=None, margins=MARGINS, grid=False):
        plt.figure(self.number)
        self._format_legend(legend)
        if legend is not None:
            plt.legend(legend, fontsize=self.label_font_size)
        if yrange is not None:
            plt.ylim(yrange)
        if xrange is not None:
            plt.xlim(xrange)
        if grid:
            plt.grid(color=self.grid_color)
        plt.xlabel(xlabel, fontsize=self.label_font_size)
        plt.ylabel(ylabel, fontsize=self.label_font_size)

        # ax = plt.gca()
        # ax.axes.xaxis.set_ticklabels([])
        plt.xticks(fontsize=self.label_font_size)
        plt.yticks(fontsize=self.label_font_size)
        plt.title(title, fontsize=self.title_font_size)
        plt.gcf().canvas.set_window_title(self._window_title())
        plt.margins(*margins)
        plt.tight_layout()
        plt.show()

    def _format_legend(self, legend):
        if (legend is None) or (type(legend) is str):
            return None
        for i, entry in enumerate(legend):
            if entry is None:
                legend[i] = '_nolegend_'
        return legend

    @staticmethod
    def _window_title():
        return f'Figure {datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")}'
