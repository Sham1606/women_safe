/**
 * Communication module for backend API interaction
 */

#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <base64.h>
#include "config.h"

extern float currentHeartRate;
extern float currentTemperature;
extern float currentLatitude;
extern float currentLongitude;
extern int batteryLevel;

/**
 * Send heartbeat to backend
 */
void sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) {
    DEBUG_PRINTLN("WiFi not connected. Skipping heartbeat.");
    return;
  }
  
  HTTPClient http;
  String url = String(API_BASE_URL) + "/devices/heartbeat";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  
  // Create JSON payload
  DynamicJsonDocument doc(256);
  doc["battery_level"] = batteryLevel;
  
  if (currentLatitude != 0 && currentLongitude != 0) {
    doc["latitude"] = currentLatitude;
    doc["longitude"] = currentLongitude;
  }
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200) {
    DEBUG_PRINTLN("✓ Heartbeat sent successfully");
  } else {
    DEBUG_PRINTF("✗ Heartbeat failed: %d\n", httpCode);
  }
  
  http.end();
}

/**
 * Send sensor data to backend
 */
void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  // Skip if no valid sensor data
  if (currentHeartRate == 0 && currentTemperature == 0) {
    return;
  }
  
  HTTPClient http;
  String url = String(API_BASE_URL) + "/devices/sensor-data";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  
  // Create JSON payload
  DynamicJsonDocument doc(512);
  
  if (currentHeartRate > 0) {
    doc["heart_rate"] = (int)currentHeartRate;
  }
  
  if (currentTemperature > 0) {
    doc["temperature"] = currentTemperature;
  }
  
  if (currentLatitude != 0 && currentLongitude != 0) {
    doc["latitude"] = currentLatitude;
    doc["longitude"] = currentLongitude;
  }
  
  doc["battery_level"] = batteryLevel;
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 201) {
    DEBUG_PRINTLN("✓ Sensor data sent");
  } else {
    DEBUG_PRINTF("✗ Sensor data failed: %d\n", httpCode);
  }
  
  http.end();
}

/**
 * Trigger alert on backend
 * Returns: Alert ID or -1 on failure
 */
int triggerAlert(const char* alertType, const char* triggerSource, float stressScore = 0, DynamicJsonDocument aiAnalysis = DynamicJsonDocument(0)) {
  if (WiFi.status() != WL_CONNECTED) {
    DEBUG_PRINTLN("WiFi not connected. Cannot trigger alert.");
    return -1;
  }
  
  HTTPClient http;
  String url = String(API_BASE_URL) + "/alerts/trigger";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  
  // Create JSON payload
  DynamicJsonDocument doc(2048);
  doc["alert_type"] = alertType;
  doc["trigger_source"] = triggerSource;
  doc["priority"] = "high";
  
  if (stressScore > 0) {
    doc["stress_score"] = stressScore;
    doc["confidence"] = stressScore;
  }
  
  if (currentHeartRate > 0) {
    doc["heart_rate"] = (int)currentHeartRate;
  }
  
  if (currentTemperature > 0) {
    doc["temperature"] = currentTemperature;
  }
  
  if (currentLatitude != 0 && currentLongitude != 0) {
    doc["latitude"] = currentLatitude;
    doc["longitude"] = currentLongitude;
  }
  
  // Add AI analysis if provided
  if (!aiAnalysis.isNull() && aiAnalysis.size() > 0) {
    doc["ai_analysis"] = aiAnalysis;
  }
  
  String payload;
  serializeJson(doc, payload);
  
  DEBUG_PRINTLN("Sending alert to backend...");
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 201) {
    String response = http.getString();
    DEBUG_PRINTLN("✓ Alert triggered successfully");
    DEBUG_PRINTLN(response);
    
    // Parse response to get alert ID
    DynamicJsonDocument responseDoc(1024);
    deserializeJson(responseDoc, response);
    int alertId = responseDoc["alert_id"];
    
    http.end();
    return alertId;
  } else {
    DEBUG_PRINTF("✗ Alert trigger failed: %d\n", httpCode);
    if (httpCode > 0) {
      DEBUG_PRINTLN(http.getString());
    }
    http.end();
    return -1;
  }
}

