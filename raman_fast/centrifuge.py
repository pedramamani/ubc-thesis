from myextract import extract
from myprocess import denoise
from myplot import Plot
import numpy as np
import matplotlib.pyplot as plt


X_LABEL = 'Wavelength (nm)'
Y_LABEL = 'Amplitude'
SPECTRUM_DENOISE = 0.1
RAMAN_DENOISE = 0.999


def plot_spectrum(file, denoise_factor=SPECTRUM_DENOISE, zoom=True, option=None, title=None):
    title = file if title is None else title
    x, y = _process_spectrum(file, denoise_factor, zoom)
    plot_stack_overlay([x], [y], options=option, xlabels=X_LABEL, ylabels=Y_LABEL, title=title)


def plot_spectrum_overlay(files, denoise_factor=SPECTRUM_DENOISE, zoom=True, options=None, legends=None, title=None):
    legends = files if legends is None else legends
    xs, ys = _process_spectrum(files, denoise_factor, zoom)
    plot_stack_overlay([xs], [ys], options=[options], legends=[legends], xlabels=X_LABEL, ylabels=Y_LABEL, title=title)


def plot_raman(file, denoise_factor=RAMAN_DENOISE, zoom=True, option=None, title=None):
    title = file if title is None else title
    x, y = _process_raman(file, denoise_factor, zoom)
    plot_stack_overlay([x], [y], options=option, xlabels=X_LABEL, ylabels=Y_LABEL, title=title)


def plot_raman_overlay(files, denoise_factor=RAMAN_DENOISE, zoom=True, options=None, legends=None, title=None):
    xs, ys = _process_raman(files, denoise_factor, zoom)
    legends = files if legends is None else legends
    plot_stack_overlay([xs], [ys], options=[options], legends=[legends], xlabels=X_LABEL, ylabels=Y_LABEL, title=title)


def plot_spectrum_raman(file, denoise_factors=(SPECTRUM_DENOISE, RAMAN_DENOISE),
                        zooms=(True, True), options=None, title=None):
    title = file if title is None else title
    x_spectrum, y_spectrum = _process_spectrum(file, denoise_factors[0], zooms[0])
    x_raman, y_raman = _process_raman(file, denoise_factors[1], zooms[1])
    plot_stack_overlay([x_spectrum, x_raman], [y_spectrum, y_raman],
                       xlabels=X_LABEL, ylabels=Y_LABEL, options=options, title=title)


def plot_spectrum_raman_overlay(files, denoise_factors=(SPECTRUM_DENOISE, RAMAN_DENOISE),
                                zooms=(True, True), options=None, legends=None, title=None):
    options = [options] * 2
    legends = [files] * 2 if legends is None else [legends] * 2
    xs_spectrum, ys_spectrum = _process_spectrum(files, denoise_factors[0], zooms[0])
    xs_raman, ys_raman = _process_raman(files, denoise_factors[1], zooms[1])
    plot_stack_overlay([xs_spectrum, xs_raman], [ys_spectrum, ys_raman], xlabels=X_LABEL, ylabels=Y_LABEL,
                       options=options, legends=legends, title=title)


def _process_spectrum(files, denoise_factor, zoom):
    files = [files] if type(files) is str else files
    xs, ys = [], []
    for file in files:
        x, y = extract(f'{file}.xls', start_row=7)
        y = denoise(y, denoise_factor)
        y -= np.average(y[:50])
        y /= np.trapz(y[1320:1365])
        if zoom:
            x, y = x[:1365], y[:1365]
        xs.append(x)
        ys.append(y)
    return xs, ys


def _process_raman(files, denoise_factor, zoom):
    files = [files] if type(files) is str else files
    xs, ys = [], []
    for file in files:
        x, y = extract(f'{file}.txt')
        y = denoise(y, denoise_factor)
        y /= np.trapz(y[540: 590])
        if zoom:
            x, y = x[530:], y[530:]
        xs.append(x)
        ys.append(y)
    return xs, ys


def compare(files, denoise_factors=(SPECTRUM_DENOISE, RAMAN_DENOISE),
            zooms=(True, True), options=None, legends=None, title=None):
    options = [options] * 2
    legends = [files] * 2 if legends is None else [legends] * 2
    xs_spectrum, ys_spectrum = _process_spectrum(files, denoise_factors[0], zooms[0])
    xs_raman, ys_raman = _process_raman(files, denoise_factors[1], zooms[1])

    xs = [xs_spectrum, xs_raman]
    ys = [ys_spectrum, ys_raman]
    xlabels = X_LABEL
    ylabels = Y_LABEL

    count_subplots = 3
    options = [options] * count_subplots if (options is None or type(options) is str) else options
    legends = [legends] * count_subplots if legends is None else legends
    xlabels = [xlabels] * count_subplots if (xlabels is None or type(xlabels) is str) else xlabels
    ylabels = [ylabels] * count_subplots if (ylabels is None or type(ylabels) is str) else ylabels
    subtitles = ['', '']

    fig = plt.figure(figsize=(12, 3 * count_subplots), tight_layout=True)
    for i in range(2):
        subplot = fig.add_subplot(count_subplots, 1, i + 1)
        _subplot_overlay(subplot, xs[i], ys[i], options=options[i], legends=legends[i],
                         xlabel=xlabels[i], ylabel=ylabels[i], title=subtitles[i])

    ys_ratios = [find_raman_ratios(y) for y in ys_raman]
    subplot_ratios = fig.add_subplot(count_subplots, 1, 3)

    x_ratios = np.arange(len(ys_ratios[0]))  # the label locations
    width = 0.05  # the width of the bars

    count_bars = len(ys_ratios)
    for i, values in enumerate(ys_nratios):
        values[1] /= values[0]
        values[2] /= values[0]
        values[0] = 1
        rects = subplot_ratios.bar(x_ratios + i * width, values, width)
    subplot_ratios.set_xticks(x_ratios + width * (count_bars-1) / 2)
    subplot_ratios.set_xticklabels(['Lost', 'Notch lost', 'Super rotors'])

    fig.suptitle(title)
    # plt.gcf().canvas.set_window_title(_window_title() if title is None else title)
    plt.show()


def find_raman_ratios(y):
    lost = np.trapz(y[20:100])
    dropped = np.trapz(y[100:250])
    super_ = np.trapz(y[250:])

    return [lost, dropped, super_]
