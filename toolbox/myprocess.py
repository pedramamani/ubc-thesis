from scipy import optimize, signal
import numpy as np

DENOISE_FILTER_ORDER = 2
DENOISE_FACTOR = 0.1
PEAK_PROMINENCE = 0.1
PEAK_DISTANCE = 10
EDGE_PROMINENCE = 0.8
DEFAULT_MAXFEV = 10000
BIN_COUNT = 20
CENTROID_COUNT = 5
ERROR_RELATIVE_STEP = 1E-8
ERROR_ABSOLUTE_STEP = 1E-8


def hist2d(x, y, bin_count=BIN_COUNT):
    return np.histogram2d(x, y, bins=bin_count)


def trim_zeros(x):
    start, end = 0, len(x) - 1
    while x[start] == 0:
        start += 1
    while x[end] == 0:
        end -= 1
    end += 1
    return x[start: end], start, end


def denoise(y, factor=DENOISE_FACTOR, order=DENOISE_FILTER_ORDER):
    params = signal.butter(order, factor, btype='lowpass')
    y = signal.filtfilt(*params, y)
    return y


def index_peaks(y, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE):
    prominence *= np.max(y) - np.min(y)
    indices, _ = signal.find_peaks(y, distance=distance, prominence=(prominence, None))
    return indices


def index_edges(y, prominence=EDGE_PROMINENCE):
    prominence *= np.max(y) - np.min(y)
    indices = np.where(abs(y[:-1] - y[1:]) >= prominence)[0] + 1
    return indices


def centroid(x, peak_index, count=CENTROID_COUNT):
    n = (count - 1) // 2
    start, end = peak_index - n, peak_index + n
    x0 = np.average(x[start: end])
    dx = np.average(x[start + 1: end + 1] - x[start: end])
    sigma = (dx / 2) / np.sqrt(count)
    return x0, sigma


def fit(f, x, y, sigma, absolute_sigma=True, guess=None):
    params, cov = optimize.curve_fit(f, x, y, p0=guess, sigma=sigma, absolute_sigma=absolute_sigma, maxfev=DEFAULT_MAXFEV)
    errors = np.diag(cov)

    chi2 = np.sum(((y - f(x, *params)) / sigma) ** 2)
    return params, errors, chi2


def fit_func(f, x, y, sigma, absolute_sigma=True, relative_step=ERROR_RELATIVE_STEP, absolute_step=ERROR_ABSOLUTE_STEP):
    params, errors, _ = fit(f, x, y, sigma, absolute_sigma=absolute_sigma)

    def func(x_vals, sigma=None):
        x_vals = np.array(x_vals)
        y_errors = np.zeros_like(x_vals)
        for i, (param, error) in enumerate(zip(params, errors)):
            aparams, bparams = params.copy(), params.copy()
            dparam = np.maximum(np.abs(param * relative_step), absolute_step)
            aparams[i] += dparam
            bparams[i] -= dparam
            diff = np.divide(f(x_vals, *aparams) - f(x_vals, *bparams), 2 * dparam)
            y_errors = np.add(y_errors, np.power(diff * error, 2))
        if sigma is not None:
            dx = np.maximum(np.abs(x_vals * relative_step), absolute_step)
            ax = x_vals + dx
            bx = x_vals - dx
            diff = np.divide(f(ax, *params) - f(bx, *params), 2 * dx)
            y_errors = np.add(y_errors, np.power(np.multiply(diff, sigma), 2))
        return f(x_vals, *params), np.sqrt(y_errors)

    return func


class Function:
    @staticmethod
    def line(x, a, b):
        x = np.array(x)
        return a * x + b

    @staticmethod
    def rabi(x, A, a1, B, a2, omega, phi, y0):
        x = np.array(x)
        return A * np.exp(-a1 * x) + B * np.exp(-a2 * x) * np.cos(omega * x + phi) + y0

    @staticmethod
    def lorentzian(x, A, w, x0, y0):
        x = np.array(x)
        return A * w ** 2 / ((x - x0) ** 2 + w ** 2) + y0

    @staticmethod
    def gaussian(x, h, x0, sigma, y0):
        x = np.array(x)
        return h / (sigma * np.sqrt(2 * np.pi)) * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + y0

    @staticmethod
    def exp_decay(x, A, a, y0):
        x = np.array(x)
        return A * np.exp(-a * x) + y0

