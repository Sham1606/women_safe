"""Audio Preprocessing Utilities

Preprocessing functions for audio data:
- Noise removal
- Normalization
- Silence trimming
- Audio augmentation
"""

import numpy as np
import librosa
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def remove_noise(audio: np.ndarray, sr: int, noise_duration: float = 0.5) -> np.ndarray:
    """Remove background noise using spectral gating
    
    Args:
        audio: Audio time series
        sr: Sample rate
        noise_duration: Duration of noise profile in seconds
        
    Returns:
        Denoised audio
    """
    try:
        # Use first part as noise profile
        noise_sample_length = int(noise_duration * sr)
        noise_profile = audio[:noise_sample_length]
        
        # Calculate noise threshold
        noise_rms = np.sqrt(np.mean(noise_profile**2))
        threshold = noise_rms * 1.5
        
        # Simple spectral subtraction
        audio_denoised = np.where(np.abs(audio) > threshold, audio, 0)
        
        logger.debug(f"Noise removed with threshold {threshold:.4f}")
        return audio_denoised
    except Exception as e:
        logger.warning(f"Noise removal failed: {e}. Returning original audio.")
        return audio


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to [-1, 1] range
    
    Args:
        audio: Audio time series
        
    Returns:
        Normalized audio
    """
    max_val = np.abs(audio).max()
    if max_val > 0:
        audio_normalized = audio / max_val
    else:
        audio_normalized = audio
    
    logger.debug("Audio normalized")
    return audio_normalized


def trim_silence(audio: np.ndarray, sr: int, top_db: int = 20) -> np.ndarray:
    """Trim silence from beginning and end of audio
    
    Args:
        audio: Audio time series
        sr: Sample rate
        top_db: Threshold in dB below reference to consider silence
        
    Returns:
        Trimmed audio
    """
    audio_trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
    
    original_duration = len(audio) / sr
    trimmed_duration = len(audio_trimmed) / sr
    
    logger.debug(f"Silence trimmed: {original_duration:.2f}s -> {trimmed_duration:.2f}s")
    return audio_trimmed


def augment_audio_pitch_shift(audio: np.ndarray, sr: int, n_steps: int = 2) -> np.ndarray:
    """Augment audio by shifting pitch
    
    Args:
        audio: Audio time series
        sr: Sample rate
        n_steps: Number of semitones to shift
        
    Returns:
        Pitch-shifted audio
    """
    audio_shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)
    logger.debug(f"Pitch shifted by {n_steps} semitones")
    return audio_shifted


def augment_audio_time_stretch(audio: np.ndarray, rate: float = 1.2) -> np.ndarray:
    """Augment audio by stretching time
    
    Args:
        audio: Audio time series
        rate: Stretch factor (>1 speeds up, <1 slows down)
        
    Returns:
        Time-stretched audio
    """
    audio_stretched = librosa.effects.time_stretch(audio, rate=rate)
    logger.debug(f"Time stretched by factor {rate}")
    return audio_stretched


def augment_audio_add_noise(audio: np.ndarray, noise_factor: float = 0.005) -> np.ndarray:
    """Augment audio by adding Gaussian noise
    
    Args:
        audio: Audio time series
        noise_factor: Standard deviation of noise
        
    Returns:
        Audio with added noise
    """
    noise = np.random.normal(0, noise_factor, audio.shape)
    audio_noisy = audio + noise
    logger.debug(f"Added Gaussian noise with factor {noise_factor}")
    return audio_noisy


def preprocess_audio(
    audio: np.ndarray,
    sr: int,
    remove_noise_flag: bool = True,
    normalize_flag: bool = True,
    trim_silence_flag: bool = True
) -> np.ndarray:
    """Complete preprocessing pipeline
    
    Args:
        audio: Audio time series
        sr: Sample rate
        remove_noise_flag: Whether to remove noise
        normalize_flag: Whether to normalize
        trim_silence_flag: Whether to trim silence
        
    Returns:
        Preprocessed audio
    """
    processed_audio = audio.copy()
    
    if trim_silence_flag:
        processed_audio = trim_silence(processed_audio, sr)
    
    if remove_noise_flag:
        processed_audio = remove_noise(processed_audio, sr)
    
    if normalize_flag:
        processed_audio = normalize_audio(processed_audio)
    
    logger.info("Audio preprocessing completed")
    return processed_audio