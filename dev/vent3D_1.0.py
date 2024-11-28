import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from noise import pnoise3
import random

# Paramètres de la grille
grid_size = 5
scale = 0.1
s = None
rs = None

# Générer une grille de pression en 3D
def initialize_pressure_grid_3d(size, scale=0.1):
    offset_x, offset_y, offset_z = (
        random.uniform(0, 100),
        random.uniform(0, 100),
        random.uniform(0, 100),
    )
    grid = np.zeros((size, size, size))
    for i in range(size):
        for j in range(size):
            for k in range(size):
                grid[i][j][k] = (
                    pnoise3(
                        i * scale + offset_x, j * scale + offset_y, k * scale + offset_z
                    )
                    * 45
                )
    return grid


# Calcul des gradients (vent simulé) en 3D
def calculate_wind_3d(pressure_grid):
    grad_x, grad_y, grad_z = np.gradient(-pressure_grid)
    return grad_x, grad_y, grad_z


# Initialiser la grille de pression et les gradients de vent
pressure_grid = initialize_pressure_grid_3d(grid_size)
grad_x, grad_y, grad_z = calculate_wind_3d(pressure_grid)

# Préparation de la figure en 3D
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

# Créer les coordonnées pour chaque point de la grille
x, y, z = np.meshgrid(np.arange(grid_size), np.arange(grid_size), np.arange(grid_size))

# Appliquer des couleurs en fonction de la pression
norm = plt.Normalize(vmin=pressure_grid.min(), vmax=pressure_grid.max())
colors = cm.plasma(norm(pressure_grid))  # Choix d'une palette colorée

# Afficher les cubes de pression
for i in range(grid_size):
    for j in range(grid_size):
        for k in range(grid_size):
            ax.bar3d(i, j, k, dx=1, dy=1, dz=1, color=colors[i, j, k], alpha=0.1)

# Ajouter les vecteurs de vent en 3D
ax.quiver(x, y, z, grad_x, grad_y, grad_z, color="cyan", length=0.7, normalize=True)


ax.axis("off")
plt.show()
