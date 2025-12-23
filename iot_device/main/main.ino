/**
 * Women Safety System - ESP32 IoT Device Firmware
 * 
 * Features:
 * - Heart rate sensor (MAX30102)
 * - Temperature sensor (MLX90614 or DS18B20)
 * - GPS module (NEO-6M)
 * - Microphone for audio capture
 * - ESP32-CAM for photo/video
 * - Emergency button
 * - Buzzer for alerts
 * - WiFi communication with backend
 * 
 * Author: Women Safety System Team
 * Version: 1.0.0
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors.h"
#include "communication.h"
#include "camera.h"
#include "audio.h"
#include "gps.h"

// Pin Definitions
#define EMERGENCY_BUTTON_PIN 15
#define BUZZER_PIN 2
#define LED_STATUS_PIN 4

// Global State
bool isConnected = false;
bool alertActive = false;
unsigned long lastHeartbeat = 0;
unsigned long lastSensorRead = 0;
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds
const unsigned long SENSOR_READ_INTERVAL = 5000; // 5 seconds

// Sensor data
float currentHeartRate = 0;
float currentTemperature = 0;
float currentLatitude = 0;
float currentLongitude = 0;
int batteryLevel = 100;

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=== Women Safety System - ESP32 Device ===");
  Serial.println("Version: 1.0.0");
  Serial.println("==========================================\n");
  
  // Initialize pins
  pinMode(EMERGENCY_BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_STATUS_PIN, OUTPUT);
  
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_STATUS_PIN, LOW);
  
  // Initialize WiFi
  Serial.println("Connecting to WiFi...");
  connectWiFi();
  
  // Initialize sensors
  Serial.println("\nInitializing sensors...");
  initSensors();
  
  // Initialize camera
  Serial.println("Initializing camera...");
  initCamera();
  
  // Initialize GPS
  Serial.println("Initializing GPS...");
  initGPS();
  
  // Initialize audio
  Serial.println("Initializing audio system...");
  initAudio();
  
  Serial.println("\n=== Device Ready ===");
  Serial.println("Waiting for sensor data...\n");
  
  // Startup beep
  beep(2, 100);
  blinkLED(3, 200);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectWiFi();
  }
  
  // Check emergency button
  if (digitalRead(EMERGENCY_BUTTON_PIN) == LOW) {
    Serial.println("\n!!! EMERGENCY BUTTON PRESSED !!!");
    handleEmergencyButton();
    delay(1000); // Debounce
  }
  
  // Read sensors periodically
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    lastSensorRead = currentMillis;
    readAllSensors();
    
    // Check for stress based on physiological data
    if (checkStressThresholds()) {
      Serial.println("\n!!! STRESS DETECTED FROM SENSORS !!!");
      // Capture audio for AI analysis
      analyzeStressWithAudio();
    }
    
    // Send sensor data to backend
    sendSensorData();
  }
  
  // Send heartbeat periodically
  if (currentMillis - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = currentMillis;
    sendHeartbeat();
  }
  
  // Update GPS
  updateGPS();
  
  // Check for continuous audio monitoring (if enabled)
  if (ENABLE_CONTINUOUS_AUDIO_MONITORING && !alertActive) {
    checkAudioForStress();
  }
  
  delay(100);
}

// ===== WiFi Functions =====

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    isConnected = true;
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_STATUS_PIN, HIGH);
  } else {
    isConnected = false;
    Serial.println("\nWiFi connection failed!");
    digitalWrite(LED_STATUS_PIN, LOW);
  }
}

// ===== Sensor Functions =====

void readAllSensors() {
  // Read heart rate
  currentHeartRate = readHeartRate();
  
  // Read temperature
  currentTemperature = readTemperature();
  
  // Read GPS
  if (isGPSAvailable()) {
    currentLatitude = getLatitude();
    currentLongitude = getLongitude();
  }
  
  // Read battery level (analog read from voltage divider)
  batteryLevel = readBatteryLevel();
  
  // Print sensor data
  Serial.println("\n--- Sensor Readings ---");
  Serial.printf("Heart Rate: %.1f bpm\n", currentHeartRate);
  Serial.printf("Temperature: %.1f °C\n", currentTemperature);
  Serial.printf("GPS: %.6f, %.6f\n", currentLatitude, currentLongitude);
  Serial.printf("Battery: %d%%\n", batteryLevel);
  Serial.println("---------------------\n");
}

bool checkStressThresholds() {
  // Check if heart rate or temperature exceed thresholds
  bool stressDetected = false;
  
  if (currentHeartRate > HEART_RATE_THRESHOLD_HIGH) {
    Serial.printf("High heart rate detected: %.1f bpm\n", currentHeartRate);
    stressDetected = true;
  }
  
  if (currentTemperature > TEMPERATURE_THRESHOLD_HIGH) {
    Serial.printf("High temperature detected: %.1f °C\n", currentTemperature);
    stressDetected = true;
  }
  
  return stressDetected;
}

// ===== Emergency Functions =====

void handleEmergencyButton() {
  alertActive = true;
  
  // Activate buzzer
  digitalWrite(BUZZER_PIN, HIGH);
  digitalWrite(LED_STATUS_PIN, HIGH);
  
  // Trigger alert on backend
  int alertId = triggerAlert("manual_trigger", "button");
  
  if (alertId > 0) {
    Serial.printf("Alert triggered successfully. Alert ID: %d\n", alertId);
    
    // Capture and upload evidence
    captureAndUploadEvidence(alertId);
  } else {
    Serial.println("Failed to trigger alert!");
  }
  
  // Keep buzzer on for 5 seconds
  delay(5000);
  digitalWrite(BUZZER_PIN, LOW);
}

void analyzeStressWithAudio() {
  Serial.println("Capturing audio for stress analysis...");
  
  // Capture audio sample
  uint8_t* audioData = NULL;
  size_t audioSize = 0;
  
  if (captureAudioSample(&audioData, &audioSize)) {
    Serial.printf("Audio captured: %d bytes\n", audioSize);
    
    // Send to backend for AI analysis
    DynamicJsonDocument result = analyzeAudioStress(audioData, audioSize, currentHeartRate, currentTemperature);
    
    // Check if stress detected
    if (result["stress_detected"].as<bool>()) {
      float stressScore = result["combined_score"].as<float>();
      Serial.printf("\n!!! AI STRESS DETECTED - Score: %.2f !!!\n", stressScore);
      
      // Trigger alert if score exceeds threshold
      if (stressScore >= AI_STRESS_THRESHOLD) {
        Serial.println("Triggering AI-detected alert...");
        
        int alertId = triggerAlert("ai_detected", "hybrid", stressScore, result);
        
        if (alertId > 0) {
          alertActive = true;
          digitalWrite(BUZZER_PIN, HIGH);
          digitalWrite(LED_STATUS_PIN, HIGH);
          
          // Capture evidence
          captureAndUploadEvidence(alertId);
          
          delay(5000);
          digitalWrite(BUZZER_PIN, LOW);
        }
      }
    } else {
      Serial.println("No stress detected from AI analysis.");
    }
    
    // Free audio buffer
    if (audioData) free(audioData);
  }
}

void captureAndUploadEvidence(int alertId) {
  Serial.println("\nCapturing evidence...");
  
  // Capture photos
  for (int i = 0; i < 3; i++) {
    Serial.printf("Capturing photo %d/3...\n", i + 1);
    if (captureAndUploadPhoto(alertId)) {
      Serial.println("Photo uploaded successfully");
    }
    delay(500);
  }
  
  // Capture audio recording
  Serial.println("Capturing audio recording...");
  if (captureAndUploadAudio(alertId, 10)) { // 10 seconds
    Serial.println("Audio uploaded successfully");
  }
  
  Serial.println("Evidence capture complete.\n");
}

void checkAudioForStress() {
  // Periodically sample audio and check for stress
  static unsigned long lastAudioCheck = 0;
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastAudioCheck >= AUDIO_CHECK_INTERVAL) {
    lastAudioCheck = currentMillis;
    
    // Quick audio sample for monitoring
    analyzeStressWithAudio();
  }
}

// ===== Utility Functions =====

void beep(int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
    delay(duration);
  }
}

void blinkLED(int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_STATUS_PIN, HIGH);
    delay(duration);
    digitalWrite(LED_STATUS_PIN, LOW);
    delay(duration);
  }
  digitalWrite(LED_STATUS_PIN, HIGH); // Keep on when connected
}

int readBatteryLevel() {
  // Read battery voltage from analog pin
  // Assumes voltage divider on pin 35
  int adcValue = analogRead(35);
  float voltage = (adcValue / 4095.0) * 3.3 * 2.0; // Voltage divider factor
  
  // Map voltage to percentage (3.0V = 0%, 4.2V = 100%)
  int percentage = map(voltage * 100, 300, 420, 0, 100);
  percentage = constrain(percentage, 0, 100);
  
  return percentage;
}