/**
 * Analyze audio for stress using backend AI
 */
DynamicJsonDocument analyzeAudioStress(uint8_t* audioData, size_t audioSize, float heartRate, float temperature) {
  DynamicJsonDocument result(2048);
  result["stress_detected"] = false;
  result["combined_score"] = 0.0;
  
  if (WiFi.status() != WL_CONNECTED || audioData == NULL || audioSize == 0) {
    return result;
  }
  
  HTTPClient http;
  String url = String(API_BASE_URL) + "/stress-detection/analyze-audio";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  http.setTimeout(30000); // 30 second timeout for AI processing
  
  // Encode audio to base64
  String audioBase64 = base64::encode(audioData, audioSize);
  
  // Create JSON payload
  DynamicJsonDocument doc(audioBase64.length() + 512);
  doc["audio_base64"] = audioBase64;
  
  if (heartRate > 0) {
    doc["heart_rate"] = (int)heartRate;
  }
  
  if (temperature > 0) {
    doc["temperature"] = temperature;
  }
  
  String payload;
  serializeJson(doc, payload);
  
  DEBUG_PRINTLN("Sending audio to backend for AI analysis...");
  DEBUG_PRINTF("Audio size: %d bytes, Base64 size: %d bytes\n", audioSize, audioBase64.length());
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200) {
    String response = http.getString();
    DEBUG_PRINTLN("✓ Audio analysis complete");
    
    // Parse response
    deserializeJson(result, response);
    
    if (result["success"].as<bool>()) {
      DEBUG_PRINTF("Stress detected: %s\n", result["stress_detected"].as<bool>() ? "YES" : "NO");
      DEBUG_PRINTF("Combined score: %.2f\n", result["combined_score"].as<float>());
    }
  } else {
    DEBUG_PRINTF("✗ Audio analysis failed: %d\n", httpCode);
    if (httpCode > 0) {
      DEBUG_PRINTLN(http.getString());
    }
  }
  
  http.end();
  return result;
}

/**
 * Upload evidence (photo/video/audio) to backend
 */
bool uploadEvidence(int alertId, const char* evidenceType, uint8_t* fileData, size_t fileSize, const char* fileName) {
  if (WiFi.status() != WL_CONNECTED || fileData == NULL || fileSize == 0) {
    return false;
  }
  
  HTTPClient http;
  String url = String(API_BASE_URL) + "/evidence/upload";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  http.setTimeout(60000); // 60 second timeout for large files
  
  // Encode file to base64
  String fileBase64 = base64::encode(fileData, fileSize);
  
  // Create JSON payload
  DynamicJsonDocument doc(fileBase64.length() + 1024);
  doc["alert_id"] = alertId;
  doc["evidence_type"] = evidenceType;
  doc["file_name"] = fileName;
  doc["file_base64"] = fileBase64;
  
  if (currentLatitude != 0 && currentLongitude != 0) {
    doc["latitude"] = currentLatitude;
    doc["longitude"] = currentLongitude;
  }
  
  // ISO timestamp
  doc["captured_at"] = "2024-01-01T00:00:00Z"; // Should use RTC
  
  String payload;
  serializeJson(doc, payload);
  
  DEBUG_PRINTF("Uploading %s (%d bytes)...\n", evidenceType, fileSize);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 201) {
    DEBUG_PRINTF("✓ %s uploaded successfully\n", evidenceType);
    http.end();
    return true;
  } else {
    DEBUG_PRINTF("✗ %s upload failed: %d\n", evidenceType, httpCode);
    if (httpCode > 0) {
      DEBUG_PRINTLN(http.getString());
    }
    http.end();
    return false;
  }
}

#endif // COMMUNICATION_H