from scipy import optimize, signal
import numpy as np
import warnings
warnings.filterwarnings('error')

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


def denoise(y, factor=DENOISE_FACTOR, order=DENOISE_FILTER_ORDER):
    params = signal.butter(order, factor, btype='lowpass')
    y = signal.filtfilt(*params, y)
    return y


def indexPeaks(y, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE):
    prominence *= np.max(y) - np.min(y)
    indices, _ = signal.find_peaks(y, distance=distance, prominence=(prominence, None))
    return indices


def indexEdges(y, prominence=EDGE_PROMINENCE):
    prominence *= np.max(y) - np.min(y)
    indices = np.where(abs(y[:-1] - y[1:]) >= prominence)[0] + 1
    return indices


def centroid(x, peakIndex, count=CENTROID_COUNT):
    n = (count - 1) // 2
    start, end = peakIndex - n, peakIndex + n
    x0 = np.average(x[start: end])
    dx = np.average(x[start + 1: end + 1] - x[start: end])
    sigma = (dx / 2) / np.sqrt(count)
    return x0, sigma


def fit(f, x, y, sigma, absoluteSigma=True, guess=None):
    try:
        params, cov = optimize.curve_fit(f, x, y, p0=guess, sigma=sigma, absolute_sigma=absoluteSigma, maxfev=DEFAULT_MAXFEV)
    except Warning:
        raise Exception('Optimal fit parameters could not be estimated.')
    errors = np.diag(cov)

    chi2 = np.sum(((y - f(x, *params)) / sigma) ** 2)
    return params, errors, chi2


def fitFunc(f, x, y, sigma, absoluteSigma=True, relativeStep=ERROR_RELATIVE_STEP, absoluteStep=ERROR_ABSOLUTE_STEP):
    params, errors, _ = fit(f, x, y, sigma, absoluteSigma=absoluteSigma)

    def func(xVals, sigma=None):
        xVals = np.array(xVals)
        yErrors = np.zeros_like(xVals)
        for i, (param, error) in enumerate(zip(params, errors)):
            aparams, bparams = params.copy(), params.copy()
            dparam = np.maximum(np.abs(param * relativeStep), absoluteStep)
            aparams[i] += dparam
            bparams[i] -= dparam
            diff = np.divide(f(xVals, *aparams) - f(xVals, *bparams), 2 * dparam)
            yErrors = np.add(yErrors, np.power(diff * error, 2))
        if sigma is not None:
            dx = np.maximum(np.abs(xVals * relativeStep), absoluteStep)
            ax = xVals + dx
            bx = xVals - dx
            diff = np.divide(f(ax, *params) - f(bx, *params), 2 * dx)
            yErrors = np.add(yErrors, np.power(np.multiply(diff, sigma), 2))
        return f(xVals, *params), np.sqrt(yErrors)
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

