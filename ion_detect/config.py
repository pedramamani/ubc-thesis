import os
import pathlib

ASSETS_DIR = pathlib.Path(os.path.dirname(__file__)) / 'assets'

COUNT_PEAKS = 25
THRESHOLD_PEAK = 80
THRESHOLD_AVERAGE = 20
THRESHOLD_SKIRT = 2

IMAGE_HEIGHT = 408
IMAGE_WIDTH = 400
