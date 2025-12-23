"""Audio Feature Extraction

Extracts key features for stress detection:
- MFCC (Mel-Frequency Cepstral Coefficients)
- Chroma features
- Mel Spectrogram
- Spectral Contrast
"""

import librosa
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract audio features for stress detection"""
    
    def __init__(self, sr: int = 22050, n_mfcc: int = 13):
        """
        Args:
            sr: Sample rate for audio processing
            n_mfcc: Number of MFCC coefficients to extract
        """
        self.sr = sr
        self.n_mfcc = n_mfcc
        logger.info(f"Initialized FeatureExtractor with sr={sr}, n_mfcc={n_mfcc}")
    
    def extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features"""
        mfcc = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=self.n_mfcc)
        return np.mean(mfcc.T, axis=0)
    
    def extract_chroma(self, audio: np.ndarray) -> np.ndarray:
        """Extract Chroma features"""
        chroma = librosa.feature.chroma_stft(y=audio, sr=self.sr)
        return np.mean(chroma.T, axis=0)
    
    def extract_mel(self, audio: np.ndarray) -> np.ndarray:
        """Extract Mel Spectrogram features"""
        mel = librosa.feature.melspectrogram(y=audio, sr=self.sr)
        return np.mean(mel.T, axis=0)
    
    def extract_spectral_contrast(self, audio: np.ndarray) -> np.ndarray:
        """Extract Spectral Contrast features"""
        contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sr)
        return np.mean(contrast.T, axis=0)
    
    def extract_all_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract all features and concatenate
        
        Returns:
            Combined feature vector
        """
        try:
            mfcc = self.extract_mfcc(audio)
            chroma = self.extract_chroma(audio)
            mel = self.extract_mel(audio)
            contrast = self.extract_spectral_contrast(audio)
            
            # Concatenate all features
            features = np.concatenate([mfcc, chroma, mel, contrast])
            logger.debug(f"Extracted {len(features)} features")
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    def extract_from_file(self, audio_path: str) -> np.ndarray:
        """Load audio file and extract features
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Feature vector
        """
        try:
            audio, _ = librosa.load(audio_path, sr=self.sr)
            return self.extract_all_features(audio)
        except Exception as e:
            logger.error(f"Failed to extract features from {audio_path}: {e}")
            raise
