# Women Safety System - Complete IoT Solution

An AI-powered women safety system combining **IoT wearable devices**, **machine learning stress detection**, and **real-time alert management**. The system provides automatic threat detection using physiological sensors and audio analysis, with immediate notification to guardians and emergency services.

## 🎯 Overview

This project implements a comprehensive safety solution with:
- **ESP32-based wearable device** with multiple sensors (heart rate, temperature, GPS, camera, microphone)
- **Dual-mode alert system**: Manual trigger + AI-powered stress detection
- **Machine learning models** for audio stress analysis with ensemble approach
- **Flask REST API backend** with SQLite database
- **Modern web dashboard** built with HTML/CSS/JavaScript/Bootstrap
- **Real-time notifications** to guardians via SMS/Email/Push
- **Evidence collection** (photos, audio, GPS) for documentation

## 📁 Project Structure

```
women_safe/
├── ai_engine/              # Machine learning stress detection
│   ├── models/            # Trained model files
│   ├── preprocessing/     # Audio/text preprocessing
│   ├── stress_detector.py # Main detection engine
│   └── README.md          # AI engine documentation
├── backend/               # Flask REST API
│   ├── app.py             # Main Flask application
│   ├── models.py          # SQLAlchemy models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── utils/             # Helper functions
│   └── README.md          # Backend documentation
├── iot_device/            # ESP32 firmware
│   ├── main/              # Arduino code
│   │   ├── main.ino       # Main firmware
│   │   ├── config.h       # Configuration
│   │   ├── sensors.h      # Sensor modules
│   │   ├── communication.h # API communication
│   │   ├── camera.h       # Camera module
│   │   ├── gps.h          # GPS module
│   │   └── audio.h        # Audio capture
│   └── README.md          # Hardware documentation
├── web_dashboard/         # Web interface
│   ├── index.html         # Login page
│   ├── dashboard.html     # Main dashboard
│   ├── devices.html       # Device management
│   ├── alerts.html        # Alert management
│   ├── guardians.html     # Guardian management
│   ├── profile.html       # User profile
│   ├── assets/            # CSS, JavaScript, images
│   └── README.md          # Dashboard documentation
└── README.md              # This file
```

## ✨ Key Features

### 1. **Dual-Mode Alert System**

#### Manual Trigger
- User presses emergency button on device
- Immediate alert activation
- Buzzer and LED indicators
- Captures evidence automatically
- Notifies all emergency contacts

#### AI-Detected Trigger
- Continuous monitoring of physiological data
- When stress thresholds exceeded:
  - Heart rate > 120 bpm
  - Body temperature > 38.5°C
- Captures 3-second audio sample
- Backend AI analyzes:
  - Audio stress patterns
  - Physiological data
  - Combined stress score
- Auto-triggers if stress score ≥ 0.7

### 2. **Multi-Sensor IoT Device**

- **MAX30102**: Heart rate & SpO2 monitoring
- **MLX90614**: Non-contact temperature sensor
- **NEO-6M GPS**: Real-time location tracking
- **ESP32-CAM**: Photo/video capture
- **INMP441**: Audio recording
- **Emergency Button**: Manual alert trigger
- **Buzzer & LED**: Status indicators
- **3.7V Li-Po Battery**: Portable power

### 3. **AI Stress Detection**

- **Ensemble Model Approach**:
  - Audio CNN for speech patterns
  - BERT-based text analysis (if transcribed)
  - Physiological data integration
  - Weighted combination for final score

- **Training Datasets**:
  - IEMOCAP: Emotional speech database
  - CREMA-D: Crowd-sourced emotional multimodal actors

### 4. **Evidence Collection**

- **Photos**: 3 images captured automatically
- **Audio**: 10-second recording
- **GPS**: Precise location coordinates
- **Physiological Data**: Heart rate, temperature snapshot
- **Timestamp**: Exact time of incident
- All uploaded to backend immediately

### 5. **Real-Time Notifications**

