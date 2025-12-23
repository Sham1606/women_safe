/**
 * GPS module using NEO-6M or similar
 */

#ifndef GPS_H
#define GPS_H

#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include "config.h"

TinyGPSPlus gps;
HardwareSerial gpsSerial(1); // Use UART1

bool gpsAvailable = false;
float lastLatitude = 0;
float lastLongitude = 0;
unsigned long lastGPSUpdate = 0;

/**
 * Initialize GPS module
 */
void initGPS() {
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  
  DEBUG_PRINTLN("GPS module initialized");
  DEBUG_PRINTLN("Waiting for GPS fix...");
  
  // Wait a bit for GPS to initialize
  delay(1000);
  
  // Check if data is coming
  if (gpsSerial.available() > 0) {
    gpsAvailable = true;
    DEBUG_PRINTLN("✓ GPS data detected");
  } else {
    DEBUG_PRINTLN("✗ No GPS data detected");
  }
}

/**
 * Update GPS data from serial
 */
void updateGPS() {
  unsigned long currentMillis = millis();
  
  // Update at specified interval
  if (currentMillis - lastGPSUpdate < GPS_UPDATE_INTERVAL) {
    return;
  }
  
  lastGPSUpdate = currentMillis;
  
  // Read GPS data
  while (gpsSerial.available() > 0) {
    char c = gpsSerial.read();
    
    if (gps.encode(c)) {
      // New data available
      if (gps.location.isValid()) {
        lastLatitude = gps.location.lat();
        lastLongitude = gps.location.lng();
        
        if (!gpsAvailable) {
          gpsAvailable = true;
          DEBUG_PRINTLN("✓ GPS fix acquired!");
          DEBUG_PRINTF("Location: %.6f, %.6f\n", lastLatitude, lastLongitude);
        }
      }
    }
  }
  
  // Check GPS fix status
  if (gpsAvailable && !gps.location.isValid()) {
    // Lost GPS fix
    if (currentMillis - gps.location.age() > 30000) { // 30 seconds
      DEBUG_PRINTLN("✗ GPS fix lost");
      gpsAvailable = false;
    }
  }
}

/**
 * Check if GPS has valid fix
 */
bool isGPSAvailable() {
  return gpsAvailable && gps.location.isValid();
}

/**
 * Get current latitude
 */
float getLatitude() {
  if (gps.location.isValid()) {
    return gps.location.lat();
  }
  return lastLatitude;
}

/**
 * Get current longitude
 */
float getLongitude() {
  if (gps.location.isValid()) {
    return gps.location.lng();
  }
  return lastLongitude;
}

/**
 * Get GPS altitude in meters
 */
float getAltitude() {
  if (gps.altitude.isValid()) {
    return gps.altitude.meters();
  }
  return 0;
}

/**
 * Get GPS speed in km/h
 */
float getSpeed() {
  if (gps.speed.isValid()) {
    return gps.speed.kmph();
  }
  return 0;
}

/**
 * Get number of satellites
 */
int getSatellites() {
  if (gps.satellites.isValid()) {
    return gps.satellites.value();
  }
  return 0;
}

/**
 * Get GPS status as string
 */
String getGPSStatus() {
  if (!isGPSAvailable()) {
    return "No GPS fix";
  }
  
  char status[128];
  sprintf(status, "GPS: %.6f, %.6f | Sats: %d | Alt: %.1fm",
          getLatitude(), getLongitude(), getSatellites(), getAltitude());
  
  return String(status);
}

#endif // GPS_H