import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from noise import pnoise2
import random

# Paramètres de la simulation
grid_size = 25
temp_variation = 0.1
random_temp_variation = 0.2
update_interval = 10

# Position initiale et température du point stable
stable_point = [grid_size // 2, grid_size // 2]
stable_temp = 40


def initialize_temperature_grid(size, scale=0.1):
    # Générer un décalage aléatoire pour chaque exécution
    offset_x, offset_y = random.uniform(0, 100), random.uniform(0, 100)
    grid = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            # Appliquer le décalage aléatoire dans les coordonnées du bruit
            grid[i][j] = pnoise2(i * scale + offset_x, j * scale + offset_y) * 20 + 25
    return grid


def calculate_wind(temperature_grid):
    grad_x, grad_y = np.gradient(-temperature_grid)
    return grad_x, grad_y


# Mise à jour de la grille de température pour simuler la convection
def update_temperature(temperature_grid):
    new_grid = temperature_grid.copy()
    for i in range(1, grid_size - 1):
        for j in range(1, grid_size - 1):
            if [i, j] == stable_point:
                continue  # Ignorer le point stable

            # Diffusion avec convection et variation aléatoire
            new_grid[i, j] += temp_variation * (
                temperature_grid[i - 1 : i + 2, j - 1 : j + 2].mean()
                - temperature_grid[i, j]
            )
            new_grid[i, j] += (random.random() - 0.5) * random_temp_variation

    # Appliquer la température fixe au point stable
    new_grid[stable_point[0], stable_point[1]] = stable_temp
    return new_grid


def on_key_press(event):
    global stable_temp, stable_point

    if event.key == "p":
        stable_temp += 1
    elif event.key == "m":
        stable_temp -= 1

    if event.key == "up" and stable_point[0] > 0:
        stable_point[0] -= 1
    elif event.key == "down" and stable_point[0] < grid_size - 1:
        stable_point[0] += 1
    elif event.key == "left" and stable_point[1] > 0:
        stable_point[1] -= 1
    elif event.key == "right" and stable_point[1] < grid_size - 1:
        stable_point[1] += 1


# Initialisation de la grille de température
temperature_grid = initialize_temperature_grid(grid_size)
X, Y = np.meshgrid(np.arange(grid_size), np.arange(grid_size))

# Initialisation de la figure
fig, ax = plt.subplots()
temp_plot = ax.imshow(temperature_grid, cmap="hot", interpolation="nearest")
wind_quiver = ax.quiver(X, Y, *calculate_wind(temperature_grid), color="blue", scale=30)


# Fonction d'animation
def animate(frame):
    global temperature_grid
    temperature_grid = update_temperature(temperature_grid)
    temp_plot.set_data(temperature_grid)

    grad_x, grad_y = calculate_wind(temperature_grid)
    wind_quiver.set_UVC(grad_x, grad_y)


# Configuration et démarrage de l'animation
ani = animation.FuncAnimation(fig, animate, interval=update_interval)
fig.canvas.mpl_connect("key_press_event", on_key_press)
plt.colorbar(temp_plot, ax=ax, orientation="vertical", label="Température (°C)")
plt.show()
