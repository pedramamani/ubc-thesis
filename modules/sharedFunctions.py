import numpy as np
import regex


def sliceRange(values: np.ndarray, startValue: float = None, stopValue: float = None, includeStart=True, includeStop=True) -> np.ndarray:
    startIndex = 0 if startValue is None else np.argmin(np.abs(values - startValue)) + (0 if includeStart else 1)
    stopIndex = len(values) if stopValue is None else np.argmin(np.abs(values - stopValue)) + (1 if includeStop else 0)
    return np.arange(startIndex, stopIndex)


def sliceCenter(values: np.ndarray, centerValue: float, valueSpan: float, includeStart=True, includeStop=True) -> np.ndarray:
    startValue = centerValue - valueSpan / 2
    stopValue = centerValue + valueSpan / 2
    return sliceRange(values, startValue, stopValue, includeStart=includeStart, includeStop=includeStop)


def sliceThreshold(values: np.ndarray, relativeThreshold: float = 0, padding: int = 0) -> np.ndarray:
    threshold = relativeThreshold * np.max(values)
    passIndices, = np.where(values >= threshold)
    startIndex = np.clip(passIndices[0] - padding, 0, len(values))
    stopIndex = np.clip(passIndices[-1] + 1 + padding, 0, len(values))
    return np.arange(startIndex, stopIndex)


def matchDataFile(filePath: str, formatRegex: str):
    with open(filePath, 'r') as file:
        content = file.read()
    match = regex.match(formatRegex, content)
    assert match is not None, f'File "{filePath}" contents do not match given format.'
    return match


def findRelativeDifference(values: np.ndarray, controlValues: np.ndarray, threshold: float):
    return np.where(controlValues > threshold, np.divide(controlValues - values, controlValues, where=(controlValues != 0)), 0)


if __name__ == '__main__':
    someList = np.array([0, 0.1, 0.2, 0.5, 1, 0.8, 0.9, 0.6, 0.3, 0.1, 0, 0, 0])
    someSlice = sliceThreshold(someList, relativeThreshold=0.3)
    newList = someList[someSlice]
    print(newList)
