# AI Engine - Dual-Mode Stress Detection

This module implements ensemble-based stress detection using audio analysis and physiological sensors.

## Architecture

### Components

1. **Audio Stress Detector** (`audio_stress_detector.py`)
   - Ensemble model with Soft Voting
   - Base classifiers: Logistic Regression, Random Forest, Gradient Boosting, SVM
   - Trained on audio features (MFCC, Chroma, Mel, Spectral Contrast)

2. **Physiological Analyzer** (`physiological_analyzer.py`)
   - Heart rate analysis (threshold-based)
   - Body temperature analysis
   - Time-series pattern detection

3. **Hybrid Detector** (`hybrid_detector.py`)
   - Combines audio + physiological signals
   - Weighted fusion (default: 60% audio, 40% physiological)
   - Provides action recommendations

4. **Feature Extractor** (`feature_extractor.py`)
   - MFCC: 40 coefficients (mean + std = 80 features)
   - Chroma: 12 features (mean + std = 24 features)
   - Mel Spectrogram: 128 bins (mean + std = 256 features)
   - Spectral Contrast: 7 bands (mean + std = 14 features)
   - **Total: 374 features**

5. **Preprocessing** (`preprocessing.py`)
   - Noise removal (spectral gating)
   - Audio normalization
   - Silence trimming
   - Data augmentation (pitch shift, time stretch, noise injection)

6. **Training Pipeline** (`train_ensemble.py`)
   - Complete training workflow
   - Automated data loading and preprocessing
   - Model evaluation with metrics
   - Model persistence

7. **Inference Service** (`inference_service.py`)
   - Real-time stress detection API
   - Supports audio files, bytes, base64
   - Multimodal analysis
   - Singleton pattern for efficient memory usage

## Installation

```bash
cd ai_engine
pip install -r requirements.txt
```

## Usage

### Training a Model

```python
from ai_engine.train_ensemble import EnsembleTrainingPipeline

# Initialize pipeline
pipeline = EnsembleTrainingPipeline(
    data_dir="ai_engine/data",
    output_dir="ai_engine/models"
)

# Run complete training
results = pipeline.run_full_pipeline(
    stressed_dir="raw/stressed",
    non_stressed_dir="raw/non_stressed",
    test_size=0.2
)

print(f"Test Accuracy: {results['test_metrics']['accuracy']:.4f}")
```

### Real-time Inference

#### Audio Only

```python
from ai_engine.inference_service import get_inference_service

service = get_inference_service()

# From audio file
result = service.analyze_audio_file("sample.wav")
print(f"Stress Detected: {result['stress_detected']}")
print(f"Confidence: {result['confidence']:.2f}")

# From base64 (for API)
result = service.analyze_audio_base64(audio_base64_string)
```

#### Physiological Only

```python
result = service.analyze_physiological(
    heart_rate=120,
    temperature=37.8
)
print(f"Stress Detected: {result['stress_detected']}")
print(f"Alert Recommended: {result['alert_recommended']}")
```

#### Multimodal (Combined)

```python
result = service.analyze_multimodal(
    audio_data="sample.wav",
    heart_rate=115,
    temperature=37.5
)

print(f"Stress Detected: {result['stress_detected']}")
print(f"Combined Score: {result['combined_score']:.2f}")
print(f"Modalities Used: {result['modalities_used']}")

# Get recommendations
recs = result['recommendations']
if recs['trigger_alert']:
    print(f"Priority: {recs['priority']}")
    print(f"Actions: Camera={recs['activate_camera']}, Buzzer={recs['activate_buzzer']}")
```

## Data Structure

Organize your training data as follows:

```
ai_engine/
├── data/
│   ├── raw/
│   │   ├── stressed/
│   │   │   ├── stress_001.wav
│   │   │   ├── stress_002.wav
│   │   │   └── ...
│   │   └── non_stressed/
│   │       ├── normal_001.wav
│   │       ├── normal_002.wav
│   │       └── ...
│   ├── processed/
│   └── augmented/
└── models/
    ├── audio_stress_model.pkl
    └── scaler.pkl
```

## Model Performance

Expected performance metrics (based on similar audio stress detection systems):
- **Training Accuracy**: 85-95%
- **Test Accuracy**: 80-90%
- **Inference Time**: < 100ms per audio sample
- **Feature Extraction Time**: < 50ms

## Configuration

Edit configuration files in `configs/`:
- `model_config.yaml`: Model hyperparameters
- `feature_config.yaml`: Feature extraction settings
- `physiological_thresholds.yaml`: Sensor thresholds

## Integration with Backend

The inference service is called by the backend API:

```python
# In backend/services/stress_analyzer.py
from ai_engine.inference_service import get_inference_service

service = get_inference_service()
result = service.analyze_multimodal(
    audio_data=audio_bytes,
    heart_rate=device_data['heart_rate'],
    temperature=device_data['temperature']
)

if result['stress_detected']:
    # Trigger alert system
    trigger_emergency_alert(device_id, result)
```

## API Response Format

```json
{
  "success": true,
  "stress_detected": true,
  "confidence": 0.85,
  "combined_score": 0.78,
  "modalities_used": ["audio", "physiological"],
  "recommendations": {
    "trigger_alert": true,
    "activate_camera": true,
    "activate_buzzer": true,
    "notify_guardians": true,
    "priority": "high",
    "message": "Moderate stress detected - alerting guardians"
  },
  "detailed_analysis": {
    "audio": {
      "prediction": 1,
      "confidence": 0.82,
      "stress_detected": true
    },
    "physiological": {
      "heart_rate": {
        "value": 115,
        "is_abnormal": true,
        "stress_level": "moderate_stress",
        "score": 0.7
      },
      "temperature": {
        "value": 37.5,
        "is_abnormal": true,
        "stress_level": "elevated_temperature",
        "score": 0.8
      },
      "combined_score": 0.74,
      "stress_detected": true
    }
  }
}
```

## Logging

Logs are stored in `ai_engine/logs/`:
- Training logs: `training_YYYYMMDD_HHMMSS.log`
- Inference logs: `inference_YYYYMMDD.log`

## Testing

Run unit tests:

```bash
pytest tests/test_ai_engine/
```

## Future Enhancements

1. Deep learning models (CNN, RNN, Transformer)
2. Real-time audio streaming support
3. Multi-language audio support
4. Emotion classification (not just stress)
5. Contextual analysis (time of day, location)
6. Personalized thresholds per user

## References

- MFCC: https://librosa.org/doc/main/generated/librosa.feature.mfcc.html
- Ensemble Learning: https://scikit-learn.org/stable/modules/ensemble.html
- Audio Stress Detection Research: Various academic papers on speech emotion recognition