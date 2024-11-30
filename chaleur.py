import numpy as np
import matplotlib.pyplot as plt
import io
import time


class HeatSimulation3D:
    def __init__(self, width=30, height=30, diffusion_rate=0.2):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))
        self.diffusion_rate = diffusion_rate

    def simplified_perlin_noise(self):
        return np.random.normal(0, 0.001, (self.height, self.width))

    def update(self):
        new_grid = np.copy(self.grid)
        padded_grid = np.pad(self.grid, pad_width=1, mode='edge')

        for i in range(self.height):
            for j in range(self.width):
                center = padded_grid[i+1, j+1]
                north = padded_grid[i, j+1]
                south = padded_grid[i+2, j+1]
                east = padded_grid[i+1, j+2]
                west = padded_grid[i+1, j]

                if i == 0:
                    north = center
                elif i == self.height-1:
                    south = center
                if j == 0:
                    west = center
                elif j == self.width-1:
                    east = center

                laplacian = (north + south + east + west - 4 * center)
                new_grid[i, j] = center + self.diffusion_rate * laplacian

        if np.random.random() < 1:
            new_grid += self.simplified_perlin_noise()

        self.grid = np.clip(new_grid * 0.999, 0, 1)

    def add_heat_source(self, x, y, temperature=1.0, radius=3):
        y_indices, x_indices = np.ogrid[-radius:radius+1, -radius:radius+1]
        distances = np.sqrt(x_indices*x_indices + y_indices*y_indices)

        sigma = radius/2
        heat_distribution = temperature * np.exp(-(distances**2)/(2*sigma**2))

        y_start = max(0, y-radius)
        y_end = min(self.height, y+radius+1)
        x_start = max(0, x-radius)
        x_end = min(self.width, x+radius+1)

        heat_section = heat_distribution[
            radius-(y-y_start):radius+(y_end-y),
            radius-(x-x_start):radius+(x_end-x)
        ]

        current_section = self.grid[y_start:y_end, x_start:x_end]
        self.grid[y_start:y_end, x_start:x_end] = np.maximum(current_section,
                                                             heat_section)

    def visualize_3d(self, ax=None):

        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
        else:
            ax.clear()

        x = np.arange(0, self.width, 1)
        y = np.arange(0, self.height, 1)
        X, Y = np.meshgrid(x, y)

        surf = ax.plot_surface(
            X,
            Y,
            self.grid,
            cmap='hot',
            linewidth=0,
            antialiased=True)

        ax.set_zlim(0, 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Température')
        plt.title("Simulation de chaleur 3D")
        return surf


def generate_frame():

    sim = HeatSimulation3D(30, 30, diffusion_rate=0.15)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    sim.add_heat_source(15, 15, temperature=1.0, radius=4)
    sim.add_heat_source(10, 10, temperature=0.8, radius=3)
    sim.add_heat_source(20, 20, temperature=0.6, radius=3)

    num_iterations = 600
    for _ in range(num_iterations):

        sim.update()

        ax.clear()
        sim.visualize_3d(ax)

        buf = io.BytesIO()
        plt.savefig(buf, format='jpeg', bbox_inches='tight')
        buf.seek(0)

        frame = buf.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        buf.close()

        time.sleep(0.04)
