# 🛡️ AI-Powered Proactive Women's Safety Device - Refactored Architecture

## 📋 Project Overview

**Title:** An AI-Powered Proactive Women's Safety Device  
**Institution:** Sri Manakula Vinayagar Engineering College, Puducherry  
**Department:** Computer Science and Engineering  
**Academic Year:** 2025-2026

**Team Members:**
- GOPIKAA. T (22UCS045)
- DASARI DEEPTHIKA DEVI (22CSL002)
- KAYALVIZHI. A (22UCS076)

**Project Guide:** Mrs. S. DEEBA

---

## 🎯 Problem Statement

Women's safety remains a critical global concern. Traditional safety solutions have significant limitations:

### ❌ **Existing System Issues:**
1. **Manual Activation Required** - Victim must press button/open app
2. **Smartphone Dependency** - Unreliable if phone is unavailable/dead
3. **Connectivity Issues** - Requires internet/Bluetooth
4. **No Contextual Awareness** - Cannot detect distress automatically
5. **Limited Evidence Collection** - No automatic capture of surroundings
6. **Delayed Response** - Time lost in manual activation

### ✅ **Proposed Solution:**

A **standalone, AI-powered IoT device** that:
- **Detects distress automatically** using dual-mode stress detection
- **Operates independently** of smartphones
- **Triggers multi-layered emergency protocol** automatically
- **Captures evidence** (GPS + Audio + Images)
- **Sends simultaneous alerts** to police, family, and authorities

---

## 🏗️ System Architecture

### **3-Tier Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: IoT DEVICE                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ESP32-CAM    │  │ Microphone   │  │ Stress       │     │
│  │ (Image)      │  │ (Voice)      │  │ Sensor (HR)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ GPS Module   │  │ Buzzer       │  │ Manual       │     │
│  │ (Location)   │  │ (Alarm)      │  │ Button       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│             API: POST /api/device/event                      │
│                     (FormData)                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              TIER 2: BACKEND SERVER (Flask)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          AI INFERENCE ENGINE                         │  │
│  │  • Voice Stress Detection (ML Model)                 │  │
│  │  • Physiological Analysis (Heart Rate)               │  │
│  │  • Distress Score Calculation                        │  │
│  │  • Alert Decision Engine                             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          DATABASE (SQLite/PostgreSQL)                │  │
│  │  • Users, Devices, SensorEvents                      │  │
│  │  • Alerts, Evidence                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       NOTIFICATION SERVICE (Twilio API)              │  │
│  │  • SMS to Family/Police                              │  │
│  │  • Email Alerts                                      │  │
│  │  • Push Notifications                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│        REST API Endpoints (JWT Authentication)               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            TIER 3: WEB APPLICATION (Frontend)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         GUARDIAN/FAMILY PORTAL                       │  │
│  │  • Device Status Dashboard                           │  │
│  │  • Real-time GPS Tracking Map                        │  │
│  │  • Alert Notifications                               │  │
│  │  • Evidence Viewer (Audio/Images)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         POLICE/ADMIN PANEL                           │  │
│  │  • System-wide Alert Feed                            │  │
│  │  • Evidence Database                                 │  │
│  │  • Case Management                                   │  │
│  │  • Analytics & Heatmaps                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│     Tech Stack: HTML5, CSS3, Bootstrap 5, JavaScript,       │
│     Leaflet.js (Maps), Chart.js (Analytics)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow Pipeline

### **Device Workflow (Based on Flowchart)**

```
START → Device Power On
  ↓
Initialize Sensors (HR, Temp, Microphone, Camera, GPS)
  ↓
Start Dual-Mode Stress Detection Engine
  ↓
┌─────────────────────────────────────┐
│  Stress/Distress Detected?          │
└─────┬─────YES─────┬─────NO──────────┘
      │             │
      ↓             ↓
  AUTOMATIC     Wait for Manual Trigger
    MODE            MODE
      │             │
      ↓             ↓
  AI Voice     Manual Button Pressed?
  Analysis         │
      │         ┌───┴───┐
  Threat       NO     YES
  Confirmed?    │      │
      │         ↓      ↓
    YES    Continue  Activate
      │    Normal    Camera
      ↓    Monitor    ↓
  Trigger           Fetch GPS
  Alert System       ↓
      │         Send Alert
      │              ↓
      └──────┬───────┘
             │
             ▼
  ┌───────────────────────┐
  │  EMERGENCY PROTOCOL   │
  └───────────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
  Activate      Fetch GPS
  Camera      Coordinates
      ↓             ↓
  Capture   Transmit Distress
  Images      Signal + Location
      ↓             ↓
  Send to      Activate
  Server     High-Intensity
      ↓         Buzzer
      │             ↓
      │    Notify Emergency
      │   Contacts & Police
      │             ↓
      └──────┬──────┘
             │
             ▼
  Store Event Logs Securely
             │
             ↓
           END
```

