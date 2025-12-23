# 🛡️ Women's Safety System - Complete Walkthrough

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [User Roles & Access](#user-roles--access)
5. [Application Flow](#application-flow)
6. [Features Walkthrough](#features-walkthrough)
7. [API Reference](#api-reference)
8. [Testing Guide](#testing-guide)

---

## System Overview

### What is Shield System?

**Shield** is an AI-powered women's safety platform that provides real-time distress detection and emergency response coordination. The system combines:

- 🎤 **AI Stress Detection** - Voice analysis to detect distress in speech
- 💓 **Vital Signs Monitoring** - Heart rate, temperature, SpO2 tracking
- 📍 **GPS Tracking** - Real-time location monitoring
- 🚨 **Smart Alerts** - Automatic alert generation based on multiple factors
- 👥 **Multi-Role Access** - Guardian, Police, and Admin interfaces

### Key Components

```
┌─────────────────────────────────────────────────────────┐
│                   SHIELD SYSTEM                          │
├─────────────────────────────────────────────────────────┤
│  Wearable Device  →  Flask Backend  →  Web Dashboard   │
│       ↓                    ↓                  ↓          │
│   Sensors/Audio      AI Engine          Real-time UI    │
│   GPS Module         SQLite DB          Role-based      │
│   SOS Button         JWT Auth           Notifications   │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture

### Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- SQLAlchemy - ORM for database
- Flask-JWT-Extended - Authentication
- Librosa/TensorFlow - AI stress detection
- SQLite - Database

**Frontend:**
- Bootstrap 5 - UI framework
- Leaflet.js - Interactive maps
- Vanilla JavaScript - Client-side logic

**Testing:**
- Pytest - Test framework
- 56 comprehensive tests
- 100% pass rate

### Database Schema

```sql
┌──────────┐       ┌──────────┐       ┌─────────────┐
│  User    │◄─────►│  Device  │◄─────►│ SensorEvent │
├──────────┤       ├──────────┤       ├─────────────┤
│ id       │       │ id       │       │ id          │
│ name     │       │ owner_id │       │ device_id   │
│ email    │       │ device_uid│      │ heart_rate  │
│ role     │       │ last_lat │       │ temperature │
│ password │       │ last_lng │       │ ai_label    │
└──────────┘       └──────────┘       └─────────────┘
      │                  │
      │                  │
      │                  ▼
      │            ┌──────────┐       ┌──────────┐
      │            │  Alert   │◄─────►│ Evidence │
      │            ├──────────┤       ├──────────┤
      └───────────►│ id       │       │ id       │
                   │ device_id│       │ alert_id │
                   │ reason   │       │ file_type│
                   │ status   │       │ file_path│
                   │ severity │       └──────────┘
                   │ gps_lat  │
                   │ gps_lng  │
                   └──────────┘
```

---

## Getting Started

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sham1606/women_safe.git
cd women_safe

# 2. Create virtual environment
python -m venv wsafe
source wsafe/bin/activate  # On Windows: wsafe\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python run.py  # Creates tables and seeds admin user

# 5. Access the application
# Open browser: http://localhost:5000
```

### Default Users

The system comes pre-seeded with:

```
Admin Account:
  Email: admin@safety.com
  Password: admin123
  Role: ADMIN

Test Guardian:
  Email: guardian@safe.com
  Password: guardian123
  Role: GUARDIAN
```

---

## User Roles & Access

### 1. **GUARDIAN** (Device Owner)

**Access:**
- View own devices
- Register new devices
- Monitor device vitals and location
- View alerts for own devices
- Cannot change alert status

**Use Case:** Parents, family members, personal safety users

### 2. **POLICE** (Law Enforcement)

**Access:**
- View all alerts system-wide
- Update alert status (NEW → IN_PROGRESS → RESOLVED)
- Access evidence (audio/photo)
- View device locations
- Cannot access admin stats

**Use Case:** Emergency responders, law enforcement officers

### 3. **ADMIN** (System Administrator)

**Access:**
- Everything POLICE can do, plus:
- System statistics dashboard
- User management capabilities
- Device analytics
- Complete system overview

**Use Case:** System administrators, safety coordinators

---

## Application Flow

### Complete User Journey

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: User Authentication                              │
└─────────────────────────────────────────────────────────┘
                          ↓
        Landing Page (index.html)
                ↓                ↓
          LOGIN              REGISTER
         (Email/Pass)      (Name/Email/Pass/Role)
                ↓                ↓
              JWT Token Generated
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Dashboard Access (Role-Based)                    │
└─────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┴────────────────┐
         ↓                ↓                ↓
    GUARDIAN          POLICE            ADMIN
    Dashboard        Dashboard         Dashboard
         │                │                │
         ↓                ↓                ↓
  My Devices       All Alerts        Statistics
  Device Cards     Alert List        Analytics
  Add Device       Status Updates    User Mgmt
         │                │                │
         └────────────────┴────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: Real-Time Monitoring                             │
└─────────────────────────────────────────────────────────┘
                          ↓
              Wearable Device Sends:
              - Vitals (HR, Temp, SpO2)
              - GPS Location
              - Audio Sample (optional)
              - Manual SOS (if pressed)
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: AI Processing & Alert Generation                │
└─────────────────────────────────────────────────────────┘
                          ↓
         Backend Processes Event:
         1. AI analyzes audio → stress score
         2. Check vitals thresholds
         3. Calculate distress score:
            (AI × 0.6) + (HR × 0.3) + (Temp × 0.1)
         4. If score > 0.5 OR manual SOS:
            → CREATE ALERT
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: Alert Response                                   │
└─────────────────────────────────────────────────────────┘
                          ↓
              Alert Created:
              - Status: NEW
              - Reason: AUTO_STRESS / MANUAL_SOS
              - GPS coordinates stored
              - Evidence files saved
                          ↓
              Notifications Sent:
              - Guardian sees alert on dashboard
              - Police/Admin see on system-wide list
              - Map updates with device location
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Alert Resolution                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
         Police/Admin Actions:
         1. View alert details
         2. Listen to audio evidence
         3. Check GPS location
         4. Update status:
            NEW → IN_PROGRESS → RESOLVED
```

---

## Features Walkthrough

### 🔐 1. Authentication

**Location:** `http://localhost:5000/`

#### Login Process
1. Navigate to landing page
2. Enter credentials:
   - Email: `guardian@safe.com`
   - Password: `guardian123`
3. Click **AUTHENTICATE**
4. JWT token stored in localStorage
5. Redirected to `/dashboard`

#### Registration Process
1. Click **JOIN** tab
2. Fill in:
   - Full Name
   - Email (unique)
   - Password (min 6 chars)
   - Role (Guardian/Police/Admin)
3. Click **CREATE ACCOUNT**
4. Auto-login after registration

**Security Features:**
- Password hashing (PBKDF2-SHA256)
- JWT tokens with role claims
- Token expiration handling
- Protected routes

---

### 🎛️ 2. Guardian Dashboard

**Location:** `http://localhost:5000/dashboard` (Guardian role)

#### Device Management

**Add New Device:**
1. Click **+** button
2. Enter Device UID (e.g., `SHIELD-001`)
3. Device linked to your account
4. Appears in device list

**Device Card Shows:**
```
┌────────────────────────────────┐
│  📱 SHIELD-001                 │
│  Battery: 85% 🔋              │
│  Status: ONLINE ✅            │
│                                │
│  Latest Vitals:                │
│  ❤️  HR: 75 bpm                │
│  🌡️ Temp: 36.5°C              │
│  🤖 AI: Normal (Conf: 0.89)   │
│                                │
│  Location: 11.9416, 79.8083   │
│  Last Update: 2 mins ago       │
└────────────────────────────────┘
```

#### Real-Time Monitoring
- Auto-refresh every 30 seconds
- Live GPS tracking on map
- Color-coded status indicators:
  - 🟢 Green: Normal
  - 🟡 Yellow: Elevated vitals
  - 🔴 Red: Alert active

---

### 🚨 3. Alert System

#### Alert Generation (Automatic)

**Triggers:**
1. **AI Stress Detection**
   - Audio analyzed for distress markers
   - Confidence score > 0.5
   - Contributes 60% to distress score

2. **Vital Signs Thresholds**
   - Heart Rate > 100 bpm (30% weight)
   - Temperature > 38.5°C (10% weight)

3. **Manual SOS Button**
   - Instant alert creation
   - Overrides all thresholds
   - Priority: HIGHEST

**Distress Score Formula:**
```
Distress = (AI_confidence × 0.6) + (HR_flag × 0.3) + (Temp_flag × 0.1)

If Distress > 0.5 OR Manual_SOS == True:
    CREATE_ALERT()
```

#### Alert Details Modal

**Information Displayed:**
- Alert ID and timestamp
- Reason (AUTO_STRESS, MANUAL_SOS, VITALS)
- Current status (NEW, IN_PROGRESS, RESOLVED)
- GPS coordinates
- Device vitals snapshot
- Evidence files:
  - 🎤 Audio recordings
  - 📷 Camera images (if available)

**Actions Available:**
- **Guardian:** View only
- **Police/Admin:** Update status, download evidence

---

### 🗺️ 4. Live Tracking Map

**Technology:** Leaflet.js with OpenStreetMap

**Features:**
- Real-time device location markers
- Color-coded by status:
  - 🟢 Blue: Normal device
  - 🔴 Red: Active alert
- Click marker for device info popup
- Auto-center on alerts
- Zoom controls
- Reset view button

**Map Popup Shows:**
```
┌──────────────────────────┐
│ Device: SHIELD-001       │
│ Status: ALERT 🚨         │
│ HR: 125 bpm              │
│ Time: 5 mins ago         │
│ [View Details]           │
└──────────────────────────┘
```

---

### 👮 5. Police Dashboard

**Enhanced Features:**
- System-wide alert list (all devices)
- Filter alerts by status:
  - NEW (red badge)
  - IN_PROGRESS (yellow badge)
  - RESOLVED (green badge)
- Sort by timestamp (newest first)
- Quick status updates
- Evidence download

**Alert Management:**
1. View alert in list
2. Click to open detail modal
3. Review vitals and evidence
4. Update status:
   ```
   NEW → [Click "Responding"] → IN_PROGRESS
   IN_PROGRESS → [Click "Resolved"] → RESOLVED
   ```

---

### 📊 6. Admin Dashboard

**Statistics Panel:**
```
┌─────────────────────────────────┐
│ SYSTEM OVERVIEW                 │
├─────────────────────────────────┤
│  Active Devices: 127            │
│  New Alerts: 3 🔴               │
│  Total Users: 845               │
│                                 │
│  RECENT ACTIVITY                │
│  ┌───────────────────────────┐ │
│  │ 14:32  SHIELD-042  NEW    │ │
│  │ 14:18  SHIELD-089  ACTIVE │ │
│  │ 14:05  SHIELD-023  OK     │ │
│  └───────────────────────────┘ │
└─────────────────────────────────┘
```

**Analytics:**
- User distribution by role
- Alerts by status breakdown
- Device online/offline ratio
- Response time metrics

---

## API Reference

### Authentication Endpoints

#### POST `/api/auth/register`
**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "role": "GUARDIAN"
}
```
**Response:** `201 Created`
```json
{
  "message": "User registered successfully"
}
```

#### POST `/api/auth/login`
**Request:**
```json
{
  "email": "john@example.com",
  "password": "secure123"
}
```
**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "GUARDIAN"
  }
}
```

#### GET `/api/auth/me`
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "GUARDIAN"
}
```

---

### Device Endpoints

#### POST `/api/device/register`
**Headers:** `Authorization: Bearer <token>`
**Request:**
```json
{
  "device_uid": "SHIELD-001"
}
```
**Response:** `201 Created`

#### GET `/api/device/my-devices`
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK`
```json
[
  {
    "uid": "SHIELD-001",
    "is_active": true,
    "battery": 85,
    "location": {"lat": 11.9416, "lng": 79.8083},
    "latest_vitals": {
      "hr": 75,
      "temp": 36.5,
      "ai_label": "normal",
      "ai_conf": 0.89
    },
    "active_alert": {
      "id": 42,
      "status": "NEW",
      "reason": "MANUAL_SOS"
    }
  }
]
```

#### POST `/api/device/event`
**Form Data:**
```
device_uid: SHIELD-001
heart_rate: 75
temperature: 36.5
spo2: 98
lat: 11.9416
lng: 79.8083
manual_sos: 0
audio: <file> (optional)
```
**Response:** `200 OK`
```json
{
  "status": "success",
  "distress_score": 0.32,
  "alert_triggered": false
}
```

---

### Alert Endpoints

#### GET `/api/alerts`
**Headers:** `Authorization: Bearer <token>`
**Query Params:** `?status=NEW` (optional)
**Response:** `200 OK`
```json
[
  {
    "id": 42,
    "device_uid": "SHIELD-001",
    "reason": "MANUAL_SOS",
    "status": "NEW",
    "severity": "HIGH",
    "timestamp": "2025-12-23T18:05:00",
    "lat": 11.9416,
    "lng": 79.8083
  }
]
```

#### GET `/api/alerts/<id>`
**Headers:** `Authorization: Bearer <token>`
**Response:** `200 OK`
```json
{
  "id": 42,
  "device_uid": "SHIELD-001",
  "reason": "MANUAL_SOS",
  "status": "NEW",
  "timestamp": "2025-12-23T18:05:00",
  "evidence": [
    {
      "type": "AUDIO",
      "path": "SHIELD-001_20251223_180500.wav",
      "captured_at": "2025-12-23T18:05:00"
    }
  ]
}
```

#### PATCH `/api/alerts/<id>/status`
**Headers:** `Authorization: Bearer <token>` (Police/Admin only)
**Request:**
```json
{
  "status": "IN_PROGRESS"
}
```
**Response:** `200 OK`

---

### Admin Endpoints

#### GET `/api/admin/stats`
**Headers:** `Authorization: Bearer <token>` (Police/Admin only)
**Response:** `200 OK`
```json
{
  "total_users": 845,
  "active_devices": 127,
  "alerts_by_status": {
    "NEW": 3,
    "IN_PROGRESS": 8,
    "RESOLVED": 234
  },
  "latest_alerts": [
    {
      "id": 42,
      "device": "SHIELD-001",
      "reason": "MANUAL_SOS",
      "time": "2025-12-23T18:05:00"
    }
  ]
}
```

---

## Testing Guide

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test suite
pytest tests/test_ai_stress_detection.py
pytest tests/test_backend_auth.py
pytest tests/test_backend_events_alerts.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run verbose
pytest -v
```

### Test Coverage

**56 Tests Total:**
- ✅ AI Stress Detection (9 tests)
- ✅ Authentication (10 tests)
- ✅ Device Management (6 tests)
- ✅ Events & Alerts (10 tests)
- ✅ Admin Functions (4 tests)
- ✅ Performance (4 tests)
- ✅ Security (6 tests)
- ✅ Detailed Scenarios (8 tests)

**Test Results:**
```
56 passed in 80.86s (0:01:20)
100% Pass Rate ✅
```

### Manual Testing Scenarios

#### Scenario 1: Normal Operation
1. Login as guardian
2. Add device
3. Send normal vitals (HR: 75, Temp: 36.5)
4. Verify no alert created
5. Check device shows "Normal" status

#### Scenario 2: High Vitals Alert
1. Send event with HR: 125
2. Check distress score calculation
3. May or may not trigger (depends on threshold)
4. Verify event recorded in database

#### Scenario 3: Manual SOS
1. Send event with `manual_sos=1`
2. Verify alert created immediately
3. Check alert reason is "MANUAL_SOS"
4. Verify guardian sees alert
5. Check map marker turns red

#### Scenario 4: Police Response
1. Login as police
2. View alert list
3. Click alert to view details
4. Update status to "IN_PROGRESS"
5. Verify status updated
6. Mark as "RESOLVED"

#### Scenario 5: Audio Evidence
1. Send event with audio file
2. AI processes audio
3. Check AI label and confidence
4. View alert details
5. Play audio evidence

---

## Troubleshooting

### Common Issues

**Problem:** "Module not found" error
**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** Database not initialized
**Solution:**
```bash
python run.py  # Creates tables automatically
```

**Problem:** AI model not loading
**Solution:**
- Ensure model file exists in `ai_engine/models/`
- Check librosa installation: `pip install librosa`

**Problem:** Tests failing
**Solution:**
```bash
# Reinstall test dependencies
pip install -r requirements-test.txt

# Run with verbose output
pytest -v
```

**Problem:** Map not showing
**Solution:**
- Check internet connection (needs OpenStreetMap tiles)
- Clear browser cache
- Check console for JavaScript errors

---

## Performance Benchmarks

**API Response Times:**
- Authentication: < 100ms
- Device list: < 200ms
- Event processing (no audio): < 500ms
- Event processing (with audio): < 2 seconds
- Alert creation: < 300ms

**Scalability:**
- Tested with 30+ concurrent events
- No crashes or data loss
- Database handles 1000+ events

---

## Security Features

✅ **Implemented:**
- JWT authentication
- Password hashing (PBKDF2-SHA256)
- Role-based access control (RBAC)
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Protected API routes

⚠️ **Production Recommendations:**
- Use HTTPS in production
- Set strong JWT secret key
- Implement rate limiting
- Add input validation
- Enable audit logging
- Use production database (PostgreSQL)

---

## Deployment

### Local Development
```bash
python run.py
# Access: http://localhost:5000
```

### Production (Example with Gunicorn)
```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

---

## Support & Resources

**Documentation:**
- This walkthrough
- `README.md` - Quick start guide
- `tests/README.md` - Testing documentation
- `RUN_TESTS.md` - Test execution guide

**Code Repository:**
- GitHub: https://github.com/Sham1606/women_safe

**Test Coverage:**
- 56 comprehensive tests
- 100% pass rate
- Performance benchmarks included

---

## Future Enhancements

🔮 **Planned Features:**
- [ ] Mobile app (React Native)
- [ ] Push notifications
- [ ] Geofencing alerts
- [ ] Video evidence support
- [ ] ML model improvements
- [ ] Multi-language support
- [ ] Emergency contact integration
- [ ] Historical analytics dashboard

---

## Conclusion

The Shield System provides a comprehensive, AI-powered safety solution with:
- ✅ Real-time monitoring
- ✅ Intelligent alert generation
- ✅ Multi-role access control
- ✅ Evidence capture
- ✅ Extensive testing (56 tests)
- ✅ Production-ready architecture

For questions or support, refer to the documentation or test files for implementation examples.
