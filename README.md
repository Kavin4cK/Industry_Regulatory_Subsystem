# 🌡️ RPI 4B Sensor Logger → Firebase

Log **Temperature**, **Humidity** (DHT11) and **Gas/CO2 concentration** (MQ2) to Firebase Realtime Database, time-stamped, every N seconds.

---

## 📁 Project Structure

```
rpi_firebase_sensors/
├── main.py                  # Entry point — runs the logger loop
├── config.py                # All settings (pins, Firebase URL, intervals)
├── requirements.txt
├── firebase_credentials.json  ← YOU ADD THIS
├── sensors/
│   ├── dht11_sensor.py      # DHT11 temperature + humidity
│   └── mq2_sensor.py        # MQ2 gas sensor via MCP3008 ADC
└── firebase/
    └── firebase_client.py   # Firebase Realtime DB wrapper
```

---

## 🔌 Wiring

### DHT11
| DHT11 Pin | Raspberry Pi |
|-----------|-------------|
| VCC       | 3.3V (Pin 1) |
| DATA      | GPIO 4 BCM (Pin 7) |
| GND       | GND (Pin 6) |

> Add a **10kΩ pull-up resistor** between DATA and VCC.

### MQ2 via MCP3008 (SPI ADC)

**MCP3008 → Raspberry Pi:**
| MCP3008 | RPi Pin |
|---------|---------|
| VDD     | 3.3V (Pin 1) |
| VREF    | 3.3V (Pin 1) |
| AGND    | GND (Pin 6) |
| CLK     | GPIO11 SCLK (Pin 23) |
| DOUT    | GPIO9 MISO (Pin 21) |
| DIN     | GPIO10 MOSI (Pin 19) |
| CS/SHDN | GPIO8 CE0 (Pin 24) |
| DGND    | GND (Pin 6) |

**MQ2 → MCP3008:**
| MQ2  | MCP3008 |
|------|---------|
| VCC  | 5V |
| GND  | GND |
| AOUT | CH0 |

---

## ☁️ Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a project → **Realtime Database** → Start in test mode
3. Go to **Project Settings → Service Accounts → Generate new private key**
4. Download the JSON and save it as `firebase_credentials.json` in the project root
5. Copy your **Database URL** (e.g. `https://your-project-default-rtdb.firebaseio.com`)
6. Paste it into `config.py` → `FIREBASE_DATABASE_URL`

---

## ⚙️ Raspberry Pi Setup

```bash
# 1. Enable SPI (for MCP3008/MQ2)
sudo raspi-config
# → Interface Options → SPI → Enable

# 2. Install dependencies
pip install -r requirements.txt --break-system-packages

# 3. Run
python main.py
```

---

## 🔧 Configuration (`config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `DHT11_PIN` | `4` | BCM GPIO pin for DHT11 DATA |
| `MQ2_CHANNEL` | `0` | MCP3008 channel (0–7) |
| `MQ2_RL_VALUE` | `10.0` | Load resistor on MQ2 board (kΩ) |
| `MQ2_RO_CLEAN_AIR` | `9.83` | Calibration value in clean air |
| `LOG_INTERVAL_SECONDS` | `10` | Seconds between readings |
| `FIREBASE_NODE` | `sensor_logs` | Root DB node for data |

---

## 📊 Firebase Data Structure

Each reading is pushed as a child under `/sensor_logs/`:

```json
{
  "sensor_logs": {
    "-NxAbc123": {
      "timestamp":      "2025-03-11T10:30:00Z",
      "temperature_c":  27.5,
      "temperature_f":  81.5,
      "humidity_pct":   58.2,
      "mq2_raw_adc":    312,
      "gas_ppm":        145.7,
      "gas_level":      "Safe",
      "device_id":      "rpi-4b-unit-01"
    }
  }
}
```

---

## 🧪 MQ2 Calibration

For accurate PPM readings:
1. Place the MQ2 in **clean open air** for 24–48 hours (burn-in)
2. Note the ADC value in clean air
3. Calculate `Ro`: `Ro = Rs_in_clean_air / 9.83`
4. Update `MQ2_RO_CLEAN_AIR` in `config.py`

> **Note:** MQ2 detects LPG, smoke, alcohol, propane, hydrogen, methane, and CO — not CO2 directly. For true CO2, use an **MH-Z19B** (UART sensor, easily addable).

---

## ▶️ Run as a System Service (Auto-start on Boot)

```bash
sudo nano /etc/systemd/system/sensor_logger.service
```

```ini
[Unit]
Description=RPI Sensor Logger to Firebase
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/rpi_firebase_sensors/main.py
WorkingDirectory=/home/pi/rpi_firebase_sensors
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sensor_logger
sudo systemctl start sensor_logger
sudo systemctl status sensor_logger
```
