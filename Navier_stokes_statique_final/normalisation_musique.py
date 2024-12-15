import string as st
import random as rd
import numpy as np
import librosa


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

def tempo_to_tuple(segment, sr):
    """
    Convertit le tempo extrait par librosa.beat.beat_track en un tuple (int, int) avec une variation de ±1.

    Parameters:
        segment (ndarray): Signal audio.
        sr (int): Fréquence d'échantillonnage du signal audio.

    Returns:
        tuple: Un tuple contenant le tempo (±1).
    """
    # Extraction du tempo
    tempo, _ = librosa.beat.beat_track(y=segment, sr=sr)

    # Conversion en tuple avec variation de ±1
    tempo_tuple = (int(tempo) - 1, int(tempo) + 1)

    return tempo_tuple

def analyze_audio(file_path):
    # Charger l'audio
    y, sr = librosa.load(file_path)

    # Durée totale en secondes
    duration = librosa.get_duration(y=y, sr=sr)
    tenth_seconds = int(duration * 10)

    # Liste pour stocker les résultats
    results_per_half_second = []

    # Analyser l'audio toutes les 0.5 secondes
    max_energy = 0.0  # Pour suivre la valeur max d'intensité sonore
    for i in range(tenth_seconds):
        # Extraire un segment de 0.5 seconde
        start_sample = int(i * sr / 10)
        end_sample = int((i + 1) * sr / 10)
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

        # Ajouter les résultats bruts pour ce segment de 0.5 seconde
        results_per_half_second.append({
            'tempo': tempo,
            'key': key,
            'intensity': energy,
            'rhythm': rhythm_complexity
        })

    # Normalisation des résultats
    normalized_results = []
    for result in results_per_half_second:
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
            normalized_tempo, # Int tempo
            tonalite_tuple,  # Tuple tonalité
            float(normalized_rhythm),   # Float intensité
            float(normalized_intensity)    # Float rythme
        ])
    normalized_results.append(len(normalized_results))

    return normalized_results