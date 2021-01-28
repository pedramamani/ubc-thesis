import numpy as np
import matplotlib.pyplot as plt
from config import *
from seaborn import color_palette
from process_methods import *


if __name__ == '__main__':
    image_count = 0
    ion_count = 0
    true_ion_count = 0
    colormap = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH))

    for file in os.listdir(str(ASSETS_DIR)):
        # coords = process_threshold(str(ASSETS_DIR / file))
        coords = process_optimized(str(ASSETS_DIR / file))

        for x, y in coords:
            colormap[y][x] += 1

        image_count += 1
        ion_count += len(coords)
        print(image_count)

    colormap = np.where(colormap > 5, 0, colormap)

    # histogram = colormap.flatten()
    # histogram = histogram[histogram != 0]
    # # plt.hist(histogram, density=False, bins=50)
    # # plt.xlabel('Ion Detections')
    # # plt.ylabel('Count')
    # # plt.yscale('log')
    # # plt.show()

    print(f'Average {ion_count / image_count:.1f} ions detected per image.')
    with color_palette('husl'):
        plt.imshow(colormap)
        plt.title('Ion Detections')
        plt.colorbar()
        plt.show()
