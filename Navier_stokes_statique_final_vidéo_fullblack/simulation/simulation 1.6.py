import pickle
import string as st
import random as rd
from Navier_stokes_statique_final_vidéo_fullblack.perturbation import *
from Navier_stokes_statique_final_vidéo_fullblack.fluid_simulation import *

sim = FluidSimulation(size=60)
center = sim.size // 2

with open("Vivaldi_Winter_tenth_second", "rb") as fichier:
    results = pickle.load(fichier)

for i in range(len(results)):
    val_position = (center, center)
    val_radius = results[i][0]
    val_strength = results[i][2]
    val_vel_direction = results[i][1]
    val_density = results[i][3]
    sim.add_timed_perturbation(
        DirectionalPerturbation(
            position=val_position,
            radius=val_radius,
            strength=val_strength-0.2,
            velocity_direction=val_vel_direction,
            density_value=val_density+0.1,
            activation_time = i
        )
    )

sim.apply_timed_perturbations()

# Visualisation et génération des vidéos
viz = FluidVisualizer(sim)

# Générer une vidéo pour la densité
print("Génération de la vidéo de densité...")
viz.save_animation('fluid_density_Vivaldi_Winter_tenth_second_fb.mp4', frames=2500)