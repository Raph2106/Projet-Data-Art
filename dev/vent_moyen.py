import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from noise import pnoise2
import random


grid_size = 40
temp_variation = 0.1
random_temp_variation = 0.2
update_interval = 100
update = True


def initialize_pressure_grid(size, scale=0.1):
    offset_x, offset_y = random.uniform(0, 100), random.uniform(0, 100)
    grid = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            grid[i][j] = pnoise2(i * scale + offset_x, j * scale + offset_y) * 20
    return grid


def calculate_wind(pressure_grid):
    grad_x, grad_y = np.gradient(-pressure_grid)
    return grad_x, grad_y


pressure_grid = initialize_pressure_grid(grid_size)
X, Y = np.meshgrid(np.arange(grid_size), np.arange(grid_size))

sns.set_theme(style="whitegrid")
palette = sns.color_palette("mako", as_cmap=True)

fig, ax = plt.subplots()
temp_plot = ax.imshow(pressure_grid, cmap=palette, interpolation="nearest")
wind_quiver = ax.quiver(
    X, Y, *calculate_wind(pressure_grid), color="deepskyblue", scale=50, alpha=0.8
)

plt.colorbar(temp_plot, ax=ax, orientation="vertical", label="Pression (Pa)")
plt.show()
