"""
dht11_sensor.py
Reads Temperature and Humidity from DHT11 using adafruit_dht + lgpio backend.

Wiring:
  DHT11 Pin 1 (VCC)  → 3.3V  (RPi Pin 1)
  DHT11 Pin 2 (DATA) → GPIO4 (RPi Pin 7)
  DHT11 Pin 3 (NC)   → not connected
  DHT11 Pin 4 (GND)  → GND   (RPi Pin 6)
  + 10kΩ resistor between DATA and VCC
"""

import time
import logging

try:
    import adafruit_dht
    import board
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False

log = logging.getLogger(__name__)

BCM_TO_BOARD = {
    4:"D4", 17:"D17", 18:"D18", 27:"D27", 22:"D22",
    23:"D23", 24:"D24", 25:"D25", 5:"D5", 6:"D6",
    12:"D12", 13:"D13", 19:"D19", 16:"D16", 26:"D26",
}


class DHT11Sensor:
    def __init__(self, pin=4, max_retries=5):
        self.pin = pin
        self.max_retries = max_retries
        self._device = None

        if not DHT_AVAILABLE:
            log.warning("adafruit_dht not installed — DHT11 will return simulated data.")
            return

        board_pin_name = BCM_TO_BOARD.get(pin)
        if not board_pin_name:
            raise ValueError(f"BCM pin {pin} not in board mapping.")

        board_pin = getattr(board, board_pin_name)
        # use_pulseio=False is required on modern Pi OS / lgpio backend
        self._device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
        log.info(f"DHT11 initialised on BCM GPIO{pin}.")

    def read(self):
        """
        Returns (temperature_c: float, humidity_pct: float)
        Returns (None, None) after all retries fail.
        """
        if not DHT_AVAILABLE or self._device is None:
            import random
            t = round(random.uniform(24.0, 32.0), 1)
            h = round(random.uniform(50.0, 75.0), 1)
            log.debug(f"[SIM] DHT11 → {t}°C  {h}%")
            return t, h

        for attempt in range(1, self.max_retries + 1):
            try:
                # Force a fresh read by reinitialising the pulse sequence
                temp = self._device.temperature
                hum  = self._device.humidity

                if temp is None or hum is None:
                    log.debug(f"DHT11 attempt {attempt}: got None, retrying...")
                    time.sleep(2)
                    continue

                # Accept any reading DHT11 can physically produce
                # DHT11 spec: 0–50°C, 20–95% RH
                # We accept slightly wider range in case of minor calibration offset
                if -5 <= temp <= 60 and 1 <= hum <= 100:
                    log.debug(f"DHT11 → {temp}°C  {hum}%")
                    return float(temp), float(hum)
                else:
                    log.warning(f"DHT11 attempt {attempt}: suspicious values temp={temp} hum={hum}")
                    time.sleep(2)

            except RuntimeError as e:
                log.debug(f"DHT11 attempt {attempt}/{self.max_retries}: {e}")
                time.sleep(2)
            except Exception as e:
                log.error(f"DHT11 unexpected error: {e}")
                time.sleep(2)

        log.warning("DHT11 all retries failed — check wiring.")
        return None, None

    def cleanup(self):
        if self._device:
            try:
                self._device.exit()
            except Exception:
                pass