"""
mq2_sensor.py
Reads gas detection from MQ2 using Digital Output (DO) pin only.
No ADC or SPI needed.

Wiring:
  MQ2 VCC → 5V       (RPi Pin 2)
  MQ2 GND → GND      (RPi Pin 6)
  MQ2 DO  → GPIO17   (RPi Pin 11)
  MQ2 AO  → NOT connected
"""

import logging

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

log = logging.getLogger(__name__)


class MQ2Sensor:
    def __init__(self, pin=17):
        self.pin = pin
        self._setup_done = False

        if not GPIO_AVAILABLE:
            log.warning("RPi.GPIO not available — MQ2 will return simulated data.")
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self._setup_done = True
            log.info(f"MQ2 (Digital) initialised on BCM GPIO{self.pin}.")
        except Exception as e:
            log.error(f"MQ2 GPIO setup failed: {e}")

    def read(self):
        """
        Returns (gas_detected: bool, status: str, do_raw: int)
        DO pin is active-LOW: 0 = gas detected, 1 = clear
        """
        if not GPIO_AVAILABLE or not self._setup_done:
            import random
            do_raw = 0 if random.random() < 0.15 else 1
            gas_detected = (do_raw == 0)
            status = "Gas Detected" if gas_detected else "Clear"
            log.debug(f"[SIM] MQ2 → {status}")
            return gas_detected, status, do_raw

        try:
            do_raw = GPIO.input(self.pin)
            gas_detected = (do_raw == GPIO.LOW)
            status = "Gas Detected" if gas_detected else "Clear"
            log.debug(f"MQ2 → DO={do_raw} → {status}")
            return gas_detected, status, do_raw
        except Exception as e:
            log.error(f"MQ2 read error: {e}")
            return False, "Read Error", -1

    def cleanup(self):
        if GPIO_AVAILABLE and self._setup_done:
            try:
                GPIO.cleanup(self.pin)
            except Exception:
                pass