---

## 🤖 AI Model Pipeline

### **Ensemble Audio Stress Detection Algorithm**

```python
# Based on algo.txt requirements

# Step 1: Data Collection
- Labeled audio dataset (stressed / non-stressed voices)
- Real-time audio capture from microphone

# Step 2: Audio Preprocessing
- Noise removal (spectral subtraction)
- Normalization (amplitude scaling)
- Segmentation (fixed windows)

# Step 3: Feature Extraction
MFCC (Mel-Frequency Cepstral Coefficients)  # Voice characteristics
Chroma Features                              # Pitch patterns
Mel Spectrogram                              # Frequency distribution
Spectral Contrast                            # Texture patterns
Zero Crossing Rate                           # Signal smoothness

# Step 4: Model Training
Base Classifiers:
  1. Logistic Regression
  2. Random Forest
  3. Gradient Boosting
  4. Support Vector Machine (SVM)

# Step 5: Ensemble Method
Soft Voting Ensemble:
  - Aggregate probability scores from all models
  - Weight by model confidence
  - Final prediction = weighted average

# Step 6: Evaluation Metrics
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix
- ROC-AUC Curve

# Step 7: Real-time Inference
Input: Audio buffer (WAV format)
Output: {'label': 'stressed', 'confidence': 0.87}

# Step 8: Distress Score Calculation
Distress Score = (
    AI_Confidence (if stressed) × 0.6 +
    Heart_Rate_Abnormal × 0.3 +
    Temperature_Abnormal × 0.1
)

if Distress_Score > 0.5 OR Manual_SOS:
    TRIGGER_ALERT()
```

---

## 📡 IoT Device API Specification

### **Device-to-Server Communication**

#### **Endpoint:** `POST /api/device/event`

**Purpose:** IoT device sends sensor data, audio, and triggers alerts

**Content-Type:** `multipart/form-data`

**Request Parameters:**

```json
{
  "device_uid": "SHIELD-001",           // Required: Device unique ID
  "heart_rate": 75.0,                   // Optional: BPM
  "temperature": 36.5,                  // Optional: Celsius
  "spo2": 98.0,                         // Optional: Oxygen saturation
  "lat": 11.9416,                       // Optional: Latitude
  "lng": 79.8083,                       // Optional: Longitude
  "battery_level": 85,                  // Optional: %
  "manual_sos": 0,                      // 0 or 1 (manual trigger)
  "audio": <file>,                      // Optional: WAV audio file
  "image": <file>                       // Optional: JPEG image
}
```

**Response (Success):**

```json
{
  "status": "success",
  "distress_score": 0.75,
  "alert_triggered": true,
  "alert_id": 42,
  "message": "Emergency protocol activated"
}
```

**Response (Normal):**

```json
{
  "status": "success",
  "distress_score": 0.12,
  "alert_triggered": false,
  "message": "Status updated"
}
```

**ESP32 Example Code (Conceptual - NOT included in refactor):**

```cpp
// This is REFERENCE ONLY - You mentioned no Arduino code needed

// Device sends multipart form data
HTTPClient http;
http.begin("http://server.com/api/device/event");

http.addHeader("Content-Type", "multipart/form-data");
String boundary = "----FormBoundary";

String formData = "";
formData += "--" + boundary + "\r\n";
formData += "Content-Disposition: form-data; name=\"device_uid\"\r\n\r\n";
formData += "SHIELD-001\r\n";

formData += "--" + boundary + "\r\n";
formData += "Content-Disposition: form-data; name=\"heart_rate\"\r\n\r\n";
formData += String(heartRate) + "\r\n";

// ... add other fields

int httpCode = http.POST(formData);
```

---

## 🗄️ Database Schema

### **Enhanced Schema (Based on Requirements)**

