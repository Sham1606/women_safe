# 🛡️ **AI-Powered Proactive Women's Safety Device**
## Complete Refactored Architecture

---

## 📋 **Project Overview**

### **Title:** An AI-Powered Proactive Women's Safety Device

### **Core Innovation:**
A standalone IoT-enabled wearable device that uses **dual-mode stress detection** (physiological sensors + AI voice analysis) to automatically detect distress and trigger multi-layered emergency protocols without requiring manual activation.

### **Key Differentiators:**
- ✅ **Proactive Detection:** Automatic stress detection using AI
- ✅ **Standalone Operation:** No smartphone dependency
- ✅ **Multi-Modal Evidence:** Audio + Image + GPS + Vitals
- ✅ **Multi-Recipient Alerts:** Family + Police + Emergency Services (simultaneous)
- ✅ **Real-time Monitoring:** Live tracking and evidence streaming

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WOMEN SAFETY ECOSYSTEM                          │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   IoT DEVICE     │       │   BACKEND API    │       │  WEB DASHBOARD   │
│   (ESP32-CAM)    │◄─────►│   (Flask/JWT)    │◄─────►│  (React/Vue.js)  │
│                  │  GSM  │                  │ HTTPS │                  │
│ - Heart Rate     │  WiFi │ - Alert Manager  │       │ - Guardian View  │
│ - Temperature    │       │ - AI Inference   │       │ - Police Panel   │
│ - Microphone     │       │ - Evidence Store │       │ - Live Monitor   │
│ - GPS Module     │       │ - Multi-Alert    │       │ - Evidence View  │
│ - Camera         │       │ - Notification   │       │ - Analytics      │
│ - Buzzer         │       │ - Database       │       │                  │
└──────────────────┘       └──────────────────┘       └──────────────────┘
         │                          │                          │
         │                          ▼                          │
         │                  ┌───────────────┐                 │
         │                  │ ALERT ENGINE  │                 │
         │                  │               │                 │
         │                  │ ├─► Family    │                 │
         └─────────────────►│ ├─► Police    │◄────────────────┘
                            │ └─► NGO/911   │
                            └───────────────┘
```

---

## 🔄 **Complete System Workflow**

### **Stage 1: Device Power On**
```
1. ESP32 initializes sensors
2. Connect to WiFi/GSM network
3. Authenticate with backend server
4. Start continuous monitoring loop
```

### **Stage 2: Dual-Mode Stress Detection**

#### **Mode A: Physiological Monitoring**
```
Heart Rate Sensor ──► [Threshold: > 100 BPM] ──► Stress Score +30%
Temperature Sensor ──► [Threshold: > 38.5°C] ──► Stress Score +10%
GSR (Skin Response) ──► [Abnormal patterns] ──► Stress Score +20%
```

#### **Mode B: AI Voice Analysis**
```
Microphone ──► Audio Buffer (3s) ──► 
    ├─► Extract Features (MFCC, Chroma, Mel, Spectral)
    ├─► Send to Backend AI Model
    └─► Get Prediction: {label: 'stressed', confidence: 0.85}
          └─► If 'stressed' && confidence > 0.7 ──► Stress Score +40%
```

### **Stage 3: Alert Threshold Check**
```
Total Stress Score = (Physiological × 0.4) + (AI Voice × 0.6)

IF Stress Score > 0.5 OR Manual SOS Button Pressed:
    ──► TRIGGER EMERGENCY PROTOCOL
