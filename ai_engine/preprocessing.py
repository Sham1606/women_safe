"""Audio Preprocessing Module

Preprocesses audio data for stress detection:
- Noise removal
- Normalization
- Silence trimming
- Resampling
"""

import sys
import os
from typing import Tuple, Optional
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

import librosa
import numpy as np
import noisereduce as nr

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Preprocess audio for stress detection"""
    
    def __init__(self, target_sr: int = 22050, trim_silence: bool = True):
        """
        Args:
            target_sr: Target sample rate
            trim_silence: Whether to trim silence from audio
        """
        self.target_sr = target_sr
        self.trim_silence = trim_silence
    
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        try:
            audio, sr = librosa.load(audio_path, sr=self.target_sr)
            logger.debug(f"Loaded audio: {len(audio)} samples at {sr}Hz")
            return audio, sr
        except Exception as e:
            logger.error(f"Failed to load audio from {audio_path}: {e}")
            raise
    
    def remove_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Remove background noise using noise reduction"""
        try:
            # Use noisereduce library
            reduced_noise = nr.reduce_noise(y=audio, sr=sr)
            logger.debug("Noise reduction applied")
            return reduced_noise
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}. Using original audio.")
            return audio
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio amplitude to [-1, 1]"""
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val
        logger.debug("Audio normalized")
        return audio
    
    def trim_silence_from_audio(self, audio: np.ndarray, top_db: int = 20) -> np.ndarray:
        """Trim leading and trailing silence"""
        try:
            trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
            logger.debug(f"Trimmed silence: {len(audio)} -> {len(trimmed)} samples")
            return trimmed
        except Exception as e:
            logger.warning(f"Silence trimming failed: {e}. Using original audio.")
            return audio
    
    def preprocess(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Complete preprocessing pipeline
        
        Args:
            audio: Raw audio data
            sr: Sample rate
            
        Returns:
            Preprocessed audio
        """
        # Remove noise
        audio = self.remove_noise(audio, sr)
        
        # Normalize
        audio = self.normalize_audio(audio)
        
        # Trim silence
        if self.trim_silence:
            audio = self.trim_silence_from_audio(audio)
        
        logger.info("Preprocessing completed")
        return audio
    
    def preprocess_from_file(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (preprocessed_audio, sample_rate)
        """
        audio, sr = self.load_audio(audio_path)
        audio = self.preprocess(audio, sr)
        return audio, sr
