"""
ds18b20_sensor.py
Reads temperature from DS18B20 via 1-Wire protocol.
No libraries needed — reads directly from Linux kernel sysfs.

Setup (one-time):
  sudo nano /boot/firmware/config.txt
  Add this line: dtoverlay=w1-gpio,gpiopin=4
  Save and reboot.

Wiring:
  DS18B20 Pin 1 (GND)  → GND        (RPi Pin 6)
  DS18B20 Pin 2 (DATA) → GPIO4      (RPi Pin 7)
  DS18B20 Pin 3 (VCC)  → 3.3V       (RPi Pin 1)
  + 4.7kΩ resistor between DATA and VCC
"""

import os
import glob
import time
import logging

log = logging.getLogger(__name__)

W1_BASE = "/sys/bus/w1/devices/"


class DS18B20Sensor:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self._device_path = None
        self._find_device()

    def _find_device(self):
        """Auto-detect the DS18B20 device file from sysfs."""
        try:
            # DS18B20 family code is 28-xxxxxxxxxxxx
            devices = glob.glob(W1_BASE + "28-*")
            if devices:
                self._device_path = devices[0] + "/w1_slave"
                log.info(f"DS18B20 found: {devices[0]}")
            else:
                log.error(
                    "DS18B20 not found in /sys/bus/w1/devices/. "
                    "Make sure 1-Wire is enabled:\n"
                    "  Add 'dtoverlay=w1-gpio,gpiopin=4' to /boot/firmware/config.txt\n"
                    "  Then reboot."
                )
        except Exception as e:
            log.error(f"DS18B20 device search failed: {e}")

    def _read_raw(self):
        """Read raw content from the 1-Wire sysfs file."""
        try:
            with open(self._device_path, "r") as f:
                return f.readlines()
        except Exception as e:
            log.debug(f"DS18B20 raw read error: {e}")
            return None

    def read(self):
        """
        Returns (temperature_c: float, temperature_f: float)
        Returns (None, None) on failure.
        """
        if self._device_path is None:
            # Simulated for dev without hardware
            import random
            t = round(random.uniform(24.0, 32.0), 2)
            f = round((t * 9/5) + 32, 2)
            log.debug(f"[SIM] DS18B20 → {t}°C")
            return t, f

        for attempt in range(1, self.max_retries + 1):
            lines = self._read_raw()
            if lines is None or len(lines) < 2:
                log.debug(f"DS18B20 attempt {attempt}: no data")
                time.sleep(1)
                continue

            # Line 1 ends with YES if CRC is valid
            if lines[0].strip().endswith("YES"):
                # Line 2 contains t=XXXXX (millidegrees)
                temp_pos = lines[1].find("t=")
                if temp_pos != -1:
                    temp_c = float(lines[1][temp_pos + 2:]) / 1000.0
                    temp_f = round((temp_c * 9/5) + 32, 2)
                    temp_c = round(temp_c, 2)
                    log.debug(f"DS18B20 → {temp_c}°C  {temp_f}°F")
                    return temp_c, temp_f
            else:
                log.debug(f"DS18B20 attempt {attempt}: CRC check failed, retrying...")
                time.sleep(1)

        log.warning("DS18B20 all retries failed.")
        return None, None

    def cleanup(self):
        pass  # No GPIO to release — kernel handles 1-Wire