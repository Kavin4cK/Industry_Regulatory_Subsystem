"""
main.py — RPI Sensor Logger to Firebase
Sensors: DS18B20 (Temperature), MQ2 (Gas Detection)
"""

import time
import logging
from datetime import datetime, timezone
from ds18b20_sensor import DS18B20Sensor
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

    ds18b20 = DS18B20Sensor()
    mq2     = MQ2Sensor(pin=Config.MQ2_DO_PIN)
    db      = FirebaseClient(
        credentials_path=Config.FIREBASE_CREDENTIALS_PATH,
        database_url=Config.FIREBASE_DATABASE_URL
    )

    log.info(f"📡 Logging every {Config.LOG_INTERVAL_SECONDS}s → {Config.FIREBASE_DATABASE_URL}")
    log.info("Press Ctrl+C to stop.\n")

    while True:
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            temp_c, temp_f       = ds18b20.read()
            gas_detected, gas_status, mq2_do_raw = mq2.read()

            if temp_c is None:
                log.warning("⚠️  DS18B20 read failed — check wiring. Retrying next cycle.")
                time.sleep(Config.LOG_INTERVAL_SECONDS)
                continue

            payload = {
                "timestamp":     timestamp,
                "temperature_c": temp_c,
                "temperature_f": temp_f,
                "gas_detected":  gas_detected,
                "gas_status":    gas_status,
                "mq2_do_raw":    mq2_do_raw,
                "device_id":     Config.DEVICE_ID,
            }

            db.push(Config.FIREBASE_NODE, payload)

            log.info(
                f"✅ Temp: {temp_c}°C ({temp_f}°F)  |  Gas: {gas_status}"
            )

        except KeyboardInterrupt:
            log.info("\n🛑 Stopped by user.")
            ds18b20.cleanup()
            mq2.cleanup()
            break
        except Exception as e:
            log.error(f"❌ Error: {e}")

        time.sleep(Config.LOG_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()