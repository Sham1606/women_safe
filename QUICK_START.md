# 🚀 Quick Start Guide - Shield System

## 5-Minute Setup

### Step 1: Install (2 minutes)
```bash
git clone https://github.com/Sham1606/women_safe.git
cd women_safe
python -m venv wsafe
source wsafe/bin/activate  # Windows: wsafe\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run (30 seconds)
```bash
python run.py
```

### Step 3: Access (30 seconds)
Open browser: **http://localhost:5000**

### Step 4: Login (1 minute)
```
Email: guardian@safe.com
Password: guardian123
```

### Step 5: Try It! (1 minute)
1. Click **+** to add device
2. Enter UID: `SHIELD-001`
3. Device appears on dashboard
4. Check map for location

---

## Test the System

### Send Test Event (using curl)
```bash
curl -X POST http://localhost:5000/api/device/event \
  -F "device_uid=SHIELD-001" \
  -F "heart_rate=75" \
  -F "temperature=36.5" \
  -F "lat=11.9416" \
  -F "lng=79.8083"
```

### Trigger Manual SOS
```bash
curl -X POST http://localhost:5000/api/device/event \
  -F "device_uid=SHIELD-001" \
  -F "heart_rate=75" \
  -F "temperature=36.5" \
  -F "manual_sos=1" \
  -F "lat=11.9416" \
  -F "lng=79.8083"
```
**Result:** Alert created instantly! 🚨

---

## Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Guardian | guardian@safe.com | guardian123 |
| Admin | admin@safety.com | admin123 |

---

## Run Tests
```bash
pip install -r requirements-test.txt
pytest
# Expected: 56 passed in ~80 seconds ✅
```

---

## Next Steps

📖 Read full walkthrough: [WALKTHROUGH.md](WALKTHROUGH.md)
🧪 See test details: [tests/README.md](tests/README.md)
🏃 Run tests: [RUN_TESTS.md](RUN_TESTS.md)

---

## Quick Reference

**Add Device:** Dashboard → + Button → Enter UID

**View Alerts:** Dashboard → Alert list (auto-updates)

**Check Map:** Dashboard → Left panel (live tracking)

**Update Alert Status (Police/Admin only):**
Alerts → Click alert → Update status dropdown

---

## Troubleshooting

**Can't login?**
- Check if server is running (`python run.py`)
- Clear browser cache
- Try default accounts above

**Device not showing?**
- Check device UID matches
- Refresh page
- Send test event to update

**Tests failing?**
```bash
pip install -r requirements-test.txt
pytest -v  # Verbose output
```

---

## System Requirements

- Python 3.10+
- 2GB RAM minimum
- Modern browser (Chrome, Firefox, Edge)
- Internet connection (for map tiles)

---

That's it! You're ready to use Shield System. 🛡️
