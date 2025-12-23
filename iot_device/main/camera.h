/**
 * Camera module for ESP32-CAM
 */

#ifndef CAMERA_H
#define CAMERA_H

#include "esp_camera.h"
#include "config.h"

bool cameraInitialized = false;

/**
 * Initialize ESP32-CAM
 */
void initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size and quality
  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = CAMERA_JPEG_QUALITY;
  config.fb_count = 1;
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    DEBUG_PRINTF("✗ Camera init failed: 0x%x\n", err);
    cameraInitialized = false;
    return;
  }
  
  cameraInitialized = true;
  DEBUG_PRINTLN("✓ Camera initialized");
  
  // Camera settings
  sensor_t* s = esp_camera_sensor_get();
  if (s) {
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    s->set_aec2(s, 0);           // 0 = disable , 1 = enable
    s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
  }
}

/**
 * Capture a photo
 * Returns: Pointer to camera framebuffer (NULL on failure)
 */
camera_fb_t* capturePhoto() {
  if (!cameraInitialized) {
    DEBUG_PRINTLN("✗ Camera not initialized");
    return NULL;
  }
  
  camera_fb_t* fb = esp_camera_fb_get();
  
  if (!fb) {
    DEBUG_PRINTLN("✗ Camera capture failed");
    return NULL;
  }
  
  DEBUG_PRINTF("✓ Photo captured: %d bytes\n", fb->len);
  return fb;
}

/**
 * Capture and upload photo to backend
 */
bool captureAndUploadPhoto(int alertId) {
  camera_fb_t* fb = capturePhoto();
  
  if (!fb) {
    return false;
  }
  
  // Generate filename
  char fileName[64];
  sprintf(fileName, "photo_%d_%lu.jpg", alertId, millis());
  
  // Upload to backend
  bool success = uploadEvidence(alertId, "photo", fb->buf, fb->len, fileName);
  
  // Return framebuffer
  esp_camera_fb_return(fb);
  
  return success;
}

/**
 * Check if camera is available
 */
bool isCameraAvailable() {
  return cameraInitialized;
}

#endif // CAMERA_H