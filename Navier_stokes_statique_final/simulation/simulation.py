import string as st
import random as rd
import librosa
from Navier_stokes_statique_final.normalisation_musique_bis2 import analyze_audio
from Navier_stokes_statique_final.perturbation import *
from Navier_stokes_statique_final.fluid_simulation import *

sim = FluidSimulation(size=70)
center = sim.size // 2

file_path = "musique/Katyusha.mp3"
results = analyze_audio(file_path)

# Perturbation
for i in range(len(results)-1):
    val_position = (center, center)
    val_radius = int(results[i][0]) # Int
    val_strength = results[i][3] # Float
    val_vel_direction = results[i][1] # Tuple
    val_density = results[i][2] # Float
    sim.add_timed_perturbation(
        DirectionalPerturbation(
            position=val_position,
            radius=val_radius,
            strength=val_strength,
            velocity_direction=val_vel_direction,
            density_value=val_density,
            activation_time = i
        )
    )

sim.apply_timed_perturbations()
viz = FluidVisualizer(sim)
print("Génération de la vidéo de densité...")
viz.save_animation('fd_n3_Katyusha.mp4', frames=results[-1])