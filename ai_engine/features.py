import librosa
import numpy as np
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def extract_features(y):
    """
    Extract features from audio time series.
    Returns a concatenated vector of statistics (mean, std) for:
    - MFCCs
    - Chroma
    - Mel Spectrogram
    - Spectral Contrast
    """
    sr = config.SAMPLE_RATE
    result = np.array([])

    # 1. MFCC
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=config.N_MFCC)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    mfccs_std = np.std(mfccs.T, axis=0)
    result = np.hstack((result, mfccs_mean, mfccs_std))

    # 2. Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma.T, axis=0)
    chroma_std = np.std(chroma.T, axis=0)
    result = np.hstack((result, chroma_mean, chroma_std))

    # 3. Mel Spectrogram
    mel = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_mean = np.mean(mel.T, axis=0)
    mel_std = np.std(mel.T, axis=0)
    result = np.hstack((result, mel_mean, mel_std))

    # 4. Spectral Contrast
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = np.mean(contrast.T, axis=0)
    contrast_std = np.std(contrast.T, axis=0)
    result = np.hstack((result, contrast_mean, contrast_std))
    
    # Optional: Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = np.mean(zcr.T, axis=0)
    zcr_std = np.std(zcr.T, axis=0)
    result = np.hstack((result, zcr_mean, zcr_std))

    return result
