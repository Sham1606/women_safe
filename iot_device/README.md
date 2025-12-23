# Women Safety System - ESP32 IoT Device

Firmware for ESP32-CAM based wearable safety device with multiple sensors and AI-powered stress detection.

## Hardware Components

### Required Components

1. **ESP32-CAM** - Main microcontroller with built-in camera
2. **MAX30102** - Heart rate and SpO2 sensor (I2C)
3. **MLX90614** or **DS18B20** - Temperature sensor (I2C/1-Wire)
4. **NEO-6M GPS Module** - GPS location tracking (UART)
5. **I2S MEMS Microphone** (INMP441 or SPH0645) - Audio capture
6. **Emergency Button** - Manual alert trigger
7. **Buzzer** - Audio alert indicator
8. **LED** - Status indicator
9. **3.7V Li-Po Battery** with charging module
10. **Voltage Regulator** (if needed)

### Pin Connections

#### ESP32-CAM Pins
```
ESP32-CAM GPIO    | Component          | Notes
------------------|--------------------|------------------
GPIO 21           | I2C SDA            | Heart rate, temp sensors
GPIO 22           | I2C SCL            | Heart rate, temp sensors
GPIO 16           | GPS RX             | Connect to GPS TX
GPIO 17           | GPS TX             | Connect to GPS RX
GPIO 25           | I2S WS (LRCLK)     | Microphone
GPIO 32           | I2S SCK (BCLK)     | Microphone
GPIO 33           | I2S SD (DOUT)      | Microphone
GPIO 15           | Emergency Button   | Pull-up, active LOW
GPIO 2            | Buzzer             | Active HIGH
GPIO 4            | Status LED         | Active HIGH
GPIO 35           | Battery ADC        | Voltage divider
Built-in          | Camera             | OV2640
```

#### Power Connections
```
5V    - ESP32-CAM VCC, GPS VCC
3.3V  - Sensors VCC (MAX30102, MLX90614, Microphone)
GND   - Common ground for all components
```

## Software Setup

### Prerequisites

1. **Arduino IDE** (1.8.19 or later) or **PlatformIO**
2. **ESP32 Board Support** installed
3. **Required Libraries** (see below)

### Arduino IDE Setup

#### 1. Install ESP32 Board Support

1. Open Arduino IDE
2. Go to **File > Preferences**
3. Add to **Additional Board Manager URLs**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools > Board > Boards Manager**
5. Search for "esp32" and install **ESP32 by Espressif Systems**

#### 2. Install Required Libraries

Go to **Sketch > Include Library > Manage Libraries** and install:

```
1. SparkFun MAX3010x Pulse and Proximity Sensor Library (v1.1.2+)
2. Adafruit MLX90614 Library (v2.1.3+)
3. TinyGPSPlus (v1.0.3+)
4. ArduinoJson (v6.21.0+)
5. ESP32-Camera (included with ESP32 board support)
6. Base64 by Densaugeo (v1.4.0+)
```

**Library List:**
- `SparkFun MAX3010x` - Heart rate sensor
- `Adafruit MLX90614` - Temperature sensor
- `TinyGPSPlus` - GPS parsing
- `ArduinoJson` - JSON handling
- `base64` - File encoding for upload

#### 3. Configure Board Settings

**Tools > Board**: "AI Thinker ESP32-CAM"
**Tools > Upload Speed**: 115200
**Tools > Flash Frequency**: 80MHz
**Tools > Partition Scheme**: "Huge APP (3MB No OTA)"

### Configuration

#### 1. Edit `config.h`

```cpp
// WiFi credentials
#define WIFI_SSID "YourWiFiSSID"
#define WIFI_PASSWORD "YourWiFiPassword"

// Backend API
#define API_BASE_URL "http://192.168.1.100:5000/api/v1"
#define DEVICE_TOKEN "your-device-token-from-backend"

// Thresholds
#define HEART_RATE_THRESHOLD_HIGH 120
#define TEMPERATURE_THRESHOLD_HIGH 38.5
#define AI_STRESS_THRESHOLD 0.7
```

#### 2. Get Device Token

1. Register device through web/mobile app
2. Copy the device token
3. Paste it in `config.h`

### Upload Firmware

#### ESP32-CAM Upload Process

1. Connect **GPIO0 to GND** (boot mode)
2. Connect **ESP32-CAM to USB-to-Serial adapter**:
   - ESP32 5V → Adapter 5V
   - ESP32 GND → Adapter GND
   - ESP32 U0R → Adapter TX
   - ESP32 U0T → Adapter RX
3. Press **Reset button** on ESP32-CAM
4. Click **Upload** in Arduino IDE
5. After upload, **disconnect GPIO0 from GND**
6. Press **Reset button** again

## Features

### 1. Continuous Monitoring
- Heart rate monitoring (every 5 seconds)
- Body temperature monitoring
- GPS location tracking
- Battery level monitoring
- Automatic data sync with backend

### 2. Dual-Mode Alert System

