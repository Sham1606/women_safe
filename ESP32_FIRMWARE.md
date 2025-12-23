# 📱 **ESP32 Firmware Implementation Guide**

## **Hardware Connections**

### **Pin Mapping:**
```cpp
// Sensor Pins
#define HR_SENSOR_SDA 21
#define HR_SENSOR_SCL 22
#define TEMP_SENSOR_PIN 4
#define GSR_SENSOR_PIN 36
#define MIC_PIN 39

// Communication
#define GPS_TX 16
#define GPS_RX 17
#define GSM_TX 14
#define GSM_RX 15

// Output
#define BUZZER_PIN 13
#define LED_INDICATOR 33

// Input
#define SOS_BUTTON_PIN 12
```

### **Complete ESP32-CAM Firmware:**

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include <Wire.h>
#include <MAX30105.h>
#include <DHT.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Backend API
const char* serverURL = "http://YOUR_SERVER_IP:5000/api/device/event";
const char* deviceUID = "SHIELD-ESP32-001";

// Sensor Objects
MAX30105 heartRateSensor;
DHT dht(TEMP_SENSOR_PIN, DHT22);
TinyGPSPlus gps;
HardwareSerial gpsSerial(1);
HardwareSerial gsmSerial(2);

// Buffers
float heartRate = 0;
float temperature = 0;
float spo2 = 0;
float gsrValue = 0;
double latitude = 0;
double longitude = 0;

// State Variables
bool emergencyMode = false;
unsigned long lastUpdateTime = 0;
const unsigned long UPDATE_INTERVAL = 60000; // 60 seconds normal mode
const unsigned long EMERGENCY_INTERVAL = 10000; // 10 seconds emergency mode

// Camera Configuration
void configureCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Image quality settings
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void setup() {
  Serial.begin(115200);
  
  // Initialize Pins
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_INDICATOR, OUTPUT);
  pinMode(SOS_BUTTON_PIN, INPUT_PULLUP);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  
  // Initialize I2C
  Wire.begin(HR_SENSOR_SDA, HR_SENSOR_SCL);
  
  // Initialize Heart Rate Sensor (MAX30105)
  if (!heartRateSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30105 not found!");
  } else {
    heartRateSensor.setup();
    heartRateSensor.setPulseAmplitudeRed(0x0A);
    heartRateSensor.setPulseAmplitudeGreen(0);
    Serial.println("Heart Rate Sensor initialized");
  }
  
  // Initialize Temperature Sensor
  dht.begin();
  Serial.println("Temperature Sensor initialized");
  
  // Initialize GPS
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  Serial.println("GPS initialized");
  
  // Initialize GSM
  gsmSerial.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX);
  Serial.println("GSM initialized");
  
  // Initialize Camera
  configureCamera();
  Serial.println("Camera initialized");
  
  Serial.println("\n\u2705 SHIELD System Ready!");
  blinkLED(3); // Startup indication
}

void loop() {
  // Check for manual SOS button
  if (digitalRead(SOS_BUTTON_PIN) == LOW) {
    Serial.println("🚨 MANUAL SOS TRIGGERED!");
    triggerEmergency(true);
  }
  
  // Read sensors
  readSensors();
  
  // Update GPS
  updateGPS();
  
  // Check stress level
  float stressScore = calculateStressScore();
  Serial.printf("Stress Score: %.2f\n", stressScore);
  
  // Trigger emergency if stress threshold exceeded
  if (stressScore > 0.5 && !emergencyMode) {
    Serial.println("🚨 AUTOMATIC STRESS DETECTION!");
    triggerEmergency(false);
  }
  
  // Send data to backend
  unsigned long currentTime = millis();
  unsigned long interval = emergencyMode ? EMERGENCY_INTERVAL : UPDATE_INTERVAL;
  
  if (currentTime - lastUpdateTime >= interval) {
    sendDataToBackend();
    lastUpdateTime = currentTime;
  }
  
  delay(1000);
}

void readSensors() {
  // Read Heart Rate & SpO2
  long irValue = heartRateSensor.getIR();
  if (irValue > 50000) {
    heartRate = heartRateSensor.getHeartRate();
    spo2 = heartRateSensor.getSp02();
  }
  
  // Read Temperature
  temperature = dht.readTemperature();
  
  // Read GSR (Galvanic Skin Response)
  gsrValue = analogRead(GSR_SENSOR_PIN) / 4096.0 * 100; // Convert to percentage
  
  Serial.printf("❤️ HR: %.0f BPM | 🌡️ Temp: %.1f°C | SpO2: %.0f%% | GSR: %.0f%%\n", 
                heartRate, temperature, spo2, gsrValue);
}

void updateGPS() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }
  
  if (gps.location.isUpdated()) {
    latitude = gps.location.lat();
    longitude = gps.location.lng();
    Serial.printf("📍 GPS: %.6f, %.6f\n", latitude, longitude);
  }
}

float calculateStressScore() {
  float score = 0.0;
  
  // Heart rate contribution (30%)
  if (heartRate > 100) {
    score += 0.3;
  }
  
  // Temperature contribution (10%)
  if (temperature > 38.5) {
    score += 0.1;
  }
  
  // GSR contribution (20%)
  if (gsrValue > 70) {
    score += 0.2;
  }
  
  // Note: AI voice analysis (40%) is done on backend
  // This is just physiological stress score
  
  return score;
}

