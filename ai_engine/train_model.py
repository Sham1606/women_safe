import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ai_engine.preprocessing import AudioPreprocessor
from ai_engine.features import extract_features

def load_data():
    """Load metadata and extract features for all files."""
    meta_path = os.path.join(config.PROCESSED_DATA_DIR, 'metadata.csv')
    if not os.path.exists(meta_path):
        print("Metadata not found. Run build_metadata.py first.")
        return None, None, None

    df = pd.read_csv(meta_path)
    X = []
    y = []
    groups = []  # For speaker-wise split

    print("Extracting features...")
    # Initialize preprocessor
    preprocessor = AudioPreprocessor(target_sr=config.SAMPLE_RATE, trim_silence=True)
    
    for index, row in tqdm(df.iterrows(), total=len(df)):
        file_path = row['file_path']
        label = row['label']
        actor_id = row['actor_id']

        try:
            audio, _ = preprocessor.preprocess_from_file(file_path)
            if audio is not None:
                feats = extract_features(audio)
                X.append(feats)
                y.append(label)
                groups.append(actor_id)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return np.array(X), np.array(y), np.array(groups)

def train():
    X, y, groups = load_data()
    if X is None or len(X) == 0:
        print("No data to train on.")
        return

    # Speaker-independent split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    print(f"Train/Test split: {len(X_train)}/{len(X_test)}")

    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Models
    clf1 = LogisticRegression(random_state=42, max_iter=1000)
    clf2 = RandomForestClassifier(n_estimators=50, random_state=42)
    clf3 = SVC(probability=True, random_state=42)
    clf4 = GradientBoostingClassifier(random_state=42)

    eclf = VotingClassifier(
        estimators=[('lr', clf1), ('rf', clf2), ('svc', clf3), ('gb', clf4)],
        voting='soft'
    )

    print("Training ensemble model...")
    eclf.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = eclf.predict(X_test_scaled)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Report:\n", classification_report(y_test, y_pred))

    # Save
    print("Saving models...")
    joblib.dump(scaler, config.SCALER_PATH)
    joblib.dump(eclf, config.MODEL_PATH)
    print(f"Saved to {config.MODEL_PATH}")

if __name__ == "__main__":
    train()
