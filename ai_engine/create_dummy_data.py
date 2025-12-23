import numpy as np
import soundfile as sf
import os
import sys
import random

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def generate_tone(freq, duration, sr=16000):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Add some noise to make it "realistic" feature-wise
    noise = np.random.normal(0, 0.01, len(t))
    sig = 0.5 * np.sin(2 * np.pi * freq * t) + noise
    return sig

def create_dummy_dataset(num_samples=200):
    """Generates dummy wav files in data/raw mimicking RAVDESS naming."""
    print(f"Generating {num_samples} dummy samples...")
    
    # Ensure dir
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)

    # 03 = Emotion index in RAVDESS filename
    # Modality-VocalChannel-Emotion-Intensity-Statement-Repetition-Actor.wav
    # Emotions: 01=neutral, 03=happy, 04=sad, 05=angry
    
    emotions = ['01', '02', '03', '04', '05', '06', '07', '08']
    
    for i in range(num_samples):
        emo_code = random.choice(emotions)
        actor = f"{random.randint(1, 24):02d}"
        filename = f"03-01-{emo_code}-01-01-01-{actor}-{i}.wav" # Added index to filename to avoid overwrite
        path = os.path.join(config.RAW_DATA_DIR, filename)
        
        # Stressed sounds (sad/angry/fear) -> higher freq/chaos
        if int(emo_code) >= 4:
            base_freq = random.uniform(600, 1200)
            sig = generate_tone(base_freq, config.DURATION)
            # Add chaotic modulation
            mod = np.sin(2 * np.pi * 50 * np.linspace(0, config.DURATION, len(sig)))
            sig = sig * mod
        else:
            # Normal (calm/happy)
            base_freq = random.uniform(200, 500)
            sig = generate_tone(base_freq, config.DURATION)
        
        sf.write(path, sig, config.SAMPLE_RATE)
        
    print(f"Created {num_samples} samples in {config.RAW_DATA_DIR}")

if __name__ == "__main__":
    create_dummy_dataset()
