"""
main.py — RPI Sensor Logger to Firebase
Sensors: DHT11 (Temp + Humidity), MQ2 (Gas Detection)
"""

import time
import logging
from datetime import datetime, timezone
from dht11_sensor import DHT11Sensor
from mq2_sensor import MQ2Sensor
from firebase_client import FirebaseClient
from config import Config

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

    dht11 = DHT11Sensor(pin=Config.DHT11_PIN)
    mq2   = MQ2Sensor(pin=Config.MQ2_DO_PIN)
    db    = FirebaseClient(
        credentials_path=Config.FIREBASE_CREDENTIALS_PATH,
        database_url=Config.FIREBASE_DATABASE_URL
    )

    log.info(f"📡 Logging every {Config.LOG_INTERVAL_SECONDS}s → {Config.FIREBASE_DATABASE_URL}")
    log.info("Press Ctrl+C to stop.\n")

    while True:
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            temp, humidity = dht11.read()
            gas_detected, gas_status, mq2_do_raw = mq2.read()

            if temp is None or humidity is None:
                log.warning("⚠️  DHT11 read failed — check wiring. Retrying next cycle.")
                time.sleep(Config.LOG_INTERVAL_SECONDS)
                continue

            payload = {
                "timestamp":     timestamp,
                "temperature_c": round(temp, 1),
                "temperature_f": round((temp * 9/5) + 32, 1),
                "humidity_pct":  round(humidity, 1),
                "gas_detected":  gas_detected,
                "gas_status":    gas_status,
                "mq2_do_raw":    mq2_do_raw,
                "device_id":     Config.DEVICE_ID,
            }

            db.push(Config.FIREBASE_NODE, payload)

            log.info(
                f"✅ Temp: {payload['temperature_c']}°C  "
                f"Humidity: {payload['humidity_pct']}%  "
                f"Gas: {gas_status}"
            )

        except KeyboardInterrupt:
            log.info("\n🛑 Stopped by user.")
            dht11.cleanup()
            mq2.cleanup()
            break
        except Exception as e:
            log.error(f"❌ Error: {e}")

        time.sleep(Config.LOG_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()