```

### **Stage 4: Emergency Protocol (Automatic)**
```
┌─────────────────── EMERGENCY ACTIVATED ─────────────────────┐
│                                                              │
│ Step 1: EVIDENCE CAPTURE (Simultaneous)                     │
│    ├─► Camera: Capture 3 images (front-facing)              │
│    ├─► Microphone: Record 10s audio                         │
│    ├─► GPS: Fetch current coordinates                       │
│    └─► Vitals: Log HR, Temp, Stress Score                   │
│                                                              │
│ Step 2: LOCAL ACTIONS                                       │
│    ├─► Activate HIGH-DECIBEL BUZZER (120dB)                 │
│    └─► Flash LED lights (visual alert)                      │
│                                                              │
│ Step 3: DATA TRANSMISSION (via GSM/WiFi)                    │
│    ├─► POST /api/device/event                               │
│    │    - device_uid                                         │
│    │    - vitals (hr, temp, spo2)                           │
│    │    - gps (lat, lng)                                     │
│    │    - audio file (multipart)                            │
│    │    - manual_sos flag                                    │
│    │                                                         │
│    └─► Backend processes & creates Alert                    │
│         └─► Stores evidence in secure storage               │
│         └─► Creates Alert with status: NEW                  │
│                                                              │
│ Step 4: MULTI-RECIPIENT ALERT DISPATCH                      │
│    ├─► SMS to Family/Guardians (via Twilio)                 │
│    │    "🚨 EMERGENCY: [Name] needs help!                   │
│    │     Location: [GPS Link]                               │
│    │     View Evidence: [Web Link]"                         │
│    │                                                         │
│    ├─► Alert to Police/Emergency Services                   │
│    │    - Automated call to nearest police station          │
│    │    - Push notification to police dashboard             │
│    │    - Email with evidence attachments                   │
│    │                                                         │
│    └─► (Optional) Community Safety Network                  │
│         - NGO helpline notification                          │
│         - Nearby registered volunteers                       │
│                                                              │
│ Step 5: CONTINUOUS TRACKING                                 │
│    └─► Send GPS updates every 30 seconds until resolved     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### **Stage 5: Guardian/Police Response**
```
Family/Guardian:
    ├─► Receives SMS + App notification
    ├─► Opens Web Dashboard
    ├─► Views real-time location on map
    ├─► Listens to audio evidence
    ├─► Views captured images
    └─► Can call emergency services directly

Police/Admin:
    ├─► Alert appears in real-time feed
    ├─► Views all evidence (audio, images, vitals)
    ├─► Updates alert status: NEW → IN_PROGRESS → RESOLVED
    ├─► Dispatches nearest patrol unit
    └─► Downloads evidence for legal documentation
```

---

## 🔧 **Hardware Specifications (ESP32 Device)**

### **Core Components:**

| Component | Model | Function | Connection |
|-----------|-------|----------|------------|
| **Microcontroller** | ESP32-CAM | Main processor + camera | - |
| **Heart Rate Sensor** | MAX30102 | Pulse oximeter (HR + SpO2) | I2C |
| **Temperature Sensor** | DHT22 / DS18B20 | Body temperature | Digital Pin |
| **GSR Sensor** | Grove GSR | Galvanic skin response | Analog Pin |
| **Microphone** | MAX9814 / INMP441 | Audio capture (I2S) | I2S / Analog |
| **GPS Module** | NEO-6M / NEO-7M | Location tracking | UART |
| **Buzzer** | Active Buzzer 5V | Emergency alarm (120dB) | Digital Pin |
| **GSM Module** | SIM800L / SIM7600 | Cellular communication | UART |
| **Camera** | ESP32-CAM OV2640 | Image capture | Built-in |
| **Battery** | 3.7V Li-Ion 3000mAh | Power supply | Battery connector |
| **Panic Button** | Push button | Manual SOS trigger | Digital Pin (Pull-up) |

### **Pin Configuration:**
```c
// ESP32-CAM Pin Mapping
#define HR_SENSOR_SDA 21
#define HR_SENSOR_SCL 22
#define TEMP_SENSOR_PIN 4
#define GSR_SENSOR_PIN 36  // ADC1_0
#define MIC_PIN 39         // ADC1_3
#define GPS_TX 16
#define GPS_RX 17
#define GSM_TX 14
#define GSM_RX 15
#define BUZZER_PIN 13
#define SOS_BUTTON_PIN 12
#define LED_INDICATOR 33
```

