import numpy as np
import librosa

import numpy as np

import numpy as np
import librosa


def normalize_frequency(features):
    min_val = np.min(features)
    max_val = np.max(features)
    normalized = 10 * (features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))


def normalize_rhythm_and_tempo(key, tempo):
    tempo_normalized = 1 if tempo > 120 else -1
    mapping = {
        'C': (tempo_normalized, 1), 'C#': (tempo_normalized, -1), 'D': (tempo_normalized, 1),
        'D#': (tempo_normalized, -1),
        'E': (tempo_normalized, 0), 'F': (tempo_normalized, 1), 'F#': (tempo_normalized, -1),
        'G': (tempo_normalized, 1),
        'G#': (tempo_normalized, -1), 'A': (tempo_normalized, 1), 'A#': (tempo_normalized, -1),
        'B': (tempo_normalized, 0)
    }
    return mapping.get(key, (tempo_normalized, 0))


def normalize_melodic_features(melodic_features):
    min_val = np.min(melodic_features)
    max_val = np.max(melodic_features)
    normalized = 2 * (melodic_features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))


def normalize_spectral_features(spectral_features):
    min_val = np.min(spectral_features)
    max_val = np.max(spectral_features)
    normalized = 3 * (spectral_features - min_val) / (max_val - min_val)
    return float(np.mean(normalized))


def analyze_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    total_samples = len(y)
    main_hop_length = int(sr * 1.0)  # 1 second
    transition_hop_length = int(sr * 0.2)  # 0.2 seconds

    results = []

    for i in range(0, total_samples, main_hop_length):
        # Extract main 1-second sample
        main_segment = y[i:i + main_hop_length]
        if len(main_segment) == 0:
            continue

        # Extract features for the main segment
        spectral_centroid = librosa.feature.spectral_centroid(y=main_segment, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=main_segment, sr=sr)
        chroma = librosa.feature.chroma_cqt(y=main_segment, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=main_segment, sr=sr)
        key_index = np.argmax(np.mean(chroma, axis=1))
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_index]

        # Apply normalizations
        freq_norm = normalize_frequency(spectral_centroid)
        rhythm_tempo_norm = normalize_rhythm_and_tempo(key, tempo)
        melodic_norm = normalize_melodic_features(chroma)
        spectral_norm = normalize_spectral_features(spectral_contrast)

        # Add main segment result
        results.append([freq_norm, rhythm_tempo_norm, round(melodic_norm, 1), round(spectral_norm, 1)])

        # Add transition segments
        for j in range(5):  # 5 transition segments of 0.2 seconds each
            start = i + int(j * transition_hop_length)
            transition_segment = y[start:start + transition_hop_length]
            if len(transition_segment) == 0:
                continue

            spectral_centroid = librosa.feature.spectral_centroid(y=transition_segment, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=transition_segment, sr=sr)
            chroma = librosa.feature.chroma_cqt(y=transition_segment, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=transition_segment, sr=sr)
            key_index = np.argmax(np.mean(chroma, axis=1))
            key = keys[key_index]

            freq_norm = normalize_frequency(spectral_centroid)
            rhythm_tempo_norm = normalize_rhythm_and_tempo(key, tempo)
            melodic_norm = normalize_melodic_features(chroma)
            spectral_norm = normalize_spectral_features(spectral_contrast)

            results.append([freq_norm, rhythm_tempo_norm, round(melodic_norm, 1), round(spectral_norm, 1)])

    results.append(len(results))  # Total number of results
    return results
