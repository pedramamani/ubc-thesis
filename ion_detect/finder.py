import cv2
import imutils
import numpy as np


class Finder:
    def __init__(self):
        pass

    def find_coords(self, image):
        image = cv2.dilate(image, np.ones((3, 3), np.uint8))
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        coords = []

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                coords.append((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
        return coords

    def plot_cmap(self):
        image_count = 0
        ion_count = 0
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