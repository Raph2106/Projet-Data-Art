import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


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
        padded_grid = np.pad(self.grid, pad_width=1, mode="edge")

        for i in range(self.height):
            for j in range(self.width):
                center = padded_grid[i + 1, j + 1]
                north = padded_grid[i, j + 1]
                south = padded_grid[i + 2, j + 1]
                east = padded_grid[i + 1, j + 2]
                west = padded_grid[i + 1, j]

                if i == 0:
                    north = center
                elif i == self.height - 1:
                    south = center
                if j == 0:
                    west = center
                elif j == self.width - 1:
                    east = center

                laplacian = north + south + east + west - 4 * center
                new_grid[i, j] = center + self.diffusion_rate * laplacian

        #    if np.random.random() < 1:
        #        new_grid += self.simplified_perlin_noise()

        self.grid = np.clip(new_grid * 0.999, 0, 1)

    def add_heat_source(self, x, y, temperature=1.0, radius=3):
        y_indices, x_indices = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        distances = np.sqrt(x_indices * x_indices + y_indices * y_indices)

        sigma = radius / 2
        heat_distribution = temperature * np.exp(-(distances**2) / (2 * sigma**2))

        y_start = max(0, y - radius)
        y_end = min(self.height, y + radius + 1)
        x_start = max(0, x - radius)
        x_end = min(self.width, x + radius + 1)

        heat_section = heat_distribution[
            radius - (y - y_start) : radius + (y_end - y),
            radius - (x - x_start) : radius + (x_end - x),
        ]

        current_section = self.grid[y_start:y_end, x_start:x_end]
        self.grid[y_start:y_end, x_start:x_end] = np.maximum(
            current_section, heat_section
        )

    def visualize_2d(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()
        cax = ax.imshow(self.grid, cmap="hot", origin="lower", interpolation="nearest")
        ax.axis("off")
        return cax


class HeatSimulation3DfromClaude:
    def __init__(self, width=30, height=30, diffusion_rate=0.2, value_limit=1.0):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))
        self.diffusion_rate = diffusion_rate
        self.value_limit = value_limit

        self.center_x = width // 2
        self.center_y = height // 2

    def update(self):
        new_grid = np.copy(self.grid)
        padded_grid = np.pad(self.grid, pad_width=1, mode="edge")

        for i in range(self.height):
            for j in range(self.width):
                center = padded_grid[i + 1, j + 1]
                north = padded_grid[i, j + 1]
                south = padded_grid[i + 2, j + 1]
                east = padded_grid[i + 1, j + 2]
                west = padded_grid[i + 1, j]

                if i == 0:
                    north = center
                elif i == self.height - 1:
                    south = center
                if j == 0:
                    west = center
                elif j == self.width - 1:
                    east = center

                laplacian = north + south + east + west - 4 * center
                new_grid[i, j] = center + self.diffusion_rate * laplacian

        self.grid = np.clip(new_grid * 0.999, -self.value_limit, self.value_limit)

    def add_heat_source(self, x, y, temperature=1.0, radius=3):
        x = self.center_x + x
        y = self.center_y + y

        x = min(max(x, radius), self.width - radius - 1)
        y = min(max(y, radius), self.height - radius - 1)

        y_indices, x_indices = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        distances = np.sqrt(x_indices**2 + y_indices**2)
        sigma = radius / 2
        heat_distribution = temperature * np.exp(-(distances**2) / (2 * sigma**2))

        y_start = max(0, y - radius)
        y_end = min(self.height, y + radius + 1)
        x_start = max(0, x - radius)
        x_end = min(self.width, x + radius + 1)

        dist_y_start = radius - (y - y_start)
        dist_y_end = radius + (y_end - y)
        dist_x_start = radius - (x - x_start)
        dist_x_end = radius + (x_end - x)

        if (y_end - y_start) <= 0 or (x_end - x_start) <= 0:
            return

        heat_section = heat_distribution[
            dist_y_start:dist_y_end, dist_x_start:dist_x_end
        ]
        current_section = self.grid[y_start:y_end, x_start:x_end]

        if heat_section.shape != current_section.shape:
            return

        if temperature >= 0:
            self.grid[y_start:y_end, x_start:x_end] = np.maximum(
                current_section, heat_section
            )
        else:
            self.grid[y_start:y_end, x_start:x_end] = np.minimum(
                current_section, heat_section
            )

    def visualize_2d(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        ax.clear()

        cax = ax.imshow(
            self.grid,
            cmap="RdBu_r",
            origin="lower",
            interpolation="nearest",
            vmin=-self.value_limit,
            vmax=self.value_limit,
        )
        ax.axis("off")
        return cax
