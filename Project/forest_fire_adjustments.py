import numpy as np
import matplotlib

from mapLoading import loadFromImage

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from PIL import Image

# Create a forest fire animation based on a simple cellular automaton model.
# The maths behind this code is described in the scipython blog article
# at https://scipython.com/blog/the-forest-fire-model/
# Christian Hill, January 2016.
# Updated January 2020.

# Displacements from a cell to its eight nearest neighbours
neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))
EMPTY, TREE, FIRE, WALL, EXIT = 0, 1, 2, 3, 4

# Colours for visualization: brown for EMPTY, dark green for TREE and orange
# for FIRE. Note that for the colormap to work, this list and the bounds list
# must be one larger than the number of different values in the array.
colors_list = [(0.2, 0, 0), 'grey', 'orange', 'white', (0, 1, 0), 'pink']
cmap = colors.ListedColormap(colors_list)
bounds = [0,1,2,3,4,5]
norm = colors.BoundaryNorm(bounds, cmap.N)

def iterate(X, i):
    """Iterate the forest according to the forest-fire rules."""

    # The boundary of the forest is always empty, so only consider cells
    # indexed from 1 to nx-2, 1 to ny-2
    X1 = np.zeros((ny, nx))
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            if X[iy,ix] == WALL:
                X1[iy,ix] = WALL
            if X[iy,ix] == TREE:
                X1[iy,ix] = TREE
                for dx,dy in neighbourhood:
                    # The diagonally-adjacent trees are further away, so
                    # only catch fire with a reduced probability:
                    if abs(dx) == abs(dy) and np.random.random() < 0.573:
                        continue
                    if X[iy+dy,ix+dx] == FIRE:
                        X1[iy,ix] = FIRE
                        break
            if X[iy,ix] == FIRE:
                if np.random.random() <= 0.005:
                    X1[iy,ix] = EMPTY
                else:
                    X1[iy,ix] = FIRE
                for dx,dy in neighbourhood:
                    if X[iy+dy,ix+dx] == EMPTY:
                        if np.random.random() <= 0.05:
                            X1[iy,ix] = EMPTY
            if X[iy,ix] == EMPTY:
                for dx,dy in neighbourhood:
                    if X[iy + dy, ix + dx] == FIRE and np.random.random() <= 0.02:
                        X1[iy,ix] = FIRE

    return X1


# load in the map
image_path = 'maps/baseline.png'
X = loadFromImage(image_path, (5, 5))
ny, nx = X.shape



fig = plt.figure(figsize=(25/3, 6.25))
ax = fig.add_subplot(111)
ax.set_axis_off()
im = ax.imshow(X, cmap=cmap, norm=norm)

# The animation function: called to produce a frame for each generation.
def animate(i):
    im.set_data(animate.X)
    animate.X = iterate(animate.X, i)
# Bind our grid to the identifier X in the animate function's namespace.
animate.X = X

# Interval between frames (ms).
interval = 100
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
plt.show()

