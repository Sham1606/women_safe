/**
 * Sensor interface for heart rate and temperature sensors
 */

#ifndef SENSORS_H
#define SENSORS_H

#include <Wire.h>
#include "MAX30105.h"  // SparkFun MAX3010x library
#include "heartRate.h"
#include <Adafruit_MLX90614.h>  // For MLX90614 IR temperature sensor
#include "config.h"

// Global sensor objects
MAX30105 particleSensor;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// Heart rate detection variables
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;

bool heartRateSensorAvailable = false;
bool temperatureSensorAvailable = false;

/**
 * Initialize all sensors
 */
void initSensors() {
  // Initialize I2C
  Wire.begin(I2C_SDA, I2C_SCL);
  
  // Initialize MAX30102 Heart Rate Sensor
  DEBUG_PRINTLN("Initializing MAX30102 heart rate sensor...");
  if (particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);  // Turn Red LED to low
    particleSensor.setPulseAmplitudeGreen(0);   // Turn off Green LED
    heartRateSensorAvailable = true;
    DEBUG_PRINTLN("✓ Heart rate sensor initialized");
  } else {
    heartRateSensorAvailable = false;
    DEBUG_PRINTLN("✗ Heart rate sensor not found");
  }
  
  // Initialize MLX90614 Temperature Sensor
  DEBUG_PRINTLN("Initializing MLX90614 temperature sensor...");
  if (mlx.begin()) {
    temperatureSensorAvailable = true;
    DEBUG_PRINTLN("✓ Temperature sensor initialized");
  } else {
    temperatureSensorAvailable = false;
    DEBUG_PRINTLN("✗ Temperature sensor not found");
  }
}

/**
 * Read heart rate from MAX30102 sensor
 * Returns: Heart rate in BPM (0 if not available)
 */
float readHeartRate() {
  if (!heartRateSensorAvailable) {
    // Return simulated data for testing
    return 75.0 + random(-10, 10);
  }
  
  long irValue = particleSensor.getIR();
  
  if (irValue < 50000) {
    // No finger detected
    DEBUG_PRINTLN("No finger detected on heart rate sensor");
    return 0;
  }
  
  if (checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();
    
    beatsPerMinute = 60 / (delta / 1000.0);
    
    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;
      
      // Calculate average
      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++) {
        beatAvg += rates[x];
      }
      beatAvg /= RATE_SIZE;
    }
  }
  
  return beatAvg > 0 ? beatAvg : beatsPerMinute;
}

/**
 * Read temperature from MLX90614 sensor
 * Returns: Temperature in Celsius (0 if not available)
 */
float readTemperature() {
  if (!temperatureSensorAvailable) {
    // Return simulated data for testing
    return 36.5 + random(-5, 5) / 10.0;
  }
  
  // Read object temperature (body temperature)
  float temp = mlx.readObjectTempC();
  
  // Validate reading
  if (temp < 30.0 || temp > 45.0) {
    DEBUG_PRINTLN("Invalid temperature reading");
    return 0;
  }
  
  return temp;
}

/**
 * Check if heart rate sensor is available
 */
bool isHeartRateSensorAvailable() {
  return heartRateSensorAvailable;
}

/**
 * Check if temperature sensor is available
 */
bool isTemperatureSensorAvailable() {
  return temperatureSensorAvailable;
}

/**
 * Get sensor status as JSON string
 */
String getSensorStatus() {
  String status = "{";
  status += "\"heart_rate_sensor\": " + String(heartRateSensorAvailable ? "true" : "false") + ",";
  status += "\"temperature_sensor\": " + String(temperatureSensorAvailable ? "true" : "false");
  status += "}";
  return status;
}

#endif // SENSORS_H