"""
config.py — All settings for the sensor logger.
"""

class Config:
    # Device
    DEVICE_ID = "rpi-4b-unit-01"

    # GPIO Pins (BCM numbering)
    DHT11_PIN  = 4      # DHT11 DATA → RPi Pin 7  (BCM GPIO4)
    MQ2_DO_PIN = 17     # MQ2 DO     → RPi Pin 11 (BCM GPIO17)

    # Firebase
    FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"
    FIREBASE_DATABASE_URL     = "https://industry-regulatory-subsystem-default-rtdb.firebaseio.com/"
    FIREBASE_NODE             = "sensor_logs"

    # Logging interval in seconds
    LOG_INTERVAL_SECONDS = 2