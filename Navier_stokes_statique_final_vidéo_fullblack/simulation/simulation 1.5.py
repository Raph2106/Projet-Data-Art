import pickle
import string as st
import random as rd
import librosa
from Navier_stokes_statique_final_vidéo.perturbation import *
from Navier_stokes_statique_final_vidéo.fluid_simulation import *

sim = FluidSimulation(size=70)
center = sim.size // 2
def generer_code_aleatoire(taille=6):
    caracteres = st.ascii_letters + st.digits
    return ''.join(rd.choice(caracteres) for _ in range(taille))

def normalize_value(value, min_value, max_value, target_min, target_max):
    """Normalise une valeur entre une plage cible."""
    return ((value - min_value) / (max_value - min_value)) * (target_max - target_min) + target_min

def tonalite_to_tuple(key):
    """Convertit une tonalité en tuple (int, int) (+-1, +-1)."""
    mapping = {
        'C': (1, 1), 'C#': (1, -1), 'D': (1, 1), 'D#': (1, -1),
        'E': (1, 1), 'F': (-1, 1), 'F#': (-1, -1), 'G': (-1, 1),
        'G#': (-1, -1), 'A': (1, 1), 'A#': (1, -1), 'B': (1, 1)
    }
    return mapping.get(key, (0, 0))  # Par défaut (0, 0) si tonalité inconnue

def analyze_audio_per_second(file_path):
    # Charger l'audio
    y, sr = librosa.load(file_path)

    # Durée totale en secondes
    duration = int(librosa.get_duration(y=y, sr=sr))

    # Liste pour stocker les résultats
    results_per_second = []

    # Analyser l'audio seconde par seconde
    max_energy = 0.0  # Pour suivre la valeur max d'intensité sonore
    for i in range(duration):
        # Extraire un segment de 1 seconde
        start_sample = i * sr
        end_sample = (i + 1) * sr
        segment = y[start_sample:end_sample]

        # Calculer le tempo
        tempo, _ = librosa.beat.beat_track(y=segment, sr=sr)

        # Calculer la tonalité dominante (Chromagram)
        chroma = librosa.feature.chroma_cqt(y=segment, sr=sr)
        key_index = np.argmax(np.mean(chroma, axis=1))
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_index]

        # Calculer l'intensité sonore
        energy = float(np.sum(segment**2))
        max_energy = max(max_energy, energy)  # Suivre l'énergie maximale pour la normalisation

        # Extraire les battements pour la signature rythmique
        _, beat_frames = librosa.beat.beat_track(y=segment, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        rhythm_complexity = float(len(beat_times))  # Complexité rythmique = nombre de battements

        # Ajouter les résultats bruts pour cette seconde
        results_per_second.append({
            'tempo': tempo,
            'key': key,
            'intensity': energy,
            'rhythm': rhythm_complexity
        })

    # Normalisation des résultats
    normalized_results = []
    for result in results_per_second:
        # Normaliser le tempo entre 0 et 10 (arrondi à l'entier)
        normalized_tempo = int(normalize_value(result['tempo'], 40, 200, 0, 10))  # Supposons une plage de tempo raisonnable [40, 200]

        # Convertir la tonalité en tuple (int, int)
        tonalite_tuple = tonalite_to_tuple(result['key'])

        # Normaliser l'intensité sonore entre 0 et 5
        normalized_intensity = normalize_value(result['intensity'], 0.0, max_energy, 0.0, 5.0)

        # Normaliser la signature rythmique entre 0 et 2
        normalized_rhythm = normalize_value(result['rhythm'], 0.0, 10.0, 0.0, 2.0)  # Supposons une plage de battements max à 10

        # Ajouter les résultats normalisés
        normalized_results.append([
            normalized_tempo,               # Int tempo
            tonalite_tuple,                 # Tuple tonalité
            float(normalized_intensity),    # Float intensité
            float(normalized_rhythm)        # Float rythme
        ])

    return normalized_results

file_path = "Stupeflip_Vite.mp3"
results = analyze_audio_per_second(file_path)

# Perturbation
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
            strength=val_strength-0.5,
            velocity_direction=val_vel_direction,
            density_value=val_density-0.2,
            activation_time = i
        )
    )

nom_de_base = "val_perturbation_musique"
code_aleatoire = generer_code_aleatoire()
nom_fichier = f"{nom_de_base}_{code_aleatoire}.csv"

with open("Stupeflip_Vite_1s", "wb") as fichier:
    pickle.dump(results, fichier)


# Application des perturbations initiales
sim.apply_initial_perturbations()

# Visualisation
viz = FluidVisualizer(sim)
viz.animate()
