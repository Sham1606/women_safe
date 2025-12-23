"""Audio Preprocessing Module

Handles noise removal, normalization, and audio preprocessing
for stress detection pipeline.
"""

import librosa
import numpy as np
import noisereduce as nr
from scipy import signal
from typing import Tuple, Optional


class AudioPreprocessor:
    """Preprocess audio signals for stress detection"""
    
    def __init__(self, sr: int = 22050):
        self.sr = sr
    
    def load_and_preprocess(self, audio_path: str, duration: float = 3.0) -> Tuple[np.ndarray, int]:
        """Load audio file and apply preprocessing
        
        Args:
            audio_path: Path to audio file
            duration: Duration to load in seconds
            
        Returns:
            Preprocessed audio signal and sample rate
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sr, duration=duration)
        
        # Apply preprocessing pipeline
        y = self.remove_noise(y, sr)
        y = self.normalize(y)
        y = self.apply_preemphasis(y)
        
        return y, sr
    
    def remove_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Remove background noise using spectral gating"""
        try:
            # Use noisereduce library for noise removal
            reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True)
            return reduced_noise
        except:
            # Fallback: simple high-pass filter
            sos = signal.butter(10, 100, 'hp', fs=sr, output='sos')
            filtered = signal.sosfilt(sos, audio)
            return filtered
    
    def normalize(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        if np.max(np.abs(audio)) > 0:
            return audio / np.max(np.abs(audio))
        return audio
    
    def apply_preemphasis(self, audio: np.ndarray, coef: float = 0.97) -> np.ndarray:
        """Apply pre-emphasis filter to enhance high frequencies"""
        return np.append(audio[0], audio[1:] - coef * audio[:-1])
    
    def trim_silence(self, audio: np.ndarray, sr: int, top_db: int = 20) -> np.ndarray:
        """Trim leading and trailing silence"""
        trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        return trimmed
    
    def augment_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply audio augmentation for training"""
        # Random pitch shift
        if np.random.random() > 0.5:
            n_steps = np.random.randint(-3, 4)
            audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)
        
        # Random time stretch
        if np.random.random() > 0.5:
            rate = np.random.uniform(0.8, 1.2)
            audio = librosa.effects.time_stretch(audio, rate=rate)
        
        # Add random noise
        if np.random.random() > 0.5:
            noise = np.random.randn(len(audio)) * 0.005
            audio = audio + noise
        
        return audio