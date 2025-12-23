/**
 * Audio capture module using I2S microphone
 */

#ifndef AUDIO_H
#define AUDIO_H

#include <driver/i2s.h>
#include "config.h"

#define I2S_PORT I2S_NUM_0

bool audioInitialized = false;

/**
 * Initialize I2S microphone
 */
void initAudio() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = AUDIO_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    DEBUG_PRINTF("✗ I2S driver install failed: %d\n", err);
    audioInitialized = false;
    return;
  }
  
  err = i2s_set_pin(I2S_PORT, &pin_config);
  if (err != ESP_OK) {
    DEBUG_PRINTF("✗ I2S pin config failed: %d\n", err);
    audioInitialized = false;
    return;
  }
  
  // Clear DMA buffer
  i2s_zero_dma_buffer(I2S_PORT);
  
  audioInitialized = true;
  DEBUG_PRINTLN("✓ Audio system initialized");
}

/**
 * Capture audio sample for stress detection (3 seconds)
 * Returns: true on success, false on failure
 * Output: audioData pointer and audioSize
 */
bool captureAudioSample(uint8_t** audioData, size_t* audioSize) {
  if (!audioInitialized) {
    DEBUG_PRINTLN("✗ Audio not initialized");
    return false;
  }
  
  const size_t bufferSize = AUDIO_BUFFER_SIZE * 2; // 16-bit samples
  *audioData = (uint8_t*)malloc(bufferSize);
  
  if (*audioData == NULL) {
    DEBUG_PRINTLN("✗ Failed to allocate audio buffer");
    return false;
  }
  
  DEBUG_PRINTF("Capturing %d second audio sample...\n", AUDIO_SAMPLE_DURATION);
  
  size_t bytesRead = 0;
  size_t totalBytesRead = 0;
  
  // Capture audio
  unsigned long startTime = millis();
  while (millis() - startTime < (AUDIO_SAMPLE_DURATION * 1000)) {
    size_t bytesToRead = min((size_t)1024, bufferSize - totalBytesRead);
    
    esp_err_t result = i2s_read(I2S_PORT, 
                                 *audioData + totalBytesRead, 
                                 bytesToRead, 
                                 &bytesRead, 
                                 portMAX_DELAY);
    
    if (result == ESP_OK) {
      totalBytesRead += bytesRead;
      
      if (totalBytesRead >= bufferSize) {
        break;
      }
    } else {
      DEBUG_PRINTLN("✗ I2S read error");
      free(*audioData);
      *audioData = NULL;
      return false;
    }
  }
  
  *audioSize = totalBytesRead;
  DEBUG_PRINTF("✓ Audio captured: %d bytes\n", totalBytesRead);
  
  return true;
}

/**
 * Record audio for evidence (10 seconds)
 */
bool recordAudioEvidence(uint8_t** audioData, size_t* audioSize, int durationSeconds) {
  if (!audioInitialized) {
    return false;
  }
  
  const size_t bufferSize = AUDIO_SAMPLE_RATE * 2 * durationSeconds; // 16-bit
  *audioData = (uint8_t*)malloc(bufferSize);
  
  if (*audioData == NULL) {
    DEBUG_PRINTLN("✗ Failed to allocate audio buffer");
    return false;
  }
  
  DEBUG_PRINTF("Recording %d second audio...\n", durationSeconds);
  
  size_t bytesRead = 0;
  size_t totalBytesRead = 0;
  
  unsigned long startTime = millis();
  while (millis() - startTime < (durationSeconds * 1000)) {
    size_t bytesToRead = min((size_t)2048, bufferSize - totalBytesRead);
    
    esp_err_t result = i2s_read(I2S_PORT,
                                 *audioData + totalBytesRead,
                                 bytesToRead,
                                 &bytesRead,
                                 portMAX_DELAY);
    
    if (result == ESP_OK) {
      totalBytesRead += bytesRead;
      
      if (totalBytesRead >= bufferSize) {
        break;
      }
    }
  }
  
  *audioSize = totalBytesRead;
  DEBUG_PRINTF("✓ Audio recorded: %d bytes\n", totalBytesRead);
  
  return true;
}

/**
 * Capture and upload audio evidence
 */
bool captureAndUploadAudio(int alertId, int durationSeconds) {
  uint8_t* audioData = NULL;
  size_t audioSize = 0;
  
  if (!recordAudioEvidence(&audioData, &audioSize, durationSeconds)) {
    return false;
  }
  
  // Generate filename
  char fileName[64];
  sprintf(fileName, "audio_%d_%lu.wav", alertId, millis());
  
  // Upload to backend
  bool success = uploadEvidence(alertId, "audio", audioData, audioSize, fileName);
  
  // Free buffer
  if (audioData) free(audioData);
  
  return success;
}

/**
 * Check if audio system is available
 */
bool isAudioAvailable() {
  return audioInitialized;
}

#endif // AUDIO_H