### **Power Management:**
- **Normal Mode:** 200-300mA (continuous monitoring)
- **Alert Mode:** 500-800mA (camera + GSM + buzzer)
- **Sleep Mode:** 10-20mA (deep sleep with wake-up triggers)
- **Battery Life:** ~10-12 hours continuous use

---

## 🤖 **AI Model Pipeline**

### **Model Architecture:**

```python
# Ensemble Audio Stress Detection Model

Input: Raw Audio (WAV/MP3) → 3-second chunks

└─► Preprocessing:
     ├─► Noise Removal (noise reduction filter)
     ├─► Normalization (amplitude scaling)
     └─► Resampling to 16kHz

└─► Feature Extraction:
     ├─► MFCC (Mel-Frequency Cepstral Coefficients) - 13 coefficients
     ├─► Chroma Features - 12 pitch classes
     ├─► Mel Spectrogram - 128 mel bands
     └─► Spectral Contrast - 7 bands

└─► Ensemble Classifier:
     ├─► Logistic Regression (weight: 0.2)
     ├─► Random Forest (weight: 0.3)
     ├─► Gradient Boosting (weight: 0.3)
     └─► SVM (RBF kernel) (weight: 0.2)

└─► Soft Voting:
     └─► Aggregate probabilities → Final Prediction

Output: {label: 'stressed' | 'normal', confidence: 0.0-1.0}
```

### **Training Dataset:**
- **Source:** RAVDESS, TESS, SAVEE, EmoDB (emotional speech datasets)
- **Classes:** 2 (stressed, normal)
- **Total Samples:** ~5000 audio clips
- **Train/Test Split:** 80/20
- **Data Augmentation:** Time stretching, pitch shifting, background noise

### **Performance Metrics:**
- **Accuracy:** 87-92%
- **Precision:** 89%
- **Recall:** 85%
- **F1-Score:** 87%
- **Inference Time:** < 2 seconds (on backend)

### **Model Deployment:**
```
Training: Python (TensorFlow/Scikit-learn)
Export: Pickle file (ensemble_stress_model.pkl)
Deployment: Flask API endpoint
Inference: Real-time via /api/ai/predict-stress
```

---

## 🗂️ **Backend API Architecture**

### **Technology Stack:**
- **Framework:** Flask 3.0
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** JWT (Flask-JWT-Extended)
- **File Storage:** Local filesystem / AWS S3
- **Messaging:** Twilio API (SMS/Calls)
- **Email:** SendGrid / SMTP
- **Real-time:** Flask-SocketIO (WebSockets)

### **API Endpoints:**

#### **1. Device Communication**
```http
POST /api/device/register
Content-Type: application/json
Authorization: Bearer <JWT>

Request:
{
  "device_uid": "SHIELD-ESP32-001",
  "owner_email": "user@example.com"
}

Response:
{
  "message": "Device registered successfully",
  "device_id": 42
}
```

```http
POST /api/device/event
Content-Type: multipart/form-data

Request:
- device_uid: "SHIELD-ESP32-001"
- heart_rate: 115
- temperature: 37.8
- spo2: 97
- lat: 11.9416
- lng: 79.8083
- manual_sos: 0
- audio: <audio_file.wav>
- image: <image.jpg>

Response:
{
  "status": "success",
  "distress_score": 0.72,
  "alert_triggered": true,
  "alert_id": 123
}
```

#### **2. Alert Management**
```http
GET /api/alerts
Authorization: Bearer <JWT>

Response:
[
  {
    "id": 123,
    "device_uid": "SHIELD-ESP32-001",
    "reason": "AUTO_STRESS",
    "status": "NEW",
    "severity": "HIGH",
    "timestamp": "2025-12-23T23:15:00Z",
    "gps_lat": 11.9416,
    "gps_lng": 79.8083,
    "vitals": {"hr": 115, "temp": 37.8}
  }
]
```

