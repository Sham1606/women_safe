"""Audio Feature Extraction

Extracts key audio features for stress detection:
- MFCC (Mel-Frequency Cepstral Coefficients)
- Chroma features
- Mel spectrogram
- Spectral contrast
"""

import numpy as np
import librosa
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AudioFeatureExtractor:
    """Extract audio features for stress detection"""
    
    def __init__(self, sr: int = 22050, n_mfcc: int = 40, n_chroma: int = 12):
        """
        Args:
            sr: Sample rate for audio processing
            n_mfcc: Number of MFCC coefficients
            n_chroma: Number of chroma features
        """
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.n_chroma = n_chroma
    
    def load_audio(self, audio_path: str, duration: Optional[float] = None) -> Tuple[np.ndarray, int]:
        """Load audio file
        
        Args:
            audio_path: Path to audio file
            duration: Optional duration to load (seconds)
            
        Returns:
            (audio_data, sample_rate)
        """
        try:
            audio, sr = librosa.load(audio_path, sr=self.sr, duration=duration)
            logger.debug(f"Loaded audio: {audio.shape[0]} samples at {sr} Hz")
            return audio, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features
        
        Args:
            audio: Audio time series
            
        Returns:
            MFCC features (mean and std across time)
        """
        mfcc = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=self.n_mfcc)
        
        # Statistical features: mean and std
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        
        return np.concatenate([mfcc_mean, mfcc_std])
    
    def extract_chroma(self, audio: np.ndarray) -> np.ndarray:
        """Extract Chroma features
        
        Args:
            audio: Audio time series
            
        Returns:
            Chroma features (mean and std)
        """
        chroma = librosa.feature.chroma_stft(y=audio, sr=self.sr, n_chroma=self.n_chroma)
        
        chroma_mean = np.mean(chroma, axis=1)
        chroma_std = np.std(chroma, axis=1)
        
        return np.concatenate([chroma_mean, chroma_std])
    
    def extract_mel_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """Extract Mel spectrogram features
        
        Args:
            audio: Audio time series
            
        Returns:
            Mel spectrogram features (mean and std)
        """
        mel = librosa.feature.melspectrogram(y=audio, sr=self.sr)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        
        mel_mean = np.mean(mel_db, axis=1)
        mel_std = np.std(mel_db, axis=1)
        
        return np.concatenate([mel_mean, mel_std])
    
    def extract_spectral_contrast(self, audio: np.ndarray) -> np.ndarray:
        """Extract Spectral Contrast features
        
        Args:
            audio: Audio time series
            
        Returns:
            Spectral contrast features (mean and std)
        """
        contrast = librosa.feature.spectral_contrast(y=audio, sr=self.sr)
        
        contrast_mean = np.mean(contrast, axis=1)
        contrast_std = np.std(contrast, axis=1)
        
        return np.concatenate([contrast_mean, contrast_std])
    
    def extract_all_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract all audio features
        
        Args:
            audio: Audio time series
            
        Returns:
            Combined feature vector
        """
        mfcc_features = self.extract_mfcc(audio)
        chroma_features = self.extract_chroma(audio)
        mel_features = self.extract_mel_spectrogram(audio)
        contrast_features = self.extract_spectral_contrast(audio)
        
        # Concatenate all features
        all_features = np.concatenate([
            mfcc_features,
            chroma_features,
            mel_features,
            contrast_features
        ])
        
        logger.debug(f"Extracted {all_features.shape[0]} features")
        return all_features
    
    def extract_from_file(self, audio_path: str) -> np.ndarray:
        """Extract features directly from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Feature vector
        """
        audio, _ = self.load_audio(audio_path)
        return self.extract_all_features(audio)
    
    def get_feature_names(self) -> list:
        """Get names of all features
        
        Returns:
            List of feature names
        """
        feature_names = []
        
        # MFCC features
        for i in range(self.n_mfcc):
            feature_names.extend([f'mfcc_{i}_mean', f'mfcc_{i}_std'])
        
        # Chroma features
        for i in range(self.n_chroma):
            feature_names.extend([f'chroma_{i}_mean', f'chroma_{i}_std'])
        
        # Mel spectrogram (128 bins default)
        for i in range(128):
            feature_names.extend([f'mel_{i}_mean', f'mel_{i}_std'])
        
        # Spectral contrast (7 bands default)
        for i in range(7):
            feature_names.extend([f'contrast_{i}_mean', f'contrast_{i}_std'])
        
        return feature_names