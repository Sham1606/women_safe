# 📚 **Complete API Documentation**

## **Base URL**
```
Production: https://api.womensafety.com
Development: http://localhost:5000
```

## **Authentication**

All protected endpoints require JWT authentication.

### **Get JWT Token:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "user@example.com",
    "role": "GUARDIAN"
  }
}
```

### **Use Token in Requests:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## **1. Authentication Endpoints**

### **Register User**
```http
POST /api/auth/register
Content-Type: application/json

Request:
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securePassword123",
  "phone": "+919876543210",
  "role": "GUARDIAN",
  "device_uid": "SHIELD-ESP32-001" // Optional
}

Response 201:
{
  "message": "User registered successfully"
}

Errors:
400: Missing required fields
400: Email already exists
```

### **Login**
```http
POST /api/auth/login
Content-Type: application/json

Request:
{
  "email": "jane@example.com",
  "password": "securePassword123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "GUARDIAN"
  }
}

Errors:
400: Email and password required
401: Invalid credentials
```

### **Get Current User**
```http
GET /api/auth/me
Authorization: Bearer <JWT>

Response 200:
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "GUARDIAN",
  "phone": "+919876543210"
}

Errors:
401: Token missing or invalid
404: User not found
```

---

## **2. Device Endpoints**

### **Register Device**
```http
POST /api/device/register
Authorization: Bearer <JWT> (optional)
Content-Type: application/json

Request:
{
  "device_uid": "SHIELD-ESP32-001",
  "email": "jane@example.com" // Required if no JWT
}

Response 201:
{
  "message": "Device successfully linked to account",
  "id": 42
}

Errors:
400: device_uid is required
401: Authentication required or provide an email
404: User not found
```

### **Get My Devices**
```http
GET /api/device/my-devices
Authorization: Bearer <JWT>

Response 200:
[
  {
    "uid": "SHIELD-ESP32-001",
    "is_active": true,
    "battery": 85,
    "location": {
      "lat": 11.9416,
      "lng": 79.8083
    },
    "latest_vitals": {
      "hr": 72,
      "temp": 36.5,
      "spo2": 98,
      "ai_label": "normal",
      "ai_conf": 0.95
    },
    "active_alert": {
      "id": null,
      "status": null,
      "reason": null
    },
    "last_update": "2025-12-23T23:15:00Z"
  }
]

Errors:
401: Token missing or invalid
```

### **Send Device Event (ESP32)**
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
- audio: <audio_file.wav> (optional)
- image: <image.jpg> (optional)

Response 200:
{
  "status": "success",
  "distress_score": 0.72,
  "alert_triggered": true,
  "alert_id": 123
}

Errors:
404: Device not found
500: Server error
```

---

## **3. Alert Endpoints**

### **List Alerts**
```http
GET /api/alerts
Authorization: Bearer <JWT>

Query Parameters (optional):
- status: NEW | IN_PROGRESS | RESOLVED
- severity: HIGH | MEDIUM | LOW
- since: ISO 8601 timestamp
- limit: integer (max 100)

Response 200:
[
  {
    "id": 123,
    "device_uid": "SHIELD-ESP32-001",
    "reason": "AUTO_STRESS",
    "status": "NEW",
    "severity": "HIGH",
    "timestamp": "2025-12-23T23:15:00Z",
    "lat": 11.9416,
    "lng": 79.8083
  }
]

Notes:
- Guardians see only their own alerts
- Police/Admin see all alerts
```

### **Get Alert Details**
```http
GET /api/alerts/{alert_id}
Authorization: Bearer <JWT>

Response 200:
{
  "id": 123,
  "device_uid": "SHIELD-ESP32-001",
  "owner_name": "Jane Doe",
  "reason": "AUTO_STRESS",
  "status": "NEW",
  "severity": "HIGH",
  "timestamp": "2025-12-23T23:15:00Z",
  "gps": {
    "lat": 11.9416,
    "lng": 79.8083
  },
  "vitals": {
    "heart_rate": 115,
    "temperature": 37.8,
    "spo2": 97
  },
  "evidence": [
    {
      "type": "AUDIO",
      "path": "evidence/SHIELD-ESP32-001_20251223_231500.wav",
      "captured_at": "2025-12-23T23:15:00Z"
    },
    {
      "type": "IMAGE",
      "path": "evidence/SHIELD-ESP32-001_20251223_231502.jpg",
      "captured_at": "2025-12-23T23:15:02Z"
    }
  ]
}

Errors:
404: Alert not found
403: Access denied (not your alert)
```

### **Update Alert Status (Police/Admin)**
```http
PATCH /api/alerts/{alert_id}/status
Authorization: Bearer <JWT> (Police/Admin only)
Content-Type: application/json

Request:
{
  "status": "IN_PROGRESS",
  "notes": "Patrol unit dispatched" // Optional
}

Response 200:
{
  "message": "Updated",
  "alert": {
    "id": 123,
    "status": "IN_PROGRESS",
    "updated_by": "Officer Sharma"
  }
}

Errors:
403: Unauthorized (not Police/Admin)
404: Alert not found
```

---

## **4. AI Inference Endpoint**

### **Predict Stress from Audio**
```http
POST /api/ai/predict-stress
Content-Type: multipart/form-data

Request:
- audio: <audio_file.wav>

Response 200:
{
  "label": "stressed",
  "confidence": 0.85,
  "timestamp": "2025-12-23T23:15:00Z",
  "features": {
    "mfcc_mean": [...],
    "chroma_mean": [...]
  }
}

Errors:
400: No audio file provided
500: AI model error
```

---

## **5. Admin Endpoints**

### **Get System Statistics**
```http
GET /api/admin/stats
Authorization: Bearer <JWT> (Police/Admin only)

Response 200:
{
  "total_users": 120,
  "active_devices": 95,
  "alerts_by_status": {
    "NEW": 2,
    "IN_PROGRESS": 1,
    "RESOLVED": 47
  },
  "latest_alerts": [
    {
      "id": 123,
      "device": "SHIELD-ESP32-001",
      "reason": "AUTO_STRESS",
      "time": "2025-12-23T23:15:00Z"
    }
  ]
}

Errors:
403: Unauthorized
```

---

## **6. Evidence Files**

### **Serve Evidence**
```http
GET /static/evidence/{filename}

Example:
GET /static/evidence/SHIELD-ESP32-001_20251223_231500.wav

Response:
- Audio/Image file (direct download)

Notes:
- No authentication required (evidence links are secure/unique)
- Consider adding signed URLs for production
```

---

## **7. Emergency Contacts (New)**

### **Add Emergency Contact**
```http
POST /api/contacts/add
Authorization: Bearer <JWT>
Content-Type: application/json

Request:
{
  "name": "John Doe",
  "phone": "+919876543211",
  "email": "john@example.com",
  "relationship": "Brother",
  "priority": 1
}

Response 201:
{
  "message": "Contact added",
  "id": 10
}
```

### **List Emergency Contacts**
```http
GET /api/contacts
Authorization: Bearer <JWT>

Response 200:
[
  {
    "id": 10,
    "name": "John Doe",
    "phone": "+919876543211",
    "email": "john@example.com",
    "relationship": "Brother",
    "priority": 1
  }
]
```

---

## **Error Responses**

All errors follow this format:
```json
{
  "message": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-12-23T23:15:00Z"
}
```

### **Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

## **Rate Limiting**

- **ESP32 Devices:** No limit (trusted)
- **Web API:** 100 requests/minute per IP
- **Authentication:** 5 failed attempts = 15 min lockout

---

## **Webhooks (Optional)**

### **Alert Created Webhook**
```http
POST {your_webhook_url}
Content-Type: application/json

{
  "event": "alert.created",
  "alert_id": 123,
  "device_uid": "SHIELD-ESP32-001",
  "severity": "HIGH",
  "timestamp": "2025-12-23T23:15:00Z"
}
```

Register webhooks at: `/api/admin/webhooks`

---

## **Testing with cURL**

### **Example: Send Device Event**
```bash
curl -X POST http://localhost:5000/api/device/event \
  -F "device_uid=SHIELD-ESP32-001" \
  -F "heart_rate=115" \
  -F "temperature=37.8" \
  -F "spo2=97" \
  -F "lat=11.9416" \
  -F "lng=79.8083" \
  -F "manual_sos=0" \
  -F "audio=@test_audio.wav"
```

### **Example: Get Alerts (with JWT)**
```bash
curl -X GET http://localhost:5000/api/alerts \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

---

**Last Updated:** December 23, 2025  
**API Version:** 2.0
