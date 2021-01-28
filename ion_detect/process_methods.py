import numpy as np
import cv2 as cv
from config import *
import imutils


def process_threshold(image_file, delay=0, debug=False):
    image = cv.imread(image_file, 0)  # read image as grayscale
    peak_indices = np.argpartition(image.flatten(), -COUNT_PEAKS)[-COUNT_PEAKS:]
    ion_coords = []

    for peak_index in peak_indices:
        x, y = peak_index % IMAGE_WIDTH, peak_index // IMAGE_WIDTH
        peak_intensity = image[y][x]

        if (peak_intensity > THRESHOLD_PEAK) and (0 < y < IMAGE_HEIGHT - 1) and (0 < x < IMAGE_WIDTH - 1):
            skirt_intensities = np.array([image[y + i][x + j] for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]])
            if all(skirt_intensities > THRESHOLD_SKIRT) and np.average(skirt_intensities) > THRESHOLD_AVERAGE:
                ion_coords.append((x, y))
                if debug:
                    print(f'Ion detected at ({x}, {y}) with peak intensity {peak_intensity},')
                    print(f'skirt intensities {skirt_intensities} and average {np.average(skirt_intensities):.0f}.\n')

    if debug:
        for ion_coord in ion_coords:
            cv.circle(image, ion_coord, 3, 255, 1)
        cv.imshow('Detection', image)
        cv.waitKey(delay)

    return ion_coords


def process_optimized(image_file, delay=0, debug=False):
    image = cv.imread(image_file, 0)  # read image as grayscale

    bilateral = cv.bilateralFilter(image, 4, 90, 2)
    _, threshold = cv.threshold(bilateral, 30, 255, cv.THRESH_TOZERO)
    ion_coords = _find_coords(threshold)
    ion_coords.extend(ion_coords)

    if debug:
        for ion_coord in ion_coords:
            cv.circle(image, ion_coord, 3, 255, 1)
        cv.imshow('Detection', image)
        cv.waitKey(delay)

    return ion_coords


def _find_coords(image):
    image = cv.dilate(image, np.ones((3, 3), np.uint8))
    contours = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    coords = []

    for contour in contours:
        M = cv.moments(contour)
        if M["m00"] != 0:
            coords.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
    return coords