```http
GET /api/alerts/{alert_id}
Authorization: Bearer <JWT>

Response:
{
  "id": 123,
  "device_uid": "SHIELD-ESP32-001",
  "reason": "AUTO_STRESS",
  "status": "NEW",
  "timestamp": "2025-12-23T23:15:00Z",
  "evidence": [
    {"type": "AUDIO", "path": "evidence/SHIELD-ESP32-001_20251223_231500.wav"},
    {"type": "IMAGE", "path": "evidence/SHIELD-ESP32-001_20251223_231502.jpg"}
  ],
  "gps": {"lat": 11.9416, "lng": 79.8083}
}
```

```http
PATCH /api/alerts/{alert_id}/status
Authorization: Bearer <JWT> (Police/Admin only)
Content-Type: application/json

Request:
{
  "status": "IN_PROGRESS"
}

Response:
{
  "message": "Alert status updated"
}
```

#### **3. Multi-Recipient Alerting**
```http
POST /api/alerts/dispatch
Internal endpoint (called automatically)

Payload:
{
  "alert_id": 123,
  "device_uid": "SHIELD-ESP32-001",
  "owner_name": "Jane Doe",
  "gps": {"lat": 11.9416, "lng": 79.8083},
  "recipients": {
    "family": ["+919876543210", "+919876543211"],
    "police": ["emergency@police.gov", "+100"],
    "ngo": ["helpline@womensafety.org"]
  }
}

Actions:
1. Send SMS to family via Twilio
2. Send email with evidence link to police
3. Make automated call to police station
4. Push notification to police dashboard
5. Notify registered NGO helpline
```

#### **4. AI Inference**
```http
POST /api/ai/predict-stress
Content-Type: multipart/form-data

Request:
- audio: <audio_file.wav>

Response:
{
  "label": "stressed",
  "confidence": 0.85,
  "timestamp": "2025-12-23T23:15:00Z"
}
```

---

## 🖥️ **Frontend Dashboard**

### **Technology Stack:**
- **Framework:** React.js / Vue.js / Vanilla JS + Bootstrap 5
- **Maps:** Leaflet.js / Google Maps API
- **Charts:** Chart.js
- **Real-time:** Socket.IO client
- **State Management:** Context API / Vuex

### **User Roles & Views:**

