from myprocess import *
from myplot import Plot


if __name__ == '__main__':
    x = [1, 2, 3, 4]
    y = [1.5, 2, 3, 3.7]
    sigma = [0.1, 0.3, 0.2, 0.3]

    f = fit_func(Function.line, x, y, sigma)
    x_vals = [0, 2, 4]
    y_vals, y_errors = f(x_vals)

    p = Plot()
    p.errbar(x, y, sigma, format_='.r').errbar(x_vals, y_vals, y_errors, format_='.--b')
    p.show(xrange=[None, None])