- **SMS**: Via Twilio API
- **Email**: Alert details with map link
- **Push Notifications**: Mobile app (future)
- **Guardian Dashboard**: Real-time updates
- **Police Portal**: Immediate alert forwarding

### 6. **Web Dashboard**

- Modern, responsive UI (Bootstrap 5)
- Real-time statistics
- Device management
- Alert history with filtering
- Guardian management
- Profile settings
- Evidence viewer
- Google Maps integration

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Arduino IDE** or **PlatformIO**
- **ESP32-CAM** and sensors
- **Modern web browser**

### 1. Clone Repository

```bash
git clone https://github.com/Sham1606/women_safe.git
cd women_safe
git checkout refactor-complete-architecture
```

### 2. Setup AI Engine

```bash
cd ai_engine
pip install -r requirements.txt
python stress_detector.py --test  # Test models
```

### 3. Setup Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs at: `http://localhost:5000`

### 4. Setup ESP32 Device

1. Open `iot_device/main/main.ino` in Arduino IDE
2. Install required libraries (see `iot_device/libraries.txt`)
3. Edit `config.h`:
   ```cpp
   #define WIFI_SSID "YourWiFi"
   #define WIFI_PASSWORD "YourPassword"
   #define API_BASE_URL "http://192.168.1.100:5000/api/v1"
   ```
4. Upload to ESP32-CAM
5. Open Serial Monitor to get device token

### 5. Setup Web Dashboard

1. Edit `web_dashboard/assets/js/config.js`:
   ```javascript
   API_BASE_URL: 'http://localhost:5000/api/v1'
   ```
2. Serve dashboard:
   ```bash
   cd web_dashboard
   python -m http.server 8000
   ```
3. Open browser: `http://localhost:8000`
4. Register account and login

## 📋 System Architecture

```
┌────────────────────┐
│   ESP32 Device     │
│  - Sensors         │
│  - Camera          │
│  - GPS             │
│  - Microphone      │
└────────┬──────────┘
         │ WiFi
         │ HTTP/JSON
         │
┌────────┴──────────┐
│  Flask Backend    │
│  - REST API       │
│  - Authentication │
│  - Database       │
└─────┬──────┬──────┘
      │      │
      │      └─────────────────────┐
      │                              │
┌─────┴───────────┐   ┌────────┴───────────┐
│  AI Engine       │   │  Web Dashboard   │
│  - Stress Model  │   │  - UI            │
│  - Audio CNN     │   │  - Alerts        │
│  - Ensemble      │   │  - Management    │
└───────────────────┘   └─────────────────────┘
         │
         │
┌────────┴──────────┐
│  Notifications   │
│  - SMS (Twilio)  │
│  - Email         │
│  - Push          │
└───────────────────┘
```

## 📊 Alert Flow

### Manual Alert Flow

```
User presses button
       ↓
ESP32 activates buzzer/LED
       ↓
Capture evidence:
  - 3 photos
  - 10s audio
  - GPS location
       ↓
Send alert to backend
       ↓
Backend processes:
  - Store alert
  - Save evidence
  - Notify guardians
  - Alert police
       ↓
Guardians receive:
  - SMS with location
  - Email with details
  - Dashboard notification
```

### AI-Detected Alert Flow

```
Sensors detect anomaly:
  - Heart rate > 120 bpm
  - Temperature > 38.5°C
       ↓
Capture 3s audio sample
       ↓
Send to backend AI
       ↓
AI analyzes:
  - Audio patterns
  - Voice stress
  - Physiological data
       ↓
Combined stress score
       ↓
If score ≥ 0.7:
  - Auto-trigger alert
  - Activate buzzer
  - Capture evidence
  - Notify contacts
```

## 🛠️ Hardware Setup

### Required Components

| Component | Price (INR) |
|-----------|-------------|
| ESP32-CAM | ₹400-600 |
| MAX30102 | ₹250-350 |
| MLX90614 | ₹400-500 |
| NEO-6M GPS | ₹400-600 |
| INMP441 Mic | ₹150-250 |
| Battery + Charger | ₹280-450 |
| Other (button, buzzer, wires) | ₹100-200 |
| **Total** | **₹2,000-3,000** |