#### **1. Guardian/Family Portal**
```
┌─────────────────────── GUARDIAN DASHBOARD ─────────────────────────┐
│                                                                     │
│  👤 Jane Doe (GUARDIAN)                                   [Logout] │
│                                                                     │
│  ┌────────────── MY DEVICES ──────────────┐                        │
│  │                                         │                        │
│  │  📱 SHIELD-ESP32-001      [🟢 ONLINE]  │                        │
│  │  ❤️ 72 BPM  🌡️ 36.5°C  🔋 85%         │                        │
│  │  AI: NORMAL (95%)                       │                        │
│  │  Last Update: 2 min ago                 │                        │
│  │                                         │                        │
│  │  [View Location] [Device Settings]      │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
│  ┌────────────── ACTIVE ALERTS ────────────┐                       │
│  │                                          │                       │
│  │  ⚠️ No active alerts                    │                       │
│  │                                          │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌────────────── LIVE MAP ──────────────────┐                      │
│  │                                          │                       │
│  │   [Interactive Map with Device Marker]   │                       │
│  │   📍 Current Location: Puducherry, IN    │                       │
│  │                                          │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌────── ALERT HISTORY (Last 7 days) ──────┐                       │
│  │  Date       | Status    | Severity       │                       │
│  │  Dec 20     | RESOLVED  | MEDIUM         │                       │
│  │  Dec 18     | RESOLVED  | HIGH           │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

🚨 WHEN ALERT TRIGGERED:
┌─────────────────────── 🚨 EMERGENCY ALERT 🚨 ──────────────────────┐
│                                                                     │
│  ⚠️ DISTRESS DETECTED - Jane Doe needs immediate help!             │
│                                                                     │
│  📍 Location: 11.9416, 79.8083                                      │
│  🗺️ [View on Google Maps]                                          │
│                                                                     │
│  ┌───────── EVIDENCE ─────────┐                                    │
│  │                            │                                    │
│  │  🎙️ Audio Recording:       │                                    │
│  │  [▶️ Play] [Download]      │                                    │
│  │                            │                                    │
│  │  📷 Image:                  │                                    │
│  │  [View Image]              │                                    │
│  │                            │                                    │
│  │  ❤️ Vitals:                │                                    │
│  │  Heart Rate: 115 BPM       │                                    │
│  │  Temperature: 37.8°C       │                                    │
│  │  AI Stress: 85%            │                                    │
│  └────────────────────────────┘                                    │
│                                                                     │
│  [📞 Call Police] [📱 Call Jane] [✅ Mark as Handled]               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### **2. Police/Admin Panel**
```
┌─────────────────────── POLICE CONTROL CENTER ──────────────────────┐
│                                                                     │
│  👮 Officer Sharma (POLICE)                           [Logout]     │
│                                                                     │
│  ┌──────── SYSTEM OVERVIEW ────────┐                               │
│  │  📊 Total Devices: 150          │                               │
│  │  🚨 Active Alerts: 2            │                               │
│  │  ✅ Resolved Today: 5           │                               │
│  │  👥 Registered Users: 120       │                               │
│  └─────────────────────────────────┘                               │
│                                                                     │
│  ┌────────── REAL-TIME ALERTS FEED ─────────┐                      │
│  │  🚨 NEW - SHIELD-ESP32-045                │                      │
│  │     Priya Kumar | HIGH                    │                      │
│  │     📍 Anna Nagar, Chennai                │                      │
│  │     ⏰ 2 min ago                          │                      │
│  │     [VIEW DETAILS] [DISPATCH UNIT]        │                      │
│  │  ─────────────────────────────────────── │                      │
│  │  🟡 IN_PROGRESS - SHIELD-ESP32-023        │                      │
│  │     Anjali Reddy | MEDIUM                 │                      │
│  │     📍 MG Road, Puducherry                │                      │
│  │     ⏰ 15 min ago                         │                      │
│  │     [VIEW DETAILS] [UPDATE STATUS]        │                      │
│  └───────────────────────────────────────────┘                      │
│                                                                     │
│  ┌─────────── CITY MAP (Heat Map) ───────────┐                     │
│  │                                           │                     │
│  │   [Map showing alert clusters/hotspots]   │                     │
│  │   Red zones = High alert frequency        │                     │
│  │                                           │                     │
│  └───────────────────────────────────────────┘                     │
│                                                                     │
│  ┌────────── EVIDENCE DATABASE ──────────┐                         │
│  │  [Search] [Filter by Date/Location]   │                         │
│  │                                        │                         │
│  │  📁 Case #123 - Dec 23, 2025           │                         │
│  │     🎙️ Audio | 📷 3 Images | 📍 GPS   │                         │
│  │     [Download All]                     │                         │
│  └────────────────────────────────────────┘                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 **Database Schema**

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'GUARDIAN',  -- GUARDIAN, POLICE, ADMIN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    emergency_contacts TEXT  -- JSON array of contacts
);

-- Devices Table
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_uid VARCHAR(50) UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL,
    device_type VARCHAR(20) DEFAULT 'ESP32-CAM',
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP,
    battery_level INTEGER,
    last_lat FLOAT,
    last_lng FLOAT,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Sensor Events Table
CREATE TABLE sensor_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heart_rate FLOAT,
    spo2 FLOAT,
    temperature FLOAT,
    gsr_value FLOAT,
    raw_stress_score FLOAT,
    ai_label VARCHAR(20),
    ai_confidence FLOAT,
    has_audio BOOLEAN DEFAULT FALSE,
    audio_path VARCHAR(200),
    has_image BOOLEAN DEFAULT FALSE,
    image_path VARCHAR(200),
    FOREIGN KEY (device_id) REFERENCES devices(id),
    INDEX idx_device_timestamp (device_id, timestamp)
);

