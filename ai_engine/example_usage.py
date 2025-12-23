"""Example Usage of AI Engine Components

Demonstrates how to use the stress detection system.
"""

import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_audio_stress_detection():
    """Example: Audio-only stress detection"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Audio-Only Stress Detection")
    print("="*60)
    
    from ai_engine.audio_stress_detector import AudioStressDetector
    from ai_engine.feature_extractor import AudioFeatureExtractor
    from ai_engine.preprocessing import preprocess_audio
    
    # Initialize components
    feature_extractor = AudioFeatureExtractor()
    detector = AudioStressDetector(
        model_path="ai_engine/models/audio_stress_model.pkl",
        scaler_path="ai_engine/models/scaler.pkl"
    )
    
    # Load and process audio
    audio_path = "sample_audio.wav"  # Replace with actual path
    print(f"\nLoading audio from: {audio_path}")
    
    try:
        audio, sr = feature_extractor.load_audio(audio_path)
        print(f"Audio loaded: {len(audio)} samples at {sr} Hz")
        
        # Preprocess
        audio_clean = preprocess_audio(audio, sr)
        print("Audio preprocessed (noise removed, normalized)")
        
        # Extract features
        features = feature_extractor.extract_all_features(audio_clean)
        print(f"Extracted {len(features)} features")
        
        # Predict
        prediction, confidence = detector.predict(features)
        
        print("\nResults:")
        print(f"  Stress Detected: {'YES' if prediction == 1 else 'NO'}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Risk Level: {'HIGH' if confidence > 0.7 else 'MEDIUM' if confidence > 0.5 else 'LOW'}")
        
    except FileNotFoundError:
        print(f"Audio file not found. Skipping audio analysis.")
        print("To test: Place a WAV file at 'sample_audio.wav'")


def example_physiological_analysis():
    """Example: Physiological sensor analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Physiological Sensor Analysis")
    print("="*60)
    
    from ai_engine.physiological_analyzer import PhysiologicalAnalyzer
    
    analyzer = PhysiologicalAnalyzer()
    
    # Simulate sensor data
    test_cases = [
        {"heart_rate": 75, "temperature": 36.8, "label": "Normal"},
        {"heart_rate": 115, "temperature": 37.5, "label": "Moderate Stress"},
        {"heart_rate": 140, "temperature": 37.9, "label": "High Stress"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case['label']}")
        print(f"  Heart Rate: {case['heart_rate']} bpm")
        print(f"  Temperature: {case['temperature']}°C")
        
        result = analyzer.analyze_combined(
            heart_rate=case['heart_rate'],
            temperature=case['temperature']
        )
        
        print("\n  Analysis:")
        print(f"    Stress Detected: {'YES' if result['stress_detected'] else 'NO'}")
        print(f"    Combined Score: {result['combined_score']:.2f}")
        print(f"    Alert Recommended: {'YES' if result['alert_recommended'] else 'NO'}")
        print(f"    HR Status: {result['heart_rate']['stress_level']}")
        print(f"    Temp Status: {result['temperature']['stress_level']}")


def example_time_series_analysis():
    """Example: Time-series physiological analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Time-Series Physiological Analysis")
    print("="*60)
    
    from ai_engine.physiological_analyzer import PhysiologicalAnalyzer
    
    analyzer = PhysiologicalAnalyzer()
    
    # Simulate 10 readings showing gradual stress increase
    heart_rates = [72, 78, 85, 92, 105, 115, 125, 130, 135, 138]
    temperatures = [36.7, 36.8, 36.9, 37.1, 37.3, 37.5, 37.7, 37.8, 37.9, 38.0]
    
    print("\nAnalyzing 10 sequential readings...")
    print(f"Heart Rate Range: {min(heart_rates)}-{max(heart_rates)} bpm")
    print(f"Temperature Range: {min(temperatures)}-{max(temperatures)}°C")
    
    result = analyzer.analyze_time_series(heart_rates, temperatures)
    
    print("\nTime-Series Analysis:")
    print(f"  Stress Detected: {'YES' if result['stress_detected'] else 'NO'}")
    print(f"  Stress Score: {result['stress_score']:.2f}")
    print(f"  \nHeart Rate Stats:")
    print(f"    Mean: {result['heart_rate_stats']['mean']:.1f} bpm")
    print(f"    Std Dev: {result['heart_rate_stats']['std']:.1f} bpm")
    print(f"    Trend: {result['heart_rate_stats']['trend']:.2f} bpm/reading")
    print(f"    High Variability: {result['heart_rate_stats']['high_variability']}")
    print(f"  \nTemperature Stats:")
    print(f"    Mean: {result['temperature_stats']['mean']:.2f}°C")
    print(f"    Std Dev: {result['temperature_stats']['std']:.2f}°C")
    print(f"    Trend: {result['temperature_stats']['trend']:.3f}°C/reading")


def example_hybrid_detection():
    """Example: Hybrid multimodal detection"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Hybrid Multimodal Detection")
    print("="*60)
    
    from ai_engine.hybrid_detector import HybridStressDetector
    
    # Initialize hybrid detector
    detector = HybridStressDetector(
        audio_weight=0.6,
        physio_weight=0.4
    )
    
    print("\nScenario: Woman in distress situation")
    print("  - Elevated heart rate and temperature")
    print("  - Audio analysis would require actual audio file")
    
    # Analyze physiological data only (audio would need actual file)
    result = detector.analyze_physiological_only(
        heart_rate=125,
        temperature=37.8
    )
    
    print("\nResults:")
    print(f"  Stress Detected: {'YES' if result['stress_detected'] else 'NO'}")
    print(f"  Combined Score: {result['combined_score']:.2f}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Modalities Used: {result['modalities_used']}")
    
    # Get recommendations
    recommendations = detector.get_recommendation(result)
    
    print("\nRecommended Actions:")
    print(f"  Trigger Alert: {recommendations['trigger_alert']}")
    print(f"  Activate Camera: {recommendations['activate_camera']}")
    print(f"  Activate Buzzer: {recommendations['activate_buzzer']}")
    print(f"  Notify Guardians: {recommendations['notify_guardians']}")
    print(f"  Priority: {recommendations['priority'].upper()}")
    print(f"  Message: {recommendations['message']}")


