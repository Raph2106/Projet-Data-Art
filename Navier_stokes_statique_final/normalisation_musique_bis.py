import numpy as np
import librosa

import numpy as np


# 1. Normalisation des caractéristiques fréquentielles entre 0 et 10
def normalize_frequency(features):
    """
    Normalise les caractéristiques fréquentielles entre 0 et 10.
    :param features: Tableau des caractéristiques fréquentielles (ex : spectral_centroid).
    :return: Valeur normalisée entre 0 et 10.
    """
    min_val = np.min(features)
    max_val = np.max(features)
    normalized = 10 * (features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))  # Retourne une moyenne pour une seule valeur


# 2. Normalisation du rythme et du tempo en (-1, 1) pour former un tuple

def normalize_rhythm_and_tempo(key, tempo):
    """
    Normalise le tempo et les battements en -1 ou 1 et retourne un tuple.
    :param tempo: Tempo extrait (float).
    :param beats: Tableau des battements (onsets détectés).
    :return: Tuple (tempo_normalized, beats_normalized).
    """

    tempo_normalized = 1 if tempo > 120 else -1

    mapping = {
        'C': (tempo_normalized, 1), 'C#': (tempo_normalized, -1), 'D': (tempo_normalized, 1), 'D#': (tempo_normalized, -1),
        'E': (tempo_normalized, 0), 'F': (tempo_normalized, 1), 'F#': (tempo_normalized, -1), 'G': (tempo_normalized, 1),
        'G#': (tempo_normalized, -1), 'A': (tempo_normalized, 1), 'A#': (tempo_normalized, -1), 'B': (tempo_normalized, 0)
    }
    return mapping.get(key, (tempo_normalized, 0))  # Par défaut (0, 0) si tonalité inconnue


# 3. Normalisation des caractéristiques mélodiques entre 0 et 2
def normalize_melodic_features(melodic_features):
    """
    Normalise les caractéristiques mélodiques entre 0 et 2.
    :param melodic_features: Tableau des caractéristiques mélodiques (ex : chroma, pitches).
    :return: Valeur normalisée entre 0 et 2.
    """
    min_val = np.min(melodic_features)
    max_val = np.max(melodic_features)
    normalized = 2 * (melodic_features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))  # Retourne une moyenne pour une seule valeur


# 4. Normalisation des caractéristiques spectrales entre 0 et 5
def normalize_spectral_features(spectral_features):
    """
    Normalise les caractéristiques spectrales entre 0 et 5.
    :param spectral_features: Tableau des caractéristiques spectrales (ex : spectral_contrast, spectral_bandwidth).
    :return: Valeur normalisée entre 0 et 5.
    """
    min_val = np.min(spectral_features)
    max_val = np.max(spectral_features)
    normalized = 3 * (spectral_features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))  # Retourne une moyenne pour une seule valeur


# 5. Fonction générique pour normaliser un tableau dans une plage donnée
def normalize_generic(features, range_min, range_max):
    """
    Normalise un tableau de caractéristiques dans une plage donnée.
    :param features: Tableau des caractéristiques.
    :param range_min: Valeur minimale de la plage cible.
    :param range_max: Valeur maximale de la plage cible.
    :return: Tableau normalisé dans la plage [range_min, range_max].
    """
    min_val = np.min(features)
    max_val = np.max(features)
    normalized = range_min + (range_max - range_min) * (features - min_val) / (max_val - min_val)
    return normalized


# 6. Analyse audio par tranche de 0.1 seconde
def analyze_audio(audio_path):
    """
    Découpe l'audio en tranches de 0.1 seconde et analyse chaque tranche.
    :param audio_path: Chemin vers le fichier audio.
    :return: Liste de listes contenant les résultats des normalisations par tranche et le nombre total de tranches.
    """
    # Charger l'audio
    y, sr = librosa.load(audio_path, sr=None)
    total_samples = len(y)
    hop_length = int(sr * 0.1)  # Nombre d'échantillons pour 0.1s

    # Initialisation de la liste des résultats
    results = []

    for i in range(0, total_samples, hop_length):
        # Extraire le segment de 0.1 seconde
        segment = y[i:i + hop_length]

        # Vérifier que le segment n'est pas vide
        if len(segment) == 0:
            continue

        # Extraire les caractéristiques
        spectral_centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)
        tempo, beats = librosa.beat.beat_track(y=segment, sr=sr)
        chroma = librosa.feature.chroma_stft(y=segment, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=segment, sr=sr)
        # Calculer la tonalité dominante (Chromagram)
        chroma = librosa.feature.chroma_cqt(y=segment, sr=sr)
        key_index = np.argmax(np.mean(chroma, axis=1))
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_index]

        # Appliquer les normalisations
        freq_norm = normalize_frequency(spectral_centroid) #range
        rhythm_tempo_norm = normalize_rhythm_and_tempo(key, tempo) #direct
        melodic_norm = normalize_melodic_features(chroma) #density
        spectral_norm = normalize_spectral_features(spectral_contrast) #stren

        # Ajouter les résultats
        results.append([freq_norm, rhythm_tempo_norm, round(melodic_norm,1), round(spectral_norm],1)])

    # Ajouter le nombre total de tranches comme dernier élément
    results.append(len(results))
    return results
