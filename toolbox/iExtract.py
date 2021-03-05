import numpy as np

DEFAULT_XCOL = 0
DEFAULT_YCOL = 1
EXTENSIONS = ['txt', 'xls', 'csv', 'dat']
SEPARATORS = ['\t', '\t', ',', '\t']


def extract(file_path, xcol=DEFAULT_XCOL, ycol=DEFAULT_YCOL, separator=None):
    file_path = str(file_path)
    extension = file_path.split('.')[-1].lower()
    col_count = max(xcol, ycol) + 1

    if extension in EXTENSIONS:
        with open(file_path, 'r') as file:
            raw_data = file.read()
    else:
        raise RuntimeError(f'File extension .{extension} is not supported.')
    if separator is None:
        separator = SEPARATORS[EXTENSIONS.index(extension)]

    xs, ys = [], []
    for row in raw_data.split('\n'):
        if row == '':
            break
        bits = row.split(separator)
        if col_count <= len(bits):
            x, y = _float(bits[xcol]), _float(bits[ycol])
            if (x is not None) and (y is not None):
                xs.append(x)
                ys.append(y)
    return np.array(xs), np.array(ys)


def _float(s):
    try:
        x = float(s)
        return x
    except ValueError:
        return None
