# 🏭 Industry Regulatory Subsystem
### Raspberry Pi 4B · DS18B20 Temperature · MQ2 Gas Detection · Firebase Realtime Database

> **Complete guide** — from a blank SD card to live sensor data streaming to the cloud.

---

## 📋 Table of Contents

1. [Hardware Requirements](#1-hardware-requirements)
2. [Flashing Raspberry Pi OS](#2-flashing-raspberry-pi-os)
3. [First Boot & Initial Setup](#3-first-boot--initial-setup)
4. [Circuit Wiring](#4-circuit-wiring)
5. [Enable 1-Wire for DS18B20](#5-enable-1-wire-for-ds18b20)
6. [Firebase Project Setup](#6-firebase-project-setup)
7. [Project Installation](#7-project-installation)
8. [Configuration](#8-configuration)
9. [Running the Logger](#9-running-the-logger)
10. [Firebase Data Structure](#10-firebase-data-structure)
11. [Auto-Start on Boot](#11-auto-start-on-boot)
12. [Troubleshooting](#12-troubleshooting)
13. [File Reference](#13-file-reference)

---

## 1. Hardware Requirements

### Components

| Component | Purpose | Notes |
|-----------|---------|-------|
| Raspberry Pi 4B | Main controller | Any RAM variant works |
| MicroSD Card | OS storage | 16GB+ recommended, Class 10 |
| DS18B20 | Temperature sensor | Waterproof or bare TO-92 variant |
| MQ2 | Gas sensor module | Detects LPG, smoke, CO, methane |
| 4.7kΩ Resistor | DS18B20 pull-up | **Required** — sensor won't work without it |
| Jumper wires | Connections | Male-to-female recommended |
| Breadboard | Prototyping | Optional but recommended |
| 5V Power Supply | Pi power | Official RPi PSU or 5V/3A USB-C |

### Tools Needed

- PC or Mac with internet connection (for flashing)
- Raspberry Pi Imager (free download)
- Micro-HDMI cable + monitor (or SSH access)
- USB keyboard + mouse (for first boot, or use SSH)
- Small Phillips screwdriver (for MQ2 potentiometer)

---

## 2. Flashing Raspberry Pi OS

### Step 1 — Download Raspberry Pi Imager

Go to [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/) and download the Imager for your OS (Windows / macOS / Linux).

Install and launch it.

### Step 2 — Flash the OS

1. Insert your MicroSD card into your PC
2. Open **Raspberry Pi Imager**
3. Click **"Choose Device"** → Select **Raspberry Pi 4**
4. Click **"Choose OS"** → Select:
   ```
   Raspberry Pi OS (64-bit)
   ```
   > Use the **Lite** version if you don't need a desktop (headless setup)

5. Click **"Choose Storage"** → Select your MicroSD card

### Step 3 — Configure OS Settings (Important!)

Before flashing, click the **⚙️ gear icon** (or "Edit Settings") to pre-configure:

**General tab:**
```
✅ Set hostname:        raspberrypi
✅ Set username:        kavin
✅ Set password:        [your password]
✅ Configure WiFi:      [your WiFi SSID + password]
    WiFi country:       IN  (for India)
✅ Set locale:
    Timezone:           Asia/Kolkata
    Keyboard layout:    us
```

**Services tab:**
```
✅ Enable SSH
   ● Use password authentication
```

Click **Save** → Click **Write** → Wait for flash to complete (~3–5 minutes).

### Step 4 — Eject and Insert

Safely eject the SD card from your PC and insert it into the Raspberry Pi.

---

## 3. First Boot & Initial Setup

### Power On

Connect power to the Pi. Wait **60–90 seconds** for first boot to complete.

### Find the Pi's IP Address

**Option A — Check your router's admin panel** for a device named `raspberrypi`.

**Option B — Scan your network:**
```bash
# On Linux/macOS
ping raspberrypi.local

# Or use nmap
nmap -sn 192.168.1.0/24 | grep raspberry
```

### Connect via SSH

```bash
ssh kavin@raspberrypi.local
# or
ssh kavin@192.168.1.XXX
```

Enter your password when prompted.

### Update the System

Always update before installing anything:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

This may take 5–10 minutes on first run.

### Set Timezone (India)

```bash
sudo timedatectl set-timezone Asia/Kolkata
timedatectl status
# Should show: Time zone: Asia/Kolkata (IST, +0530)
```

### Sync Clock

```bash
sudo apt-get install chrony -y
sudo chronyc makestep
date
# Should show correct IST time
```

### Enable SPI and I2C (optional but good practice)

```bash
sudo raspi-config
```

Navigate to: `Interface Options` → Enable **SPI**, **I2C**, **1-Wire**

Or do it manually (see Section 5 for 1-Wire).

---

## 4. Circuit Wiring

> ⚠️ **Always power off the Pi before connecting or disconnecting wires.**

### Raspberry Pi GPIO Pinout Reference

```
                    3V3  (1) (2)  5V
                  GPIO2  (3) (4)  5V
                  GPIO3  (5) (6)  GND  ←── GND (shared)
              [DS18B20]  (7) (8)  GPIO14
                    GND  (9) (10) GPIO15
    [MQ2 DO] GPIO17 (11) (12) GPIO18
                GPIO27 (13) (14) GND
                GPIO22 (15) (16) GPIO23
                    3V3 (17) (18) GPIO24
               GPIO10 (19) (20) GND
                GPIO9 (21) (22) GPIO25
               GPIO11 (23) (24) GPIO8
                   GND (25) (26) GPIO7
```

---

### DS18B20 Temperature Sensor Wiring

The DS18B20 has 3 pins. Hold it with the **flat face toward you**, pins pointing down — left to right:

```
┌─────────────┐
│   DS18B20   │  (flat face)
└──┬────┬────┘
   │    │    │
  GND  DATA  VCC
  (1)  (2)   (3)
```

| DS18B20 Pin | Wire Color | Connects To | RPi Physical Pin |
|-------------|-----------|-------------|-----------------|
| PIN 1 — GND | Black | GND | Pin 6 |
| PIN 2 — DATA | Yellow | GPIO4 | Pin 7 |
| PIN 3 — VCC | Red | 3.3V | Pin 1 |

**⚡ CRITICAL — Pull-up Resistor:**

```
3.3V (Pin 1) ──────┬──────── DS18B20 VCC (Pin 3)
                   │
                 [4.7kΩ]
                   │
GPIO4 (Pin 7) ─────┴──────── DS18B20 DATA (Pin 2)
```

Connect a **4.7kΩ resistor** between VCC and DATA. Without this, the sensor will not be detected — this is the most common wiring mistake.

---

### MQ2 Gas Sensor Wiring

The MQ2 breakout module has 4 pins labeled on the PCB:

| MQ2 Pin | Wire Color | Connects To | RPi Physical Pin |
|---------|-----------|-------------|-----------------|
| VCC | Red | 5V | Pin 2 |
| GND | Black | GND | Pin 6 (shared with DS18B20) |
| DO | Purple | GPIO17 | Pin 11 |
| AO | — | **NOT CONNECTED** | — |

> The **AO (Analog Output)** pin requires an ADC chip to read. We use **DO (Digital Output)** only, which works directly with the Pi's GPIO. Leave AO unconnected.

**MQ2 Sensitivity Adjustment:**

The blue potentiometer on the MQ2 board sets the gas detection threshold:
- Turn **clockwise** = less sensitive (higher threshold)
- Turn **counter-clockwise** = more sensitive (lower threshold)

To calibrate: in clean air, turn the pot until the DO LED just turns OFF. That's your baseline threshold.

---

### Complete Wiring Summary

```
Raspberry Pi 4B          Sensors
───────────────          ───────
Pin 1  (3.3V) ──────────── DS18B20 VCC (Pin 3)
                    │
                  [4.7kΩ]
                    │
Pin 7  (GPIO4) ─────┴────── DS18B20 DATA (Pin 2)
Pin 6  (GND)  ──────┬────── DS18B20 GND (Pin 1)
                    │
                    └────── MQ2 GND
Pin 2  (5V)   ─────────────MQ2 VCC
Pin 11 (GPIO17)────────────MQ2 DO
```

---

## 5. Enable 1-Wire for DS18B20

The DS18B20 uses the 1-Wire protocol which must be enabled in the Pi's config.

### Add the Overlay

```bash
sudo nano /boot/firmware/config.txt
```

Scroll to the bottom and add:

```
dtoverlay=w1-gpio,gpiopin=4
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

### Reboot

```bash
sudo reboot
```

### Verify Sensor Detection

After reboot, reconnect via SSH and run:

```bash
ls /sys/bus/w1/devices/
```

You should see output like:

```
28-3c01d6075f3e   w1_bus_master1
```

The `28-xxxxxxxxxxxx` entry is your DS18B20. If you don't see it, check:
- The 4.7kΩ resistor is in place
- VCC is on Pin 3 (not Pin 1) of the sensor
- `dtoverlay=w1-gpio,gpiopin=4` was saved correctly

### Test a Raw Reading

```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

Output:
```
50 05 55 05 7f a5 a5 66 1a : crc=1a YES
50 05 55 05 7f a5 a5 66 1a t=26500
```

`t=26500` means **26.5°C**. If the first line ends in `YES`, the CRC passed and the reading is valid.

---

## 6. Firebase Project Setup

### Create a Firebase Project

1. Go to [https://console.firebase.google.com](https://console.firebase.google.com)
2. Click **"Add project"**
3. Enter project name: `Industry-Regulatory-Subsystem`
4. Disable Google Analytics (optional)
5. Click **"Create project"**

### Create a Realtime Database

1. In left sidebar → **Build** → **Realtime Database**
2. Click **"Create Database"**
3. Choose location: **Singapore** (closest to India)
4. Start in **test mode** (allows read/write without auth for now)
5. Click **Enable**

Copy your database URL — it looks like:
```
https://industry-regulatory-subsystem-default-rtdb.firebaseio.com/
```

### Get the Database Secret (for authentication)

1. Click ⚙️ **Project Settings** (gear icon, top left)
2. Go to **Service Accounts** tab
3. Click **"Database secrets"** in the left panel
4. Click **"Show"** next to the secret
5. Copy the long token string

### Set Database Rules

Go to **Realtime Database** → **Rules** tab and set:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

Click **Publish**.

> ⚠️ These are open rules for development. Restrict them before deploying to production.

---

## 7. Project Installation

### Create Project Directory

```bash
mkdir ~/Industry_Regulatory_Subsystem
cd ~/Industry_Regulatory_Subsystem
```

### Install Dependencies

```bash
pip install firebase-admin RPi.GPIO adafruit-circuitpython-dht --break-system-packages
```

> `lgpio` is pre-installed on Debian Trixie / RPi OS Bookworm and newer — no need to install it separately.

### Create Project Files

Create the following files in `~/Industry_Regulatory_Subsystem/`:

**`config.py`**
```python
class Config:
    DEVICE_ID = "rpi-4b-unit-01"
    DS18B20_PIN = 4       # GPIO4 → RPi Pin 7
    MQ2_DO_PIN  = 17      # GPIO17 → RPi Pin 11
    FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"
    FIREBASE_DATABASE_URL     = "https://YOUR-PROJECT-default-rtdb.firebaseio.com/"
    FIREBASE_NODE             = "sensor_data"
    LOG_INTERVAL_SECONDS      = 2
```

**`firebase_credentials.json`**
```json
{
  "database_secret": "PASTE_YOUR_DATABASE_SECRET_HERE"
}
```

**`firebase_client.py`** — handles all Firebase communication via REST API (no JWT required):

```python
import logging, json, urllib.request

log = logging.getLogger(__name__)

class FirebaseClient:
    def __init__(self, credentials_path, database_url):
        self._db_url = database_url.rstrip("/")
        self._secret = None
        try:
            with open(credentials_path) as f:
                self._secret = json.load(f).get("database_secret")
            if self._secret:
                log.info("Firebase REST client ready.")
            else:
                log.error("No 'database_secret' in credentials file.")
        except Exception as e:
            log.error(f"Firebase init failed: {e}")

    def set(self, node, data):
        if not self._secret:
            log.info(f"[LOCAL] {data}"); return
        try:
            url  = f"{self._db_url}/{node}.json?auth={self._secret}"
            body = json.dumps(data).encode("utf-8")
            req  = urllib.request.Request(url, data=body, method="PUT")
            req.add_header("Content-Type", "application/json")
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            log.error(f"Firebase set failed: {e}")
```

**`ds18b20_sensor.py`** — reads temperature directly from Linux kernel sysfs:

```python
import os, glob, time, logging

log = logging.getLogger(__name__)

class DS18B20Sensor:
    def __init__(self):
        self._device_path = None
        devices = glob.glob("/sys/bus/w1/devices/28-*")
        if devices:
            self._device_path = devices[0] + "/w1_slave"
            log.info(f"DS18B20 found: {devices[0]}")
        else:
            log.error("DS18B20 not found. Enable 1-Wire and reboot.")

    def read(self):
        if not self._device_path:
            return None, None
        for _ in range(3):
            try:
                with open(self._device_path) as f:
                    lines = f.readlines()
                if lines[0].strip().endswith("YES"):
                    pos    = lines[1].find("t=")
                    temp_c = round(float(lines[1][pos+2:]) / 1000.0, 2)
                    temp_f = round((temp_c * 9/5) + 32, 2)
                    return temp_c, temp_f
            except Exception as e:
                log.debug(f"DS18B20 read error: {e}")
            time.sleep(1)
        return None, None

    def cleanup(self): pass
```

**`mq2_sensor.py`** — reads digital output from MQ2:

```python
import logging

log = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class MQ2Sensor:
    def __init__(self, pin=17):
        self.pin = pin
        self._setup_done = False
        if not GPIO_AVAILABLE:
            return
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._setup_done = True
            log.info(f"MQ2 initialised on BCM GPIO{self.pin}.")
        except Exception as e:
            log.error(f"MQ2 setup failed: {e}")

    def read(self):
        if not GPIO_AVAILABLE or not self._setup_done:
            return False, "Clear", 1
        try:
            do_raw       = GPIO.input(self.pin)
            gas_detected = (do_raw == GPIO.LOW)
            return gas_detected, "Gas Detected" if gas_detected else "Clear", do_raw
        except Exception as e:
            log.error(f"MQ2 read error: {e}")
            return False, "Read Error", -1

    def cleanup(self):
        if GPIO_AVAILABLE and self._setup_done:
            GPIO.cleanup(self.pin)
```

**`main.py`** — main loop:

```python
import time, logging
from ds18b20_sensor import DS18B20Sensor
from mq2_sensor import MQ2Sensor
from firebase_client import FirebaseClient
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("sensor_log.txt")]
)
log = logging.getLogger(__name__)

def main():
    log.info("🚀 Starting RPI Sensor Logger...")
    ds18b20 = DS18B20Sensor()
    mq2     = MQ2Sensor(pin=Config.MQ2_DO_PIN)
    db      = FirebaseClient(Config.FIREBASE_CREDENTIALS_PATH, Config.FIREBASE_DATABASE_URL)
    log.info(f"📡 Updating Firebase every {Config.LOG_INTERVAL_SECONDS}s")

    while True:
        try:
            temp_c, temp_f              = ds18b20.read()
            gas_detected, gas_status, _ = mq2.read()

            if temp_c is None:
                log.warning("⚠️ DS18B20 read failed — retrying.")
                time.sleep(Config.LOG_INTERVAL_SECONDS)
                continue

            payload = {
                "temperature_c": temp_c,
                "temperature_f": temp_f,
                "gas_detected":  gas_detected,
                "gas_status":    gas_status,
            }

            db.set(Config.FIREBASE_NODE, payload)
            log.info(f"✅ Temp: {temp_c}°C ({temp_f}°F)  |  Gas: {gas_status}")

        except KeyboardInterrupt:
            log.info("🛑 Stopped."); ds18b20.cleanup(); mq2.cleanup(); break
        except Exception as e:
            log.error(f"❌ {e}")

        time.sleep(Config.LOG_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
```

### Final File Structure

```
~/Industry_Regulatory_Subsystem/
├── main.py                   ← Entry point
├── config.py                 ← All settings
├── ds18b20_sensor.py         ← Temperature sensor driver
├── mq2_sensor.py             ← Gas sensor driver
├── firebase_client.py        ← Firebase REST API client
├── firebase_credentials.json ← Your database secret
└── sensor_log.txt            ← Auto-generated log file
```

---

## 8. Configuration

Edit `config.py` to match your setup:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEVICE_ID` | `rpi-4b-unit-01` | Unique name for this device |
| `DS18B20_PIN` | `4` | BCM GPIO pin for DS18B20 DATA |
| `MQ2_DO_PIN` | `17` | BCM GPIO pin for MQ2 DO |
| `FIREBASE_DATABASE_URL` | `https://...firebaseio.com/` | Your Firebase DB URL |
| `FIREBASE_CREDENTIALS_PATH` | `firebase_credentials.json` | Path to credentials file |
| `FIREBASE_NODE` | `sensor_data` | Firebase DB node name |
| `LOG_INTERVAL_SECONDS` | `2` | How often to update Firebase |

Edit `firebase_credentials.json` and paste your Database Secret:

```json
{
  "database_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

## 9. Running the Logger

```bash
cd ~/Industry_Regulatory_Subsystem
python main.py
```

### Expected Output

```
2026-03-12 06:30:00,123 [INFO] 🚀 Starting RPI Sensor Logger...
2026-03-12 06:30:00,124 [INFO] DS18B20 found: /sys/bus/w1/devices/28-3c01d6075f3e
2026-03-12 06:30:00,125 [INFO] MQ2 initialised on BCM GPIO17.
2026-03-12 06:30:00,401 [INFO] Firebase REST client ready.
2026-03-12 06:30:00,402 [INFO] 📡 Updating Firebase every 2s
2026-03-12 06:30:02,614 [INFO] ✅ Temp: 29.74°C (85.53°F)  |  Gas: Clear
2026-03-12 06:30:04,721 [INFO] ✅ Temp: 29.75°C (85.55°F)  |  Gas: Clear
```

Stop with `Ctrl+C`.

---

## 10. Firebase Data Structure

Your Firebase Realtime Database will have a single node that gets **overwritten every 2 seconds**:

```
https://industry-regulatory-subsystem-default-rtdb.firebaseio.com/
└── sensor_data/
    ├── temperature_c: 29.74
    ├── temperature_f: 85.53
    ├── gas_detected:  false
    └── gas_status:    "Clear"
```

When gas is detected:
```json
{
  "sensor_data": {
    "temperature_c": 31.20,
    "temperature_f": 88.16,
    "gas_detected":  true,
    "gas_status":    "Gas Detected"
  }
}
```

To view live: open your Firebase Console → Realtime Database → watch the values update every 2 seconds.

---

## 11. Auto-Start on Boot

To have the logger start automatically every time the Pi boots:

### Create a systemd Service

```bash
sudo nano /etc/systemd/system/sensor_logger.service
```

Paste:

```ini
[Unit]
Description=Industry Regulatory Subsystem Sensor Logger
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=kavin
WorkingDirectory=/home/kavin/Industry_Regulatory_Subsystem
ExecStart=/usr/bin/python3 /home/kavin/Industry_Regulatory_Subsystem/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

### Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable sensor_logger
sudo systemctl start sensor_logger
```

### Check Status

```bash
sudo systemctl status sensor_logger
```

### View Live Logs

```bash
journalctl -u sensor_logger -f
```

### Stop / Restart

```bash
sudo systemctl stop sensor_logger
sudo systemctl restart sensor_logger
```

---

## 12. Troubleshooting

### DS18B20 not detected (`ls /sys/bus/w1/devices/` shows nothing)

| Check | Fix |
|-------|-----|
| `dtoverlay=w1-gpio,gpiopin=4` in config.txt? | Add it and reboot |
| Did you reboot after adding overlay? | `sudo reboot` |
| 4.7kΩ pull-up resistor connected? | Connect between VCC and DATA |
| VCC on correct pin (Pin 3, rightmost)? | Verify pin orientation |

### DS18B20 returns wrong temperature

The sensor is reading but values fluctuate wildly — this means the pull-up resistor value is wrong or connection is loose. Re-seat all wires and confirm 4.7kΩ (not 47kΩ).

### MQ2 always shows "Gas Detected"

The potentiometer threshold is set too sensitive. Turn it **clockwise** slightly to raise the threshold.

### MQ2 never triggers

The potentiometer threshold is too high. Turn it **counter-clockwise**. Also verify DO is connected to GPIO17 (Pin 11), not AO.

### Firebase push fails — `invalid_grant: Invalid JWT Signature`

Your Pi's clock is wrong. Fix:

```bash
sudo timedatectl set-timezone Asia/Kolkata
sudo apt-get install chrony -y
sudo chronyc makestep
date
```

If still failing, use the **Database Secret** method (REST API) instead of firebase-admin SDK — see `firebase_client.py` in this project, which already uses this approach.

### Firebase push fails — `Permission denied`

Your database rules are blocking writes. In Firebase Console → Realtime Database → Rules, set:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

Click **Publish**.

### `ModuleNotFoundError: No module named 'sensors'`

All files must be in the **same flat directory** — no subfolders. Run:

```bash
ls ~/Industry_Regulatory_Subsystem/
# Should show: main.py config.py ds18b20_sensor.py mq2_sensor.py firebase_client.py
```

Always run from inside the project folder:

```bash
cd ~/Industry_Regulatory_Subsystem
python main.py
```

### WiFi drops / Pi loses connection

```bash
# Check WiFi status
iwconfig wlan0

# Reconnect
sudo ifconfig wlan0 down && sudo ifconfig wlan0 up
```

To prevent WiFi power saving (common cause of drops):

```bash
sudo nano /etc/network/interfaces
```

Add:
```
wireless-power off
```

---

## 13. File Reference

### `main.py`
Entry point. Initialises all sensors and Firebase, then runs an infinite loop reading sensors and pushing data to Firebase every `LOG_INTERVAL_SECONDS`.

### `config.py`
Single source of truth for all configuration. Edit this file to change pins, Firebase URL, or logging interval. Never hardcode values in other files.

### `ds18b20_sensor.py`
Reads temperature by parsing `/sys/bus/w1/devices/28-*/w1_slave` — the Linux kernel 1-Wire sysfs interface. No external Python libraries required. Returns `(temp_c, temp_f)` or `(None, None)` on failure.

### `mq2_sensor.py`
Reads the MQ2 DO pin state via `RPi.GPIO`. Returns `(gas_detected: bool, status: str, raw: int)`. Active-LOW logic: GPIO reads `0` when gas is detected, `1` when clear.

### `firebase_client.py`
Sends data to Firebase Realtime Database using plain HTTPS REST API (`urllib`). Uses the Database Secret for authentication — bypasses JWT entirely, so Pi clock sync is not required.

### `firebase_credentials.json`
Contains only one field: `database_secret`. Keep this file private — do not commit to git.

### `sensor_log.txt`
Auto-generated. Contains timestamped logs of every reading and any errors. Useful for debugging.

---

## Quick Reference — RPi GPIO Pins Used

| Physical Pin | BCM | Function | Connected To |
|---|---|---|---|
| Pin 1 | — | 3.3V Power | DS18B20 VCC |
| Pin 2 | — | 5V Power | MQ2 VCC |
| Pin 6 | — | GND | DS18B20 GND + MQ2 GND |
| Pin 7 | GPIO4 | 1-Wire Data | DS18B20 DATA |
| Pin 11 | GPIO17 | Digital Input | MQ2 DO |

---

*Built for the Industry Regulatory Subsystem project · Raspberry Pi 4B IoT Lab*