import numpy as np
from PIL import Image

EMPTY, TREE, FIRE, WALL, EXIT = 0, 1, 2, 3, 4

# create the grid from some image
# if many values become empty the color profile might not be set correctly
# for testing sRGB was used and the image was saved as PNG24
def loadFromImage(path, source=None):
    image = Image.open(path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image_array = np.array(image)
    mapping = {(0, 0, 0): 0,
               (200, 200, 200): 1,
               (255, 255, 255): 3,
               (255, 0, 0): 2,}
    default_value = 0
    mapped_array = np.apply_along_axis(
        lambda pixel: mapping.get(tuple(pixel), default_value), 2, image_array
    )

    if source is not None:
        mapped_array[source[0]][source[1]] = 2
    return mapped_array

# create the grid from a txt file
def loadFromfile(path, source=None):
    grid = np.loadtxt(path)
    if source is not None:
        grid[source[0]][source[1]] = 2
    return grid