**Manual Trigger:**
- Press emergency button
- Immediately activates buzzer
- Captures photo/video/audio evidence
- Sends alert to backend
- Notifies guardians and emergency contacts

**AI-Detected Trigger:**
- Continuously monitors physiological signals
- Captures audio when stress thresholds exceeded
- Backend AI analyzes audio + physiological data
- Automatically triggers alert if stress detected
- Captures evidence and notifies contacts

### 3. Evidence Collection
- **Photos**: 3 images captured automatically
- **Audio**: 10-second recording
- **GPS**: Current location
- **Physiological**: Heart rate, temperature at time of alert
- All evidence uploaded to backend immediately

### 4. Real-Time Communication
- Heartbeat every 30 seconds
- Sensor data every 5 seconds
- WiFi auto-reconnection
- Status LED indicator

## System Flow

### Normal Operation
```
1. Power on → Connect to WiFi
2. Initialize sensors (Heart rate, Temperature, GPS, Camera, Audio)
3. Continuous loop:
   - Read sensors every 5 seconds
   - Send data to backend
   - Check for stress thresholds
   - Send heartbeat every 30 seconds
   - Update GPS location
```

### Manual Alert Flow
```
1. User presses emergency button
2. Buzzer activates
3. LED flashes
4. Send alert to backend (type: manual_trigger)
5. Capture 3 photos
6. Record 10-second audio
7. Upload all evidence
8. Backend notifies guardians/police
9. Keep buzzer on for 5 seconds
```

### AI Detection Flow
```
1. Physiological sensors detect abnormal values
   (Heart rate > 120 bpm OR Temperature > 38.5°C)
2. Capture 3-second audio sample
3. Send audio + physiological data to backend
4. Backend AI analyzes stress level
5. If stress score ≥ 0.7:
   - Trigger alert (type: ai_detected)
   - Activate buzzer
   - Capture evidence
   - Upload to backend
   - Notify contacts
```

## Serial Monitor Output

```
=== Women Safety System - ESP32 Device ===
Version: 1.0.0
==========================================

Connecting to WiFi...
.........
WiFi connected!
IP Address: 192.168.1.150

Initializing sensors...
✓ Heart rate sensor initialized
✓ Temperature sensor initialized

Initializing camera...
✓ Camera initialized

Initializing GPS...
GPS module initialized
Waiting for GPS fix...
✓ GPS data detected

Initializing audio system...
✓ Audio system initialized

=== Device Ready ===
Waiting for sensor data...

--- Sensor Readings ---
Heart Rate: 75.0 bpm
Temperature: 36.5 °C
GPS: 12.345678, 77.654321
Battery: 95%
---------------------

✓ Sensor data sent
✓ Heartbeat sent successfully
```

## Troubleshooting

### WiFi Not Connecting
- Check SSID and password in `config.h`
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Check WiFi signal strength

### Camera Not Working
- Verify camera cable connection
- Check if camera is properly seated
- Try different partition scheme in Arduino IDE

### Sensors Not Detected
- Check I2C connections (SDA, SCL)
- Verify sensor power supply (3.3V)
- Run I2C scanner to detect addresses

### GPS Not Getting Fix
- Ensure GPS antenna has clear sky view
- Wait 1-2 minutes for initial fix (cold start)
- Check GPS module power and connections

### Upload Failed
- Ensure GPIO0 is connected to GND during upload
- Check USB-to-Serial adapter connections
- Try lower upload speed (57600)
- Press reset button before upload

## Power Consumption

**Typical Power Usage:**
- Idle (WiFi connected): ~150mA
- Sensor reading: ~200mA
- Camera capture: ~300mA
- Alert mode (buzzer + camera): ~400mA

**Battery Life** (3000mAh Li-Po):
- Normal operation: ~15-20 hours
- With frequent alerts: ~8-10 hours

## Safety Features

1. **Automatic alert** on stress detection
2. **Manual trigger** with emergency button
3. **Evidence collection** (photo/audio/GPS)
4. **Multi-channel notification** (SMS/Email/Push)
5. **Real-time tracking** via GPS
6. **Buzzer alarm** for deterrence
7. **Battery monitoring** with low battery alert
8. **Auto-reconnect** WiFi for reliability

## Development

### Testing Individual Components

```cpp
// Test heart rate sensor
float hr = readHeartRate();
Serial.println(hr);

// Test camera
camera_fb_t* fb = capturePhoto();
if (fb) esp_camera_fb_return(fb);

// Test GPS
if (isGPSAvailable()) {
  Serial.printf("%.6f, %.6f\n", getLatitude(), getLongitude());
}

// Test audio
uint8_t* audio = NULL;
size_t size = 0;
captureAudioSample(&audio, &size);
if (audio) free(audio);
```

### Debug Mode

Enable debug output in `config.h`:
```cpp
#define DEBUG_MODE true
```

## Circuit Diagram

See `circuit_diagram.png` for complete wiring schematic.

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [repository-url]
- Email: support@womensafety.com
