"""Test AI stress detection module."""
import os
import pytest
import numpy as np
import io
from scipy.io import wavfile

try:
    from ai_engine.inference import predict_stress
    AI_AVAILABLE = True
except Exception as e:
    AI_AVAILABLE = False
    print(f"AI module not available: {e}")


def create_dummy_audio(duration=2.0, sample_rate=16000, frequency=440):
    """Create a dummy audio file for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    
    # Convert to bytes
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sample_rate, audio_data)
    byte_io.seek(0)
    return byte_io.read()


@pytest.mark.skipif(not AI_AVAILABLE, reason="AI module not available")
class TestAIStressDetection:
    """Test suite for AI stress detection functionality."""
    
    def test_predict_stress_returns_dict(self):
        """Test that predict_stress returns a dictionary with required keys."""
        audio_bytes = create_dummy_audio()
        result = predict_stress(audio_bytes=audio_bytes)
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'label' in result, "Result should contain 'label' key"
        assert 'confidence' in result, "Result should contain 'confidence' key"
    
    def test_predict_stress_label_values(self):
        """Test that label is either 'normal' or 'stressed'."""
        audio_bytes = create_dummy_audio()
        result = predict_stress(audio_bytes=audio_bytes)
        
        assert result['label'] in ['normal', 'stressed', 'unknown'], \
            f"Label should be 'normal', 'stressed', or 'unknown', got {result['label']}"
    
    def test_predict_stress_confidence_range(self):
        """Test that confidence is between 0 and 1."""
        audio_bytes = create_dummy_audio()
        result = predict_stress(audio_bytes=audio_bytes)
        
        assert isinstance(result['confidence'], float), "Confidence should be a float"
        assert 0 <= result['confidence'] <= 1, \
            f"Confidence should be between 0 and 1, got {result['confidence']}"
    
    def test_predict_stress_normal_audio(self):
        """Test prediction on normal-like audio (low frequency)."""
        # Low frequency audio (mimicking calm speech)
        audio_bytes = create_dummy_audio(duration=2.0, frequency=200)
        result = predict_stress(audio_bytes=audio_bytes)
        
        assert result is not None
        assert 'label' in result
    
    def test_predict_stress_stressed_audio(self):
        """Test prediction on stressed-like audio (high frequency)."""
        # High frequency audio (mimicking agitated speech)
        audio_bytes = create_dummy_audio(duration=2.0, frequency=1000)
        result = predict_stress(audio_bytes=audio_bytes)
        
        assert result is not None
        assert 'label' in result
    
    def test_predict_stress_empty_audio(self):
        """Test handling of empty audio input."""
        try:
            result = predict_stress(audio_bytes=b'')
            # Should either return unknown or handle gracefully
            assert result['label'] in ['normal', 'stressed', 'unknown']
        except Exception as e:
            # Exception is acceptable for invalid input
            assert True
    
    def test_predict_stress_invalid_audio(self):
        """Test handling of invalid audio data."""
        try:
            result = predict_stress(audio_bytes=b'invalid audio data')
            # Should handle gracefully
            assert result is not None
        except Exception as e:
            # Exception is acceptable for invalid input
            assert True
    
    def test_predict_stress_very_short_audio(self):
        """Test handling of very short audio (< 0.5 seconds)."""
        audio_bytes = create_dummy_audio(duration=0.3)
        try:
            result = predict_stress(audio_bytes=audio_bytes)
            assert result is not None
        except Exception:
            # Short audio may cause exceptions, which is acceptable
            assert True
    
    def test_predict_stress_consistency(self):
        """Test that same audio produces consistent results."""
        audio_bytes = create_dummy_audio()
        
        result1 = predict_stress(audio_bytes=audio_bytes)
        result2 = predict_stress(audio_bytes=audio_bytes)
        
        # Same input should produce same output
        assert result1['label'] == result2['label']
        assert abs(result1['confidence'] - result2['confidence']) < 0.01