```sql
-- Users Table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'GUARDIAN',  -- GUARDIAN, POLICE, ADMIN
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Emergency Contacts (JSON field)
    emergency_contacts TEXT,  -- [{"name": "Mom", "phone": "+91..."}]
    
    -- Notification Preferences
    notify_email BOOLEAN DEFAULT 1,
    notify_sms BOOLEAN DEFAULT 1,
    notify_push BOOLEAN DEFAULT 1
);

-- Devices Table
CREATE TABLE device (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_uid VARCHAR(50) UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL,
    device_name VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    last_seen DATETIME,
    battery_level INTEGER,
    last_lat FLOAT,
    last_lng FLOAT,
    
    -- Device Configuration
    hr_threshold INTEGER DEFAULT 100,      -- Alert if HR > this
    temp_threshold FLOAT DEFAULT 38.5,     -- Alert if Temp > this
    ai_confidence_threshold FLOAT DEFAULT 0.6,  -- AI threshold
    
    FOREIGN KEY (owner_id) REFERENCES user(id)
);

-- Sensor Events Table
CREATE TABLE sensor_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Physiological Data
    heart_rate FLOAT,
    spo2 FLOAT,
    temperature FLOAT,
    
    -- AI Analysis
    raw_stress_score FLOAT,
    ai_label VARCHAR(20),          -- 'normal' or 'stressed'
    ai_confidence FLOAT,
    
    -- Evidence
    has_audio BOOLEAN DEFAULT 0,
    audio_path VARCHAR(200),
    has_image BOOLEAN DEFAULT 0,
    image_path VARCHAR(200),
    
    FOREIGN KEY (device_id) REFERENCES device(id),
    INDEX idx_device_timestamp (device_id, timestamp)
);

-- Alerts Table
CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Alert Details
    reason VARCHAR(50),            -- AUTO_STRESS, MANUAL_SOS, HR_SPIKE, etc.
    status VARCHAR(20) DEFAULT 'NEW',  -- NEW, IN_PROGRESS, RESOLVED
    severity VARCHAR(20) DEFAULT 'HIGH',  -- LOW, MEDIUM, HIGH, CRITICAL
    
    -- Location
    gps_lat FLOAT,
    gps_lng FLOAT,
    location_accuracy FLOAT,       -- GPS accuracy in meters
    
    -- Response Tracking
    acknowledged_by INTEGER,       -- User ID who acknowledged
    acknowledged_at DATETIME,
    resolved_by INTEGER,
    resolved_at DATETIME,
    resolution_notes TEXT,
    
    FOREIGN KEY (device_id) REFERENCES device(id),
    FOREIGN KEY (acknowledged_by) REFERENCES user(id),
    FOREIGN KEY (resolved_by) REFERENCES user(id),
    INDEX idx_status_timestamp (status, timestamp)
);

-- Evidence Table
CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    file_type VARCHAR(10),         -- AUDIO, IMAGE, VIDEO
    file_path VARCHAR(200),
    file_size INTEGER,             -- bytes
    mime_type VARCHAR(50),
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata
    duration FLOAT,                -- for audio/video (seconds)
    gps_lat FLOAT,
    gps_lng FLOAT,
    
    FOREIGN KEY (alert_id) REFERENCES alert(id)
);

-- Notifications Log
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    recipient_type VARCHAR(20),    -- FAMILY, POLICE, ADMIN
    recipient_id INTEGER,
    recipient_contact VARCHAR(100), -- phone/email
    
    notification_type VARCHAR(20), -- SMS, EMAIL, PUSH
    status VARCHAR(20),            -- SENT, DELIVERED, FAILED
    
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at DATETIME,
    error_message TEXT,
    
    FOREIGN KEY (alert_id) REFERENCES alert(id),
    FOREIGN KEY (recipient_id) REFERENCES user(id)
);
```

---

## 🔐 Security Measures

### **Data Protection:**

1. **Authentication:** JWT tokens with expiry
2. **Password Hashing:** PBKDF2-SHA256
3. **HTTPS:** SSL/TLS encryption in production
4. **Evidence Encryption:** AES-256 for stored files
5. **Access Control:** Role-based permissions
6. **Audit Logs:** Track all data access

### **Privacy Compliance:**

- User consent for data collection
- GDPR/local privacy law adherence
- Data retention policies
- Right to delete account and data

---

## 📊 Key Features Summary

