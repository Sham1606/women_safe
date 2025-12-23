# Hardware Setup Guide - ESP32 Women Safety Device

## Bill of Materials (BOM)

| Component | Specification | Quantity | Approx. Price (INR) |
|-----------|---------------|----------|---------------------|
| ESP32-CAM | AI-Thinker with OV2640 camera | 1 | ₹400-600 |
| MAX30102 | Heart rate & SpO2 sensor module | 1 | ₹250-350 |
| MLX90614 | Non-contact IR temperature sensor | 1 | ₹400-500 |
| NEO-6M GPS | GPS module with antenna | 1 | ₹400-600 |
| INMP441 | I2S MEMS microphone | 1 | ₹150-250 |
| Push Button | Tactile switch (emergency button) | 1 | ₹20-30 |
| Buzzer | 5V active buzzer | 1 | ₹20-30 |
| LED | 5mm LED (status indicator) | 1 | ₹5-10 |
| Resistor | 220Ω (for LED) | 1 | ₹2-5 |
| Li-Po Battery | 3.7V 3000mAh | 1 | ₹250-400 |
| TP4056 | Li-Po charging module | 1 | ₹30-50 |
| AMS1117-3.3 | 3.3V voltage regulator (if needed) | 1 | ₹20-30 |
| Voltage Divider | 10kΩ + 10kΩ resistors | 2 | ₹5-10 |
| MB102 | Breadboard power supply (optional) | 1 | ₹50-80 |
| Jumper Wires | Male-to-male, male-to-female | 40pcs | ₹50-100 |
| Breadboard | 830 points (for prototyping) | 1 | ₹50-100 |
| USB-TTL | Serial adapter for programming | 1 | ₹100-150 |

**Total Estimated Cost:** ₹2,500 - ₹3,500 INR (~$30-45 USD)

## Detailed Wiring Diagram

### ESP32-CAM Pin Layout

```
              ┌─────────────┐
              │  ESP32-CAM  │
              ├─────────────┤
          5V ─┤ 5V      GND ├─ GND
        IO16 ─┤ U0R      3V ├─ 3.3V
        IO17 ─┤ U0T     IO0 ├─ (Boot)
             ─┤ IO2     IO1 ├─
        IO15 ─┤ IO3     IO4 ├─ LED (Status)
        IO21 ─┤ SDA    IO12 ├─
        IO22 ─┤ SCL    IO13 ├─
        IO25 ─┤ WS     IO14 ├─
        IO32 ─┤ SCK    IO15 ├─ Button
        IO33 ─┤ SD     IO33 ├─ Mic SD
             ─┤        IO35 ├─ Battery ADC
              └─────────────┘
```

### Connection Table

#### 1. MAX30102 (Heart Rate Sensor)
```
MAX30102    →  ESP32-CAM
─────────────────────────
VIN         →  3.3V
GND         →  GND
SDA         →  GPIO 21
SCL         →  GPIO 22
INT         →  (Not connected)
```

#### 2. MLX90614 (Temperature Sensor)
```
MLX90614    →  ESP32-CAM
─────────────────────────
VIN         →  3.3V
GND         →  GND
SDA         →  GPIO 21 (shared with MAX30102)
SCL         →  GPIO 22 (shared with MAX30102)
```

**Note:** Both sensors share the same I2C bus (SDA/SCL)

#### 3. NEO-6M GPS Module
```
NEO-6M      →  ESP32-CAM
─────────────────────────
VCC         →  5V
GND         →  GND
TX          →  GPIO 16 (RX)
RX          →  GPIO 17 (TX)
```

#### 4. INMP441 Microphone (I2S)
```
INMP441     →  ESP32-CAM
─────────────────────────
VDD         →  3.3V
GND         →  GND
WS (LRCLK)  →  GPIO 25
SCK (BCLK)  →  GPIO 32
SD (DOUT)   →  GPIO 33
L/R         →  GND (left channel)
```

#### 5. Emergency Button
```
Button      →  ESP32-CAM
─────────────────────────
One terminal →  GPIO 15
Other terminal → GND
```

**Note:** Internal pull-up enabled in code, button is active LOW

#### 6. Buzzer
```
Buzzer      →  ESP32-CAM
─────────────────────────
+           →  GPIO 2
-           →  GND
```

#### 7. Status LED
```
LED         →  ESP32-CAM
─────────────────────────
Anode (+)   →  GPIO 4
Cathode (-) →  220Ω resistor → GND
```

#### 8. Battery Monitor (Voltage Divider)
```
Battery +   →  10kΩ resistor → GPIO 35 (ADC)
                                    ↓
                              10kΩ resistor → GND

Battery -   →  GND
```

**Voltage Divider Formula:** ADC voltage = (Battery voltage × R2) / (R1 + R2)

