"""
====================================================
  Raspberry Pi 4B - Sensor Logger to Firebase
  Sensors: DHT11 (Temp + Humidity), MQ2 (Gas/CO2)
====================================================
"""

import time
import logging
from datetime import datetime
from dht11_sensor import DHT11Sensor
from mq2_sensor import MQ2Sensor
from firebase_client import FirebaseClient
from config import Config

# ── Logging Setup ──────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("sensor_log.txt")
    ]
)
log = logging.getLogger(__name__)


def main():
    log.info("🚀 Starting RPI Sensor Logger...")

    # Init sensors
    dht11 = DHT11Sensor(pin=Config.DHT11_PIN)
    mq2   = MQ2Sensor(channel=Config.MQ2_CHANNEL)

    # Init Firebase
    db = FirebaseClient(
        credentials_path=Config.FIREBASE_CREDENTIALS_PATH,
        database_url=Config.FIREBASE_DATABASE_URL
    )

    log.info(f"📡 Logging every {Config.LOG_INTERVAL_SECONDS}s → Firebase: {Config.FIREBASE_DATABASE_URL}")
    log.info("Press Ctrl+C to stop.\n")

    while True:
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Read DHT11
            temp, humidity = dht11.read()

            # Read MQ2
            mq2_raw, gas_ppm, gas_level = mq2.read()

            if temp is None or humidity is None:
                log.warning("⚠️  DHT11 read failed — skipping this cycle.")
                time.sleep(Config.LOG_INTERVAL_SECONDS)
                continue

            payload = {
                "timestamp":        timestamp,
                "temperature_c":    round(temp, 2),
                "temperature_f":    round((temp * 9/5) + 32, 2),
                "humidity_pct":     round(humidity, 2),
                "mq2_raw_adc":      mq2_raw,
                "gas_ppm":          round(gas_ppm, 2),
                "gas_level":        gas_level,        # "Safe" / "Warning" / "Danger"
                "device_id":        Config.DEVICE_ID,
            }

            db.push(Config.FIREBASE_NODE, payload)

            log.info(
                f"✅ Logged → Temp: {payload['temperature_c']}°C | "
                f"Humidity: {payload['humidity_pct']}% | "
                f"Gas: {payload['gas_ppm']} ppm ({gas_level})"
            )

        except KeyboardInterrupt:
            log.info("\n🛑 Stopped by user.")
            break
        except Exception as e:
            log.error(f"❌ Unexpected error: {e}")

        time.sleep(Config.LOG_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
