import os
from datetime import timedelta

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Audio Settings
SAMPLE_RATE = 16000
DURATION = 3  # seconds (fixed duration for consistent input)
N_MFCC = 13
N_FFT = 2048
HOP_LENGTH = 512

# Model Paths
SCALER_PATH = os.path.join(MODELS_DIR, 'preprocess.joblib')
MODEL_PATH = os.path.join(MODELS_DIR, 'stress_model.joblib')

# Database & App Config
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_DIR, 'women_safety.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'replace-this-with-a-secure-random-key')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=24)
EVIDENCE_DIR = os.path.join(DATA_DIR, 'evidence')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Emotion Mappings
# Maps standard emotion labels to "normal" or "stressed"
EMOTION_TO_LABEL = {
    'neutral': 'normal',
    'calm': 'normal',
    'happy': 'normal',
    'sad': 'stressed',
    'angry': 'stressed',
    'fearful': 'stressed',
    'disgust': 'stressed',
    'surprised': 'stressed'
}

# RAVDESS numeric codes
# 01=neutral, 02=calm, 03=happy, 04=sad, 05=angry, 06=fearful, 07=disgust, 08=surprised
RAVDESS_MAP = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprised'
}