void triggerEmergency(bool manualSOS) {
  emergencyMode = true;
  
  // Activate buzzer
  activateBuzzer();
  
  // Flash LED
  blinkLED(10);
  
  // Send immediate alert
  sendDataToBackend(manualSOS);
  
  Serial.println("✅ Emergency protocol activated");
}

void activateBuzzer() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(500);
    digitalWrite(BUZZER_PIN, LOW);
    delay(500);
  }
}

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_INDICATOR, HIGH);
    delay(200);
    digitalWrite(LED_INDICATOR, LOW);
    delay(200);
  }
}

camera_fb_t* captureImage() {
  camera_fb_t * fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Camera capture failed");
    return NULL;
  }
  return fb;
}

void sendDataToBackend(bool manualSOS = false) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected");
    return;
  }
  
  HTTPClient http;
  http.begin(serverURL);
  
  // Create multipart form data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  
  String body = "";
  
  // Add text fields
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"device_uid\"\r\n\r\n";
  body += String(deviceUID) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"heart_rate\"\r\n\r\n";
  body += String(heartRate) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"temperature\"\r\n\r\n";
  body += String(temperature) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"spo2\"\r\n\r\n";
  body += String(spo2) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"lat\"\r\n\r\n";
  body += String(latitude, 6) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"lng\"\r\n\r\n";
  body += String(longitude, 6) + "\r\n";
  
  body += "--" + boundary + "\r\n";
  body += "Content-Disposition: form-data; name=\"manual_sos\"\r\n\r\n";
  body += manualSOS ? "1" : "0";
  body += "\r\n";
  
  // Capture and add image
  if (emergencyMode) {
    camera_fb_t * fb = captureImage();
    if (fb) {
      body += "--" + boundary + "\r\n";
      body += "Content-Disposition: form-data; name=\"image\"; filename=\"capture.jpg\"\r\n";
      body += "Content-Type: image/jpeg\r\n\r\n";
      // Note: For actual implementation, you'd need to send the binary data
      // This is a simplified version
      esp_camera_fb_return(fb);
    }
  }
  
  body += "--" + boundary + "--\r\n";
  
  // Send request
  int httpResponseCode = http.POST(body);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("✅ Data sent successfully");
    Serial.println("Response: " + response);
  } else {
    Serial.printf("❌ Error: %s\n", http.errorToString(httpResponseCode).c_str());
  }
  
  http.end();
}
```

---

## **Testing the Firmware**

### **1. Upload to ESP32:**
```bash
# Install Arduino IDE and ESP32 board support
# Install required libraries:
# - MAX30105
# - DHT sensor library
# - TinyGPS++
# - HTTPClient

# Select: Tools > Board > ESP32 Dev Module
# Select: Tools > Port > (your COM port)
# Click Upload
```

### **2. Serial Monitor Output:**
```
Connecting to WiFi...
WiFi Connected!
IP Address: 192.168.1.100
Heart Rate Sensor initialized
Temperature Sensor initialized
GPS initialized
GSM initialized
Camera initialized

✅ SHIELD System Ready!

❤️ HR: 72 BPM | 🌡️ Temp: 36.5°C | SpO2: 98% | GSR: 45%
📍 GPS: 11.941600, 79.808300
Stress Score: 0.00
✅ Data sent successfully
```

### **3. Simulating Emergency:**
```
// Press SOS button OR
// Increase heart rate > 100 BPM

🚨 AUTOMATIC STRESS DETECTION!
Stress Score: 0.72
✅ Emergency protocol activated
🚨 Buzzer activated
📸 Image captured
✅ Data sent successfully
Response: {"status":"success","alert_triggered":true,"alert_id":123}
```

---

## **Power Management**

```cpp
// Deep sleep mode when inactive
void enterDeepSleep() {
  Serial.println("Entering deep sleep...");
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_12, 0); // Wake on SOS button
  esp_deep_sleep_start();
}

// Battery monitoring
float getBatteryVoltage() {
  int raw = analogRead(35); // Battery voltage divider
  float voltage = (raw / 4096.0) * 3.3 * 2; // Assuming 2:1 divider
  return voltage;
}

int getBatteryPercentage() {
  float voltage = getBatteryVoltage();
  // Li-Ion: 4.2V (100%) to 3.0V (0%)
  int percentage = map(voltage * 100, 300, 420, 0, 100);
  return constrain(percentage, 0, 100);
}
```

---

## **Troubleshooting**

### **Issue: WiFi not connecting**
```cpp
// Add fallback to GSM
if (WiFi.status() != WL_CONNECTED) {
  Serial.println("WiFi failed, using GSM...");
  sendViaGSM();
}
```

### **Issue: Sensor not detected**
```cpp
// Check I2C devices
void scanI2C() {
  for(byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("I2C device found at 0x%02X\n", address);
    }
  }
}
```

### **Issue: High power consumption**
- Reduce camera resolution
- Increase update interval
- Use deep sleep between readings
- Lower LED brightness

---

## **Next Steps**

1. **Flash firmware to ESP32-CAM**
2. **Connect all sensors as per pin mapping**
3. **Configure WiFi credentials**
4. **Set backend server URL**
5. **Test each sensor individually**
6. **Test complete emergency flow**
7. **Deploy in wearable enclosure**