-- Alerts Table
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(50),  -- AUTO_STRESS, MANUAL_SOS, FALL_DETECTED
    status VARCHAR(20) DEFAULT 'NEW',  -- NEW, IN_PROGRESS, RESOLVED
    severity VARCHAR(20) DEFAULT 'HIGH',  -- HIGH, MEDIUM, LOW
    gps_lat FLOAT,
    gps_lng FLOAT,
    response_time INTEGER,  -- seconds taken to respond
    resolved_by INTEGER,  -- user_id of police/admin who resolved
    resolved_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_timestamp (timestamp)
);

-- Evidence Table
CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    file_type VARCHAR(10),  -- AUDIO, IMAGE, VIDEO
    file_path VARCHAR(200),
    file_size INTEGER,  -- bytes
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gps_lat FLOAT,
    gps_lng FLOAT,
    FOREIGN KEY (alert_id) REFERENCES alerts(id)
);

-- Notifications Table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    alert_id INTEGER,
    type VARCHAR(20),  -- SMS, EMAIL, PUSH
    recipient VARCHAR(100),  -- phone/email
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (alert_id) REFERENCES alerts(id)
);

-- Emergency Contacts Table
CREATE TABLE emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    relationship VARCHAR(50),
    priority INTEGER DEFAULT 1,  -- 1=highest priority
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔐 **Security & Privacy**

### **Data Encryption:**
- ✅ **In Transit:** HTTPS/TLS 1.3 for all API communications
- ✅ **At Rest:** AES-256 encryption for sensitive evidence files
- ✅ **Passwords:** bcrypt hashing with salt
- ✅ **JWT Tokens:** Signed with HMAC-SHA256

### **Access Control:**
- ✅ **Role-Based Access Control (RBAC):** Guardian, Police, Admin
- ✅ **Evidence Access:** Restricted to authorized users only
- ✅ **API Authentication:** JWT required for all protected endpoints
- ✅ **Device Authentication:** Unique device UID + API key

### **Privacy Measures:**
- ✅ **Data Minimization:** Collect only necessary information
- ✅ **User Consent:** Explicit permission for emergency contacts
- ✅ **Audit Logs:** Track all evidence access attempts
- ✅ **Auto-Deletion:** Evidence older than 90 days (configurable)

---

## 📡 **Communication Protocols**

### **ESP32 ↔ Backend:**
```
Protocol: HTTP/HTTPS over WiFi or GSM
Format: Multipart form-data (for files) + JSON
Frequency: 
  - Normal: Every 60 seconds (vitals update)
  - Alert Mode: Every 10 seconds (GPS tracking)
```

### **Backend → Twilio (SMS/Calls):**
```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Send SMS
message = client.messages.create(
    body=f"🚨 EMERGENCY: {user_name} needs help! Location: https://maps.google.com/?q={lat},{lng}",
    from_=TWILIO_PHONE_NUMBER,
    to=family_phone
)

# Make automated call
call = client.calls.create(
    url='http://yourserver.com/emergency_call.xml',  # TwiML
    to=police_phone,
    from_=TWILIO_PHONE_NUMBER
)
```

### **Backend → Frontend (Real-time):**
```javascript
// Socket.IO for live updates
const socket = io('http://localhost:5000');

socket.on('new_alert', (data) => {
  console.log('New alert:', data);
  showAlertNotification(data);
  updateMap(data.gps);
});

socket.on('alert_status_update', (data) => {
  updateAlertCard(data.alert_id, data.status);
});
```

---

## 🧪 **Testing Strategy**

### **Unit Tests:**
```bash
# AI Model
pytest tests/test_ai_model.py

# Backend APIs
pytest tests/test_api_endpoints.py

# Database operations
pytest tests/test_database.py
```

### **Integration Tests:**
```bash
# ESP32 → Backend flow
pytest tests/test_device_integration.py

# Alert dispatch system
pytest tests/test_alert_dispatch.py
```

### **End-to-End Tests:**
```bash
# Full workflow simulation
python tests/test_e2e_workflow.py
```

