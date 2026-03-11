"""
sensors/dht11_sensor.py
Reads Temperature and Humidity from a DHT11 sensor via Adafruit's library.

Wiring:
  DHT11 VCC  → 3.3V or 5V (Pin 1 or 2)
  DHT11 DATA → GPIO 4     (BCM, configurable in config.py)
  DHT11 GND  → GND        (Pin 6)
  DHT11 DATA → 10kΩ pull-up resistor to VCC (recommended)
"""

import logging
import time

try:
    import adafruit_dht
    import board
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False

log = logging.getLogger(__name__)

# BCM pin → board.D mapping
_BCM_TO_BOARD = {
    4:  "D4",  17: "D17", 18: "D18", 27: "D27",
    22: "D22", 23: "D23", 24: "D24", 25: "D25",
    5:  "D5",  6:  "D6",  12: "D12", 13: "D13",
    19: "D19", 16: "D16", 26: "D26", 20: "D20", 21: "D21",
}


class DHT11Sensor:
    def __init__(self, pin: int = 4, max_retries: int = 3):
        self.pin = pin
        self.max_retries = max_retries
        self._device = None

        if not DHT_AVAILABLE:
            log.warning("adafruit_dht not installed — DHT11 will return SIMULATED data.")
            return

        board_pin_name = _BCM_TO_BOARD.get(pin)
        if board_pin_name is None:
            raise ValueError(f"BCM pin {pin} not found in board mapping.")

        board_pin = getattr(board, board_pin_name)
        self._device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
        log.info(f"DHT11 initialised on BCM GPIO{pin}.")

    def read(self):
        """
        Returns (temperature_c: float, humidity_pct: float)
        Returns (None, None) on failure.
        """
        if not DHT_AVAILABLE or self._device is None:
            # Simulated values for dev/testing without hardware
            import random
            temp = round(random.uniform(22.0, 30.0), 1)
            hum  = round(random.uniform(40.0, 70.0), 1)
            log.debug(f"[SIM] DHT11 → Temp={temp}°C  Humidity={hum}%")
            return temp, hum

        for attempt in range(1, self.max_retries + 1):
            try:
                temp = self._device.temperature
                hum  = self._device.humidity
                if temp is not None and hum is not None:
                    return float(temp), float(hum)
            except RuntimeError as e:
                log.debug(f"DHT11 read attempt {attempt}/{self.max_retries}: {e}")
                time.sleep(2)
            except Exception as e:
                log.error(f"DHT11 unexpected error: {e}")
                break

        return None, None

    def cleanup(self):
        if self._device:
            self._device.exit()
