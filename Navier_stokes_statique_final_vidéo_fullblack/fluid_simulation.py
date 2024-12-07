import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.switch_backend('TkAgg')

class FluidSimulation:
    def __init__(self, size=50):
        self.size = size
        self.dt = 0.3
        self.diff = 0.0005
        self.visc = 0.00005
        self.iterations = 20
        self.current_time = 0

        self.u = np.zeros((size, size))
        self.v = np.zeros((size, size))
        self.u_prev = np.zeros((size, size))
        self.v_prev = np.zeros((size, size))
        self.density = np.zeros((size, size))
        self.density_prev = np.zeros((size, size))

        self.initial_perturbations = []
        self.continuous_perturbations = []
        self.dynamic_perturbations = []
        self.timed_perturbations = []

    def add_timed_perturbation(self, perturbation):
        """Ajouter une perturbation déclenchée à un moment spécifique"""
        self.timed_perturbations.append(perturbation)

    def apply_timed_perturbations(self):
        """Appliquer les perturbations programmées si leur temps est venu"""
        for perturbation in self.timed_perturbations:
            if perturbation.should_activate(self.current_time):
                perturbation.apply(self.u, self.v, self.density, self.size)
                perturbation.activated = True
        self.timed_perturbations = [p for p in self.timed_perturbations if not p.activated]

    def step(self):
        self.current_time += self.dt

        # Sauvegarde des champs précédents
        self.u_prev, self.v_prev = self.u.copy(), self.v.copy()
        self.density_prev = self.density.copy()

        # Diffusion de la vitesse
        self.u = self.diffuse(self.u.copy(), self.u_prev, self.visc)
        self.v = self.diffuse(self.v.copy(), self.v_prev, self.visc)

        # Projection pour assurer l'incompressibilité
        self.u, self.v = self.project(self.u, self.v)

        # Advection de la vitesse
        self.u = self.advect(self.u_prev, self.u_prev, self.v_prev)
        self.v = self.advect(self.v_prev, self.u_prev, self.v_prev)

        # Projection finale
        self.u, self.v = self.project(self.u, self.v)

        # Transport de la densité
        self.density = self.diffuse(self.density.copy(), self.density_prev, self.diff)
        self.density = self.advect(self.density_prev, self.u, self.v)

        # Application des perturbations programmées
        self.apply_timed_perturbations()

    def project(self, u, v):
        div = np.zeros((self.size, self.size))
        p = np.zeros((self.size, self.size))

        # Calcul de la divergence
        div[1:-1, 1:-1] = (
                (u[2:, 1:-1] - u[:-2, 1:-1] +
                 v[1:-1, 2:] - v[1:-1, :-2])
                * (-0.5 / self.size)
        )

        # Résolution de l'équation de Poisson
        for k in range(self.iterations):
            p[1:-1, 1:-1] = (div[1:-1, 1:-1] +
                             p[2:, 1:-1] + p[:-2, 1:-1] +
                             p[1:-1, 2:] + p[1:-1, :-2]) / 4

        # Correction du champ de vitesse
        u[1:-1, 1:-1] -= 0.5 * self.size * (p[2:, 1:-1] - p[:-2, 1:-1])
        v[1:-1, 1:-1] -= 0.5 * self.size * (p[1:-1, 2:] - p[1:-1, :-2])

        return u, v

    def diffuse(self, field, prev_field, diff):
        a = self.dt * diff * self.size * self.size

        for k in range(self.iterations):
            field[1:-1, 1:-1] = (prev_field[1:-1, 1:-1] +
                                 a * (field[2:, 1:-1] + field[:-2, 1:-1] + field[1:-1, 2:] + field[1:-1, :-2])
                                 ) / (1 + 4 * a)
        return field

    def advect(self, field, u, v):
        new_field = np.zeros_like(field)
        dt0 = self.dt * self.size

        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                # Position de départ de la particule
                x = i - dt0 * u[i, j]
                y = j - dt0 * v[i, j]

                # Application des conditions aux limites
                x = np.clip(x, 0.5, self.size - 1.5)
                y = np.clip(y, 0.5, self.size - 1.5)

                # Interpolation bilinéaire
                i0 = int(x)
                j0 = int(y)
                i1 = i0 + 1
                j1 = j0 + 1

                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1

                new_field[i, j] = (
                        s0 * (t0 * field[i0, j0] + t1 * field[i0, j1]) +
                        s1 * (t0 * field[i1, j0] + t1 * field[i1, j1])
                )
        return new_field


class FluidVisualizer:
    def __init__(self, simulation):
        self.sim = simulation

        # Create a figure with no whitespace and black background
        self.fig = plt.figure(
            figsize=(8, 8),
            facecolor='black',
            edgecolor='none',
            frameon=False
        )

        # Create an axis that fills the entire figure with no padding
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_axis_off()  # Turn off all axis lines and labels
        self.ax.set_facecolor('black')

        # Initialize density visualization
        self.img_density = self.ax.imshow(
            self.sim.density,
            cmap='turbo',  # A grayscale colormap that works well with black background
            interpolation='bicubic',
            vmin=0,
            vmax=1.5,
            aspect='equal'  # Ensure square aspect ratio
        )

    def update(self, frame):
        self.sim.step()
        self.img_density.set_array(self.sim.density)
        return [self.img_density]

    def save_animation(self, filename='fluid_density.gif', frames=2500):
        """
        Save the animation with a clean, minimalist style

        Args:
            filename (str): Output filename
            frames (int): Number of frames to generate
        """
        anim = FuncAnimation(
            self.fig,
            self.update,
            frames=frames,
            interval=50
        )

        # Save as GIF for better compatibility
        anim.save(
            filename.replace('.mp4', '.gif'),
            writer='pillow',
            fps=60,
            savefig_kwargs={
                'facecolor': 'black',
                'edgecolor': 'none',
                'bbox_inches': 'tight',  # Remove any extra whitespace
                'pad_inches': 0  # No padding
            }
        )

        plt.close(self.fig)
        print(f"Animation saved as {filename.replace('.mp4', '.gif')}")