def example_inference_service():
    """Example: Using the inference service"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Real-time Inference Service")
    print("="*60)
    
    from ai_engine.inference_service import get_inference_service
    
    # Get singleton service
    service = get_inference_service()
    
    print("\nInference Service Ready")
    print("Available methods:")
    print("  - analyze_audio_file(path)")
    print("  - analyze_audio_bytes(bytes)")
    print("  - analyze_audio_base64(base64_str)")
    print("  - analyze_physiological(hr, temp)")
    print("  - analyze_multimodal(audio, hr, temp)")
    
    # Example: Physiological analysis
    print("\n--- Physiological Analysis ---")
    result = service.analyze_physiological(
        heart_rate=118,
        temperature=37.6
    )
    
    if result['success']:
        print(f"Stress Detected: {result['stress_detected']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Alert Recommended: {result['alert_recommended']}")
    else:
        print(f"Error: {result['error']}")
    
    # Example: Multimodal (physiological only in this demo)
    print("\n--- Multimodal Analysis (Physio Only) ---")
    result = service.analyze_multimodal(
        heart_rate=130,
        temperature=38.0
    )
    
    if result['success']:
        print(f"Stress Detected: {result['stress_detected']}")
        print(f"Combined Score: {result['combined_score']:.2f}")
        print(f"Modalities: {result['modalities_used']}")
        
        recs = result['recommendations']
        if recs['trigger_alert']:
            print(f"\nALERT: {recs['message']}")
            print(f"Priority: {recs['priority'].upper()}")


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("#  AI ENGINE - STRESS DETECTION EXAMPLES")
    print("#"*60)
    
    try:
        # Run examples
        example_physiological_analysis()
        example_time_series_analysis()
        example_hybrid_detection()
        example_inference_service()
        
        # Audio example (may skip if no model file)
        example_audio_stress_detection()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\nNote: Some examples require trained models in ai_engine/models/")
        print("Run training first: python -m ai_engine.train_ensemble")
    
    print("\n" + "#"*60)
    print("#  EXAMPLES COMPLETED")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()