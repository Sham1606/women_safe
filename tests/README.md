# Women's Safety System - Test Suite

## Overview
Comprehensive test suite for the Women's Safety Device Platform covering AI stress detection, Flask backend, and integration testing.

## Test Structure

### 1. AI Stress Detection Tests (`test_ai_stress_detection.py`)
- ✅ Validates `predict_stress` function returns correct format
- ✅ Tests label values (normal/stressed/unknown)
- ✅ Verifies confidence scores are in valid range (0-1)
- ✅ Tests handling of normal and stressed audio
- ✅ Tests error handling for invalid/empty audio
- ✅ Tests consistency of predictions

### 2. Authentication Tests (`test_backend_auth.py`)
- ✅ User registration (success, duplicate email, missing fields)
- ✅ User login (success, invalid credentials, missing fields)
- ✅ JWT token structure and claims
- ✅ Protected endpoint access with valid/invalid tokens

### 3. Device Management Tests (`test_backend_device.py`)
- ✅ Device registration with JWT token
- ✅ Device registration with email
- ✅ Listing user's devices
- ✅ Device heartbeat/status updates
- ✅ Unknown device handling

### 4. Events & Alerts Tests (`test_backend_events_alerts.py`)
- ✅ Event processing with audio files
- ✅ Alert creation on high heart rate
- ✅ Alert creation on high temperature
- ✅ Manual SOS trigger
- ✅ Duplicate alert prevention
- ✅ Alert listing by role (guardian/police/admin)
- ✅ Alert detail retrieval
- ✅ Alert status updates (role-based access)

### 5. Admin Tests (`test_backend_admin.py`)
- ✅ Admin statistics access
- ✅ Role-based access control for statistics

### 6. Performance Tests (`test_performance.py`)
- ✅ Event processing time (< 2 seconds target)
- ✅ Burst handling (30+ heartbeats)
- ✅ API response time benchmarks
- ✅ Database consistency under load

### 7. Security Tests (`test_security.py`)
- ✅ Token-based authentication
- ✅ Invalid token rejection
- ✅ Role-based access control (RBAC)
- ✅ Password hashing verification
- ✅ SQL injection protection
- ✅ Evidence file access control

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Prepare Test Assets
Place test audio files in `tests/assets/`:
- 2-3 "normal" speech audio files (e.g., `normal_1.wav`, `normal_2.wav`)
- 2-3 "stressed" speech audio files (e.g., `stressed_1.wav`, `stressed_2.wav`)
- 1-2 camera images (optional, for future tests)

### 3. Run Tests

**Run all tests:**
```bash
pytest
```

**Run specific test file:**
```bash
pytest tests/test_ai_stress_detection.py
```

**Run with coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Run only fast tests (exclude slow):**
```bash
pytest -m "not slow"
```

**Verbose output:**
```bash
pytest -v
```

## Test Checklist

### ✅ AI Stress Detection
- [x] Returns correct JSON structure
- [x] Label validation (normal/stressed/unknown)
- [x] Confidence range (0-1)
- [x] Handles invalid audio gracefully
- [x] Consistent predictions

### ✅ Backend API - Auth
- [x] User registration
- [x] Login with JWT
- [x] Token validation
- [x] Protected endpoints

### ✅ Backend API - Device
- [x] Device registration
- [x] Heartbeat updates
- [x] Device listing

### ✅ Backend API - Events & Alerts
- [x] Event with audio processing
- [x] Alert creation (vitals threshold)
- [x] Alert creation (AI stress detection)
- [x] Manual SOS
- [x] Evidence storage
- [x] Alert retrieval
- [x] Status updates (role-based)

### ✅ Non-Functional
- [x] Performance (< 2s event processing)
- [x] Burst handling (30+ requests)
- [x] Security (token validation)
- [x] RBAC enforcement

## Expected Results

### AI Module
- All tests should pass if model file exists
- Graceful fallback if model unavailable

### Backend API
- 200/201 for successful operations
- 400 for bad requests
- 401 for unauthorized
- 403 for forbidden (role-based)
- 404 for not found

### Performance
- Event processing: < 2 seconds
- API responses: < 1 second
- 90%+ success rate under burst load

## Troubleshooting

### AI Tests Failing
- Ensure model file exists in `ai_engine/models/`
- Check audio processing dependencies (librosa, soundfile)
- Tests will skip if AI module unavailable

### Database Tests Failing
- Tests use temporary SQLite database
- Cleaned up automatically after each test
- Check write permissions in temp directory

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements-test.txt`
- Check PYTHONPATH includes project root

## CI/CD Integration

Add to GitHub Actions (`.github/workflows/test.yml`):
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Contributing
When adding new features:
1. Write tests first (TDD)
2. Ensure all existing tests pass
3. Aim for 80%+ code coverage
4. Update this README with new test categories