### Pin Connections

See detailed wiring in [`iot_device/HARDWARE_SETUP.md`](iot_device/HARDWARE_SETUP.md)

## 📚 API Documentation

### Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Trigger Alert

```http
POST /api/v1/alerts/trigger
Authorization: Bearer <device_token>
Content-Type: application/json

{
  "alert_type": "manual_trigger",
  "trigger_source": "button",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "heart_rate": 125,
  "temperature": 38.2
}
```

### Upload Evidence

```http
POST /api/v1/evidence/upload
Authorization: Bearer <device_token>
Content-Type: application/json

{
  "alert_id": 123,
  "evidence_type": "photo",
  "file_name": "photo_123_456789.jpg",
  "file_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

Full API documentation: [`backend/README.md`](backend/README.md)

## 🧪 Testing

### Test AI Model

```bash
cd ai_engine
python stress_detector.py --test-audio sample.wav
```

### Test Backend API

```bash
cd backend
python -m pytest tests/
```

### Test ESP32 Sensors

```cpp
// In Arduino Serial Monitor
void loop() {
    float hr = readHeartRate();
    float temp = readTemperature();
    Serial.printf("HR: %.1f, Temp: %.1f\n", hr, temp);
    delay(1000);
}
```

## 💻 Technology Stack

### Hardware
- **ESP32-CAM** - Microcontroller with WiFi & camera
- **MAX30102** - Heart rate sensor
- **MLX90614** - Temperature sensor
- **NEO-6M** - GPS module
- **INMP441** - I2S microphone

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **JWT** - Authentication
- **TensorFlow/Keras** - ML models

### Frontend
- **HTML5 / CSS3 / JavaScript**
- **Bootstrap 5** - UI framework
- **Fetch API** - HTTP requests
- **LocalStorage** - Session management

### AI/ML
- **TensorFlow** - Deep learning
- **Librosa** - Audio processing
- **Transformers** - BERT models
- **NumPy / Pandas** - Data processing

## 🛡️ Security

- JWT token authentication
- Device token validation
- Password hashing (bcrypt)
- HTTPS recommended for production
- SQL injection prevention (SQLAlchemy)
- XSS protection
- CORS configuration

## 📦 Deployment

### Backend (Production)

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Using Docker
docker build -t women-safety-backend .
docker run -p 5000:5000 women-safety-backend
```

### Frontend (Production)

```bash
# Deploy to Nginx
sudo cp -r web_dashboard/* /var/www/html/

# Or use Apache
sudo cp -r web_dashboard/* /var/www/html/womensafety/
```

## 👥 Team

Developed by: **Sham1606**

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🚀 Future Enhancements

- [ ] Mobile app (React Native / Flutter)
- [ ] Video streaming capability
- [ ] Fall detection algorithm
- [ ] Voice command activation
- [ ] Multi-language support
- [ ] Offline mode with local storage
- [ ] Advanced analytics dashboard
- [ ] Police dispatch integration
- [ ] Geofencing alerts
- [ ] Social media SOS posting

## 📞 Support

- **GitHub Issues**: [Create Issue](https://github.com/Sham1606/women_safe/issues)
- **Documentation**: See component READMEs
- **Email**: support@womensafety.com (placeholder)

## 🔗 Links

- [AI Engine Documentation](ai_engine/README.md)
- [Backend API Documentation](backend/README.md)
- [ESP32 Hardware Guide](iot_device/README.md)
- [Web Dashboard Guide](web_dashboard/README.md)

## ⭐ Acknowledgments

- IEMOCAP and CREMA-D datasets for emotion recognition
- Bootstrap team for UI framework
- ESP32 community for hardware support
- TensorFlow/Keras teams for ML frameworks

---

**⚠️ Important**: This system is designed to assist in emergency situations but should not replace professional security services. Always contact local authorities in case of immediate danger.