#### 9. Power Supply
```
Li-Po Battery (3.7V) → TP4056 Charging Module
                           ↓
                        Battery OUT+ → ESP32-CAM 5V
                        Battery OUT- → GND

USB (5V) → TP4056 IN+ (for charging)
```

## Assembly Instructions

### Step 1: Breadboard Layout

1. Place ESP32-CAM on breadboard
2. Connect power rails:
   - Red rail: 5V
   - Blue rail: GND
   - Yellow rail: 3.3V (from ESP32-CAM 3.3V pin)

### Step 2: I2C Sensors

1. Place MAX30102 and MLX90614 on breadboard
2. Connect both VIN to 3.3V rail
3. Connect both GND to GND rail
4. Wire SDA to GPIO 21 (shared)
5. Wire SCL to GPIO 22 (shared)

### Step 3: GPS Module

1. Place NEO-6M module
2. Connect VCC to 5V rail
3. Connect GND to GND rail
4. Wire GPS TX to ESP32 GPIO 16
5. Wire GPS RX to ESP32 GPIO 17

### Step 4: Microphone

1. Place INMP441 module
2. Connect VDD to 3.3V rail
3. Connect GND to GND rail
4. Connect L/R to GND
5. Wire WS to GPIO 25
6. Wire SCK to GPIO 32
7. Wire SD to GPIO 33

### Step 5: Button and Indicators

1. Insert push button across breadboard gap
2. Wire one terminal to GPIO 15
3. Wire other terminal to GND
4. Insert LED with 220Ω resistor
5. Connect LED anode to GPIO 4
6. Connect resistor to GND
7. Connect buzzer + to GPIO 2, - to GND

### Step 6: Battery System

1. Connect Li-Po battery to TP4056 module
2. Connect TP4056 OUT+ to ESP32-CAM 5V
3. Connect TP4056 OUT- to GND rail
4. Build voltage divider for battery monitoring
5. Connect divider midpoint to GPIO 35

### Step 7: Programming Connection

1. Connect USB-TTL adapter:
   - Adapter 5V → ESP32-CAM 5V
   - Adapter GND → ESP32-CAM GND
   - Adapter TX → ESP32-CAM U0R (RX)
   - Adapter RX → ESP32-CAM U0T (TX)
2. Connect GPIO 0 to GND (boot mode)
3. Press reset button
4. Upload firmware
5. Disconnect GPIO 0 from GND
6. Press reset again

## Testing Checklist

### Power Test
- [ ] Connect battery, check voltage (should be 3.7-4.2V)
- [ ] ESP32-CAM LED indicator lights up
- [ ] Check 3.3V output from ESP32

### Sensor Test
- [ ] Run I2C scanner (should detect 0x57 for MAX30102, 0x5A for MLX90614)
- [ ] Test heart rate sensor (place finger, check reading)
- [ ] Test temperature sensor (point at body, check reading)

### GPS Test
- [ ] Place GPS near window with clear sky view
- [ ] Wait 1-2 minutes for initial fix
- [ ] Check for valid coordinates in Serial Monitor

### Audio Test
- [ ] Open Serial Monitor
- [ ] Make noise near microphone
- [ ] Check if audio data is captured

### Camera Test
- [ ] Ensure camera cable is connected properly
- [ ] Run camera example code
- [ ] Verify image capture

### Button Test
- [ ] Press emergency button
- [ ] Buzzer should activate
- [ ] LED should blink
- [ ] Alert should be sent

## Enclosure Recommendations

### Wearable Design Options

1. **Wrist Band Style**
   - 3D printed case (60mm × 40mm × 15mm)
   - Elastic strap attachment
   - Sensors facing skin
   - Camera facing outward

2. **Pendant Style**
   - Compact rectangular case
   - Lanyard attachment
   - All sensors accessible
   - Lightweight design

3. **Clip-On Style**
   - Clothing clip attachment
   - Belt clip option
   - Quick release mechanism

### 3D Printing Files

STL files for enclosure available at: `iot_device/enclosure/`

## Safety Precautions

⚠️ **Important:**
- Do NOT short circuit battery terminals
- Use proper Li-Po charging module (TP4056)
- Do NOT exceed 5V on ESP32 VCC
- Ensure proper ventilation for battery
- Test thoroughly before deployment
- Add overcurrent protection

## Troubleshooting

### No Power
- Check battery voltage
- Verify TP4056 connections
- Test with USB power first

### I2C Sensors Not Detected
- Run I2C scanner sketch
- Check SDA/SCL connections
- Verify 3.3V power supply
- Try different I2C addresses

### GPS No Fix
- Ensure clear sky view
- Wait at least 2 minutes
- Check antenna connection
- Verify UART connections

### Camera Not Working
- Reseat camera cable
- Check for proper insertion
- Test with camera example code
- Try different partition scheme

## Next Steps

After hardware assembly:
1. Upload firmware (see README.md)
2. Configure WiFi and device token
3. Test all functions
4. Assemble in enclosure
5. Deploy and monitor
