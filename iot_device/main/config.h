/**
 * Configuration file for ESP32 Women Safety Device
 */

#ifndef CONFIG_H
#define CONFIG_H

// ===== WiFi Configuration =====
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// ===== Backend API Configuration =====
#define API_BASE_URL "http://192.168.1.100:5000/api/v1"
#define DEVICE_TOKEN "YOUR_DEVICE_TOKEN_HERE"

// ===== Sensor Thresholds =====
#define HEART_RATE_THRESHOLD_LOW 50
#define HEART_RATE_THRESHOLD_HIGH 120
#define TEMPERATURE_THRESHOLD_LOW 35.0
#define TEMPERATURE_THRESHOLD_HIGH 38.5

// ===== AI Configuration =====
#define AI_STRESS_THRESHOLD 0.7  // Trigger alert if AI confidence >= 70%
#define ENABLE_CONTINUOUS_AUDIO_MONITORING false  // Set to true for always-on monitoring
#define AUDIO_CHECK_INTERVAL 60000  // Check audio every 60 seconds (if enabled)

// ===== Timing Configuration =====
#define HEARTBEAT_INTERVAL 30000  // 30 seconds
#define SENSOR_READ_INTERVAL 5000  // 5 seconds
#define GPS_UPDATE_INTERVAL 1000  // 1 second

// ===== Audio Configuration =====
#define AUDIO_SAMPLE_RATE 16000
#define AUDIO_SAMPLE_DURATION 3  // seconds for stress detection
#define AUDIO_RECORD_DURATION 10  // seconds for evidence recording
#define AUDIO_BUFFER_SIZE 48000  // 3 seconds at 16kHz

// ===== Camera Configuration =====
#define CAMERA_FRAME_SIZE FRAMESIZE_SVGA  // 800x600
#define CAMERA_JPEG_QUALITY 10  // 0-63, lower is higher quality

// ===== Pin Definitions =====
// I2C for sensors
#define I2C_SDA 21
#define I2C_SCL 22

// UART for GPS
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17

// I2S for microphone
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32

// Buttons and Indicators
#define EMERGENCY_BUTTON_PIN 15
#define BUZZER_PIN 2
#define LED_STATUS_PIN 4

// Battery monitoring
#define BATTERY_ADC_PIN 35

// ===== ESP32-CAM Pin Configuration =====
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ===== Debug Configuration =====
#define DEBUG_MODE true
#define DEBUG_SERIAL Serial

// Debug macros
#if DEBUG_MODE
  #define DEBUG_PRINT(x) DEBUG_SERIAL.print(x)
  #define DEBUG_PRINTLN(x) DEBUG_SERIAL.println(x)
  #define DEBUG_PRINTF(x, ...) DEBUG_SERIAL.printf(x, __VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(x, ...)
#endif

#endif // CONFIG_H