"""
config.py — Central configuration for the sensor logger.
Edit these values to match your hardware and Firebase project.
"""


class Config:
    # ── Device Identity ──────────────────────────────
    DEVICE_ID = "rpi-4b-unit-01"          # Unique ID for this Pi (useful for multi-device setups)

    # ── GPIO / Hardware Pins ─────────────────────────
    DHT11_PIN    = 4                        # BCM GPIO pin connected to DHT11 DATA
    MQ2_CHANNEL  = 0                        # MCP3008 SPI channel for MQ2 (CH0–CH7)

    # ── MQ2 Calibration ──────────────────────────────
    MQ2_RL_VALUE     = 10.0                 # Load resistance on MQ2 board (kΩ), usually 10kΩ
    MQ2_RO_CLEAN_AIR = 9.83                 # Sensor resistance in clean air (calibrate this!)
    MQ2_ADC_MAX      = 1023                 # MCP3008 is 10-bit (0–1023)
    MQ2_VCC          = 5.0                  # Supply voltage (V)

    # Gas PPM thresholds (for LPG / smoke approximation)
    MQ2_WARNING_PPM  = 300
    MQ2_DANGER_PPM   = 1000

    # ── Firebase ───────────────────────────────────
    FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"   # Service account JSON key
    FIREBASE_DATABASE_URL     = "https://industry-regulatory-subsystem-default-rtdb.firebaseio.com/"
    FIREBASE_NODE             = "sensor_logs"                  # Root node in Realtime DB

    # ── Logging ───────────────────────────────────────
    LOG_INTERVAL_SECONDS = 2              # How often to read & upload (seconds)
