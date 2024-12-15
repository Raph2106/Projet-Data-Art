from Navier_stokes_statique_final.perturbation import *
from Navier_stokes_statique_final.fluid_simulation import *

# Création de la simulation
sim = FluidSimulation(size=70)

center = sim.size // 2

# Perturbation
sim.add_timed_perturbation(
    DirectionalPerturbation(
        position=(25, center + 10),
        radius=8,
        strength=2.0,
        velocity_direction=(1, 0),
        density_value=1.0
    )
)

# Perturbation
sim.add_timed_perturbation(
    DirectionalPerturbation(
        position=(45, center - 10),
        radius=8,
        strength=2.0,
        velocity_direction=(-1, 0),
        density_value=1.0
    )
)

# continue
sim.add_timed_perturbation(
    DirectionalPerturbation(
        position=(center, 45),
        radius=3,
        strength=0.5,
        velocity_direction=(0, -1),
        density_value=0.5,
    )
)

# continue
sim.add_timed_perturbation(
    DirectionalPerturbation(
        position=(center, 25),
        radius=3,
        strength=0.1,
        velocity_direction=(0, 1),
        density_value=0.5
    )
)

# Application des perturbations initiales
sim.apply_timed_perturbations()
viz = FluidVisualizer(sim)
print("Génération de la vidéo de densité...")
viz.save_animation('test.mp4', frames=300)