### **Hardware Tests:**
```c
// ESP32 firmware testing
void test_sensors() {
  assert(read_heart_rate() > 0);
  assert(read_temperature() > 30.0);
  assert(gps_get_location() == GPS_OK);
}
```

---

## 🚀 **Deployment Architecture**

### **Production Stack:**
```
┌─────────────────────────────────────────┐
│         CLOUD INFRASTRUCTURE            │
│                                         │
│  ┌──────────────┐   ┌──────────────┐  │
│  │   Frontend   │   │   Backend    │  │
│  │   (Nginx)    │◄─►│   (Gunicorn) │  │
│  │   React/Vue  │   │   Flask API  │  │
│  └──────────────┘   └──────────────┘  │
│         │                    │          │
│         ▼                    ▼          │
│  ┌──────────────┐   ┌──────────────┐  │
│  │     CDN      │   │  PostgreSQL  │  │
│  │  (CloudFlare)│   │   Database   │  │
│  └──────────────┘   └──────────────┘  │
│                            │            │
│                     ┌──────────────┐   │
│                     │   AWS S3     │   │
│                     │  (Evidence)  │   │
│                     └──────────────┘   │
│                                         │
│  External Services:                    │
│  - Twilio (SMS/Calls)                  │
│  - SendGrid (Email)                    │
│  - Google Maps API                     │
│                                         │
└─────────────────────────────────────────┘
```

### **Deployment Commands:**
```bash
# Backend deployment (using Docker)
docker build -t women-safety-backend .
docker run -p 5000:5000 -e DATABASE_URL=... women-safety-backend

# Frontend deployment
npm run build
scp -r build/* user@server:/var/www/html/

# Database migration
flask db upgrade

# Start services
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## 📈 **Performance Metrics**

### **System Requirements:**
- **Backend Server:** 2 vCPU, 4GB RAM, 50GB SSD
- **Database:** PostgreSQL 14+
- **Concurrent Users:** Up to 500 devices
- **Response Time:** < 3 seconds (alert dispatch)
- **Uptime:** 99.9% availability

### **Scalability:**
- **Horizontal Scaling:** Load balancer + multiple Flask instances
- **Caching:** Redis for session management
- **CDN:** Static assets served via CloudFlare
- **Database:** Read replicas for analytics queries

---

## 📚 **Documentation Structure**

```
women_safe/
├── README.md (Overview)
├── REFACTORED_ARCHITECTURE.md (This file)
├── ESP32_SETUP_GUIDE.md (Hardware setup)
├── API_DOCUMENTATION.md (Complete API reference)
├── DEPLOYMENT_GUIDE.md (Production deployment)
├── USER_MANUAL.md (End-user guide)
└── TESTING_GUIDE.md (QA procedures)
```

---

## 🎯 **Future Enhancements**

### **Phase 2 (Next 6 months):**
- ✅ **Video Streaming:** Live video feed during emergencies
- ✅ **Geofencing:** Alert if user leaves safe zone
- ✅ **Fall Detection:** Accelerometer-based fall detection
- ✅ **Voice Commands:** "Help me" voice activation
- ✅ **Multi-Language:** Support regional languages

### **Phase 3 (1 year):**
- ✅ **Community Network:** Nearby volunteers can respond
- ✅ **Predictive Analytics:** ML model to predict unsafe zones
- ✅ **Wearable Integration:** Smartwatch app
- ✅ **Blockchain:** Immutable evidence logging
- ✅ **AR Navigation:** Augmented reality escape routes

---

## 📞 **Support & Contact**

**Project Team:**
- GOPIKAA. T (22UCS045)
- DASARI DEEPTHIKA DEVI (22CSL002)
- KAYALVIZHI. A (22UCS076)

**Guide:** Mrs. S. DEEBA  
**Institution:** Sri Manakula Vinayagar Engineering College

**Emergency Helpline:** 100 (Police) | 1091 (Women Helpline)

---

**Last Updated:** December 23, 2025  
**Version:** 2.0  
**License:** MIT (Open Source)