| Feature | Implementation | Status |
|---------|----------------|--------|
| **Dual-Mode Stress Detection** | AI Voice + Physiological Sensors | ✅ Implemented |
| **Automatic Alert Triggering** | Distress score > threshold | ✅ Implemented |
| **Manual SOS Button** | Emergency override | ✅ Implemented |
| **GPS Location Tracking** | Real-time coordinates | ✅ Implemented |
| **Evidence Capture** | Audio + Images | ✅ Implemented |
| **Multi-Channel Alerts** | SMS + Email + Push | ⏳ Twilio Integration |
| **Family Portal** | Web dashboard | ✅ Implemented |
| **Police Admin Panel** | Evidence management | ✅ Implemented |
| **Live Monitoring** | Real-time device status | ✅ Implemented |
| **Analytics Dashboard** | Heatmaps, trends | ✅ Implemented |
| **Device Simulator** | Testing without hardware | ✅ Implemented |

---

## 🚀 Deployment Architecture

### **Production Setup:**

```
┌─────────────────────────────────────────────────┐
│         IoT Device (ESP32)                      │
│         - Connects via 4G/WiFi                  │
└──────────────┬──────────────────────────────────┘
               │
               ↓ HTTPS (Port 443)
┌─────────────────────────────────────────────────┐
│      Cloud Server (AWS/Azure/GCP)               │
│  ┌───────────────────────────────────────────┐ │
│  │  Load Balancer (Nginx)                    │ │
│  └───────────┬───────────────────────────────┘ │
│              ↓                                  │
│  ┌───────────────────────────────────────────┐ │
│  │  Flask App (Gunicorn Workers)             │ │
│  │  - AI Inference Engine                    │ │
│  │  - REST API                               │ │
│  └───────────┬───────────────────────────────┘ │
│              ↓                                  │
│  ┌───────────────────────────────────────────┐ │
│  │  PostgreSQL Database                      │ │
│  └───────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────┐ │
│  │  Redis Cache (Session Management)         │ │
│  └───────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────┐ │
│  │  S3/Cloud Storage (Evidence Files)        │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────┐
│      External Services                          │
│  - Twilio (SMS/Calls)                           │
│  - SendGrid (Email)                             │
│  - Firebase (Push Notifications)                │
└─────────────────────────────────────────────────┘
```

---

## 📈 Performance Metrics

### **System Requirements:**

- **Response Time:** < 2 seconds from detection to alert
- **AI Inference:** < 500ms for voice analysis
- **Uptime:** 99.9% availability
- **Concurrent Users:** 10,000+
- **Alert Delivery:** 95% within 5 seconds

### **AI Model Performance:**

- **Accuracy:** > 90%
- **False Positive Rate:** < 5%
- **False Negative Rate:** < 2% (critical)

---

## 🎓 Academic Contributions

### **Novel Features:**

1. **Dual-Mode Detection Engine:** Combining physiological + voice AI
2. **Smartphone-Independent Operation:** Standalone IoT device
3. **Proactive Threat Detection:** No manual activation needed
4. **Comprehensive Evidence Collection:** Legal admissibility
5. **Multi-Stakeholder Alert System:** Simultaneous family + police

### **Publications:**

- Conference paper submission planned
- Patent application under consideration

---

## 🔧 Technology Stack Summary

### **Hardware (IoT Device):**
- ESP32-CAM
- Microphone (MEMS)
- MAX30102 (Heart Rate + SpO2 Sensor)
- GPS Module (NEO-6M)
- High-Decibel Buzzer
- Battery Pack (Li-ion)

### **Backend:**
- Python 3.9+
- Flask 3.0
- TensorFlow / Scikit-learn (AI)
- SQLAlchemy ORM
- JWT Authentication
- Twilio API

### **Frontend:**
- HTML5, CSS3, Bootstrap 5
- Vanilla JavaScript
- Leaflet.js (Maps)
- Chart.js (Analytics)

### **Database:**
- SQLite (Development)
- PostgreSQL (Production)

### **Deployment:**
- Docker
- Gunicorn
- Nginx
- AWS/Azure/GCP

---

## 📚 References

Based on 8 research papers reviewed in literature survey (see PROJECT_PHASE_I_REPORT.docx)

---

**Document Version:** 2.0  
**Last Updated:** December 23, 2025  
**Status:** Refactored and Ready for Implementation
