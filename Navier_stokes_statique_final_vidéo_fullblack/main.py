from perturbation import *
from fluid_simulation import *

# Création de la simulation
sim = FluidSimulation(size=70)

center = sim.size // 2

# Perturbation avec mouvement vers la droite, démarrant à t=0
sim.add_initial_perturbation(
    DirectionalPerturbation(
        position=(20, center),
        radius=8,
        strength=2.0,
        velocity_direction=(1, 0),
        density_value=1.0,
        start_time=0,
        duration=5  # Active pendant 5 unités de temps
    )
)

# Perturbation avec mouvement diagonal, démarrant à t=2
sim.add_initial_perturbation(
    DirectionalPerturbation(
        position=(center, 20),
        radius=8,
        strength=2.0,
        velocity_direction=(1, 1),
        density_value=1.0,
        start_time=2,  # Commence 2 unités de temps après le début
        duration=3  # Active pendant 3 unités de temps
    )
)

# Perturbation continue au centre
sim.add_continuous_perturbation(
    DirectionalPerturbation(
        position=(center, center),
        radius=3,
        strength=0.5,
        velocity_direction=(0, -1),
        density_value=0.5,
        start_time=0,
        duration=10  # Active pendant 10 unités de temps
    )
)

# Application des perturbations initiales
sim.apply_initial_perturbations()

# Visualisation et génération des vidéos
viz = FluidVisualizer(sim)

# Générer une vidéo pour la densité
print("Génération de la vidéo de densité...")
viz.save_animation('fluid_density.gif', frames=300)

# Réinitialiser la simulation pour une nouvelle génération
sim = FluidSimulation(size=70)

# Recharger les perturbations
sim.add_initial_perturbation(
    DirectionalPerturbation(
        position=(20, center),
        radius=8,
        strength=2.0,
        velocity_direction=(1, 0),
        density_value=1.0,
        start_time=0,
        duration=5
    )
)

sim.add_initial_perturbation(
    DirectionalPerturbation(
        position=(center, 20),
        radius=8,
        strength=2.0,
        velocity_direction=(1, 1),
        density_value=1.0,
        start_time=2,
        duration=3
    )
)

sim.add_continuous_perturbation(
    DirectionalPerturbation(
        position=(center, center),
        radius=3,
        strength=0.5,
        velocity_direction=(0, -1),
        density_value=0.5,
        start_time=0,
        duration=10
    )
)

sim.apply_initial_perturbations()

# Recréer la visualisation avec la nouvelle simulation
viz = FluidVisualizer(sim)

# Générer une vidéo pour la magnitude de la vitesse
print("Génération de la vidéo de magnitude de vitesse...")
viz.save_animation('fluid_velocity_magnitude.mp4', frames=300)

print("Génération des vidéos terminée.")