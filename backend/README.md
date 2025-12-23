# Women Safety System - Flask Backend

REST API backend for the Women Safety System using Flask.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Device Management**: Register and manage ESP32 IoT devices
- **Alert System**: Real-time distress alert handling (AI-detected & manual)
- **Evidence Storage**: Photos, videos, and audio evidence management
- **Stress Detection**: Integration with AI engine for audio and physiological analysis
- **Guardian Management**: Emergency contacts and notification system
- **Database**: SQLite (development) with migration support

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-JWT-Extended
- **Security**: Flask-Bcrypt, CORS enabled
- **Migrations**: Flask-Migrate (Alembic)

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database (optional - defaults to SQLite)
# DATABASE_URL=sqlite:///women_safety.db

# CORS (optional)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Twilio (optional - for SMS alerts)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Email (optional - for email alerts)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AWS S3 (optional - for cloud storage)
USE_CLOUD_STORAGE=false
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name
```

### 3. Initialize Database

```bash
cd backend
python -c "from backend import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/change-password` - Change password

### User Management

- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update profile
- `GET /api/v1/users/guardians` - Get guardians list
- `POST /api/v1/users/guardians` - Add guardian
- `PUT /api/v1/users/guardians/<id>` - Update guardian
- `DELETE /api/v1/users/guardians/<id>` - Delete guardian
- `GET /api/v1/users/emergency-contacts` - Get emergency contacts
- `POST /api/v1/users/emergency-contacts` - Add emergency contact

### Device Management

- `GET /api/v1/devices/` - Get all user devices
- `GET /api/v1/devices/<id>` - Get device details
- `POST /api/v1/devices/register` - Register new device
- `PUT /api/v1/devices/<id>` - Update device config
- `DELETE /api/v1/devices/<id>` - Delete device
- `GET /api/v1/devices/<id>/status` - Get device status with sensor data

#### IoT Device Endpoints (require X-Device-Token header)

- `POST /api/v1/devices/heartbeat` - Send device heartbeat
- `POST /api/v1/devices/sensor-data` - Send sensor readings

### Alert Management

- `GET /api/v1/alerts/` - Get alerts (filter by status)
- `GET /api/v1/alerts/<id>` - Get alert details with evidence
- `GET /api/v1/alerts/active` - Get active alerts
- `POST /api/v1/alerts/<id>/acknowledge` - Acknowledge alert (police/guardian)
- `POST /api/v1/alerts/<id>/resolve` - Resolve alert
- `POST /api/v1/alerts/<id>/false-alarm` - Mark as false alarm

#### IoT Device Endpoints

- `POST /api/v1/alerts/trigger` - Trigger alert from device

### Evidence Management

- `GET /api/v1/evidence/alert/<alert_id>` - Get evidence for alert
- `GET /api/v1/evidence/<id>` - Get evidence details
- `GET /api/v1/evidence/<id>/download` - Download evidence file
- `DELETE /api/v1/evidence/<id>` - Delete evidence

#### IoT Device Endpoints

- `POST /api/v1/evidence/upload` - Upload evidence (photo/video/audio)

### Stress Detection

- `POST /api/v1/stress-detection/analyze-audio` - Analyze audio for stress (device)
- `POST /api/v1/stress-detection/analyze-physiological` - Analyze heart rate/temp (device)
- `GET /api/v1/stress-detection/model-status` - Check AI model status
- `POST /api/v1/stress-detection/test` - Test stress detection (development)

## Authentication

### JWT Token

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Device Token

IoT device endpoints require a device token in the X-Device-Token header:

```
X-Device-Token: <device_token>
```

## User Roles

- **user**: Device owner, can manage own devices and alerts
- **guardian**: Family member, can view alerts for associated users
- **police**: Law enforcement, can view and manage all alerts

## Database Schema

### Models

1. **User** - User accounts with authentication
2. **Guardian** - Emergency contacts/family members
3. **EmergencyContact** - Police, NGO, hospital contacts
4. **Device** - ESP32 IoT devices
5. **Alert** - Distress incidents
6. **Evidence** - Photos, videos, audio files
7. **SensorData** - Physiological sensor logs

## IoT Device Integration

### Device Registration Flow

1. User registers device via web/mobile app
2. System generates unique device token
3. User configures ESP32 with device token
4. Device sends heartbeat every 30 seconds
5. Device sends sensor data continuously

### Alert Trigger Flow

1. **AI Detection**: Device sends audio → Backend analyzes → Triggers alert if stress detected
2. **Manual Trigger**: User presses button → Device triggers alert immediately
3. Backend sends commands to device (activate camera, buzzer, GPS)
4. Device captures evidence and uploads
5. System notifies guardians and emergency contacts

## Development

### Database Migrations

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Testing

```bash
pytest tests/
```

### Run in Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## File Storage

- **Local Storage**: Files stored in `backend/uploads/evidence/`
- **Cloud Storage**: Optional AWS S3 integration (set `USE_CLOUD_STORAGE=true`)

## API Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Device token authentication
- CORS protection
- Input validation
- SQL injection protection (SQLAlchemy ORM)

## License

MIT License
