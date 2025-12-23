"""Audio Feature Extraction Module

Extracts MFCC, Chroma, Mel Spectrogram, and Spectral Contrast features
from audio signals for stress detection.
"""

import librosa
import numpy as np
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class AudioFeatureExtractor:
    """Extract audio features for stress detection"""
    
    def __init__(self, sr: int = 22050, n_mfcc: int = 40):
        self.sr = sr
        self.n_mfcc = n_mfcc
    
    def extract_features(self, audio_path: str) -> Optional[np.ndarray]:
        """Extract comprehensive audio features
        
        Args:
            audio_path: Path to audio file or audio numpy array
            
        Returns:
            Feature vector combining MFCC, Chroma, Mel, Spectral Contrast
        """
        try:
            # Load audio
            if isinstance(audio_path, str):
                y, sr = librosa.load(audio_path, sr=self.sr, duration=3)
            else:
                y = audio_path
                sr = self.sr
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            # Extract Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            chroma_std = np.std(chroma, axis=1)
            
            # Extract Mel Spectrogram
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            mel_mean = np.mean(mel, axis=1)
            mel_std = np.std(mel, axis=1)
            
            # Extract Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            contrast_mean = np.mean(contrast, axis=1)
            contrast_std = np.std(contrast, axis=1)
            
            # Concatenate all features
            features = np.hstack([
                mfcc_mean, mfcc_std,
                chroma_mean, chroma_std,
                mel_mean, mel_std,
                contrast_mean, contrast_std
            ])
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def extract_features_dict(self, audio_path: str) -> Dict[str, np.ndarray]:
        """Extract features and return as dictionary"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sr, duration=3)
            
            features = {
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc),
                'chroma': librosa.feature.chroma_stft(y=y, sr=sr),
                'mel': librosa.feature.melspectrogram(y=y, sr=sr),
                'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr)
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}