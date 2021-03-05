import numpy as np
import regex


def slice_(values: np.ndarray, startValue: float = None, stopValue: float = None) -> slice:
    startIndex = None if startValue is None else np.argmin(np.abs(values - startValue))
    stopIndex = None if stopValue is None else np.argmin(np.abs(values - stopValue))
    return slice(startIndex, stopIndex)


def sliceCenter(values: np.ndarray, centerValue: float, valueSpan: float) -> slice_:
    startValue = centerValue - valueSpan / 2
    stopValue = centerValue + valueSpan / 2
    return slice_(values, startValue, stopValue)


def sliceThreshold(values: np.ndarray, relativeThreshold: float = 0, padding: int = 0) -> slice:
    threshold = relativeThreshold * np.max(values)
    passIndices, = np.where(values >= threshold)
    startIndex = np.clip(passIndices[0] - padding, 0, len(values))
    stopIndex = np.clip(passIndices[-1] + padding, 0, len(values))
    return slice(startIndex, stopIndex)


def matchDataFile(filePath: str, formatRegex: str):
    with open(filePath, 'r') as file:
        content = file.read()
    match = regex.match(formatRegex, content)
    assert match is not None, f'File "{filePath}" contents do not match given format.'
    return match


if __name__ == '__main__':
    list0 = np.array([2, 3, 4, 5, 6])
    slice0 = slice_(list0, 3, 5)
    newList0 = list0[slice0]

    list1 = np.array([2, 3, 4, 5, 6])
    slice1 = sliceCenter(list1, 4, 3)
    newList1 = list1[slice1]

    list2 = np.array([0, 0.1, 0.2, 0.5, 1, 0.8, 0.9, 0.6, 0.3, 0.1, 0, 0, 0])
    slice2 = sliceThreshold(list2, relativeThreshold=0.3)
    newList2 = list2[slice2]
