import jax
import jax.numpy as np

class Perturbation:
    def __init__(self, position, radius, strength, density_value=1.0, activation_time=0):
        """
        Initialize a perturbation with specific parameters

        Args:
            position (tuple): (x, y) center position of the perturbation
            radius (float): radius of influence
            strength (float): strength of the velocity field
            density_value (float): value to add to the density field
            activation_time (float): time step when the perturbation should be activated
        """
        self.position = position
        self.radius = radius
        self.strength = strength
        self.density_value = density_value
        self.activation_time = activation_time
        self.activated = False

    def should_activate(self, current_time):
        """
        Check if the perturbation should be activated at the current time step

        Args:
            current_time (float): Current time step of the simulation

        Returns:
            bool: Whether the perturbation should be activated
        """
        return not self.activated and current_time >= self.activation_time

    def apply(self, u, v, density, size):
        """Apply the perturbation to the velocity and density fields"""
        x_center, y_center = self.position

        for i in range(-self.radius, self.radius + 1):
            for j in range(-self.radius, self.radius + 1):
                dist = np.sqrt(i * i + j * j)
                if dist <= self.radius:
                    x, y = x_center + i, y_center + j
                    if 0 <= x < size and 0 <= y < size:
                        angle = np.arctan2(j, i)
                        u[x, y] += self.strength * -np.sin(angle)
                        v[x, y] += self.strength * np.cos(angle)
                        density[x, y] += self.density_value


class DirectionalPerturbation(Perturbation):
    def __init__(self, position, radius, strength, velocity_direction, density_value=1.0, activation_time=0):
        """
        Initialize a directional perturbation

        Args:
            position (tuple): (x, y) center position
            radius (float): radius of influence
            strength (float): strength of the velocity field
            velocity_direction (tuple): (vx, vy) direction vector
            density_value (float): value to add to the density field
            activation_time (float): time step when the perturbation should be activated
        """
        super().__init__(position, radius, strength, density_value, activation_time)
        # Normaliser le vecteur de direction
        vx, vy = velocity_direction
        magnitude = np.sqrt(vx ** 2 + vy ** 2)
        self.vx = vx / magnitude if magnitude > 0 else 0
        self.vy = vy / magnitude if magnitude > 0 else 0

    def apply(self, u, v, density, size):
        x_center, y_center = self.position

        for i in range(-self.radius, self.radius + 1):
            for j in range(-self.radius, self.radius + 1):
                dist = np.sqrt(i * i + j * j)
                if dist <= self.radius:
                    x, y = x_center + i, y_center + j
                    if 0 <= x < size and 0 <= y < size:
                        # Appliquer la vitesse directionnelle
                        u[x, y] += self.strength * self.vx
                        v[x, y] += self.strength * self.vy
                        density[x, y] += self.density_value


