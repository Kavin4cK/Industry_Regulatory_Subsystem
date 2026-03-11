"""
dht11_sensor.py
Direct DHT11 reader using lgpio — no Adafruit library needed.
Works on Debian Trixie / Raspberry Pi OS Bookworm and newer.

Wiring:
  DHT11 VCC  → 3.3V  (RPi Pin 1)
  DHT11 DATA → GPIO4 (RPi Pin 7)
  DHT11 GND  → GND   (RPi Pin 6)
"""

import time
import logging

log = logging.getLogger(__name__)

try:
    import lgpio
    LGPIO_AVAILABLE = True
except ImportError:
    LGPIO_AVAILABLE = False


class DHT11Sensor:
    def __init__(self, pin=4, max_retries=5):
        self.pin = pin
        self.max_retries = max_retries
        self._chip = None

        if not LGPIO_AVAILABLE:
            log.warning("lgpio not available — DHT11 will return simulated data.")
            return

        try:
            self._chip = lgpio.gpiochip_open(0)
            log.info(f"DHT11 initialised on BCM GPIO{pin} via lgpio.")
        except Exception as e:
            log.error(f"DHT11 lgpio init failed: {e}")
            self._chip = None

    def _read_raw(self):
        """
        Bit-bang the DHT11 protocol directly using lgpio.
        Returns (temperature, humidity) or (None, None) on failure.
        """
        chip = self._chip
        pin  = self.pin

        # ── Send start signal ──────────────────────────────────────────
        lgpio.gpio_claim_output(chip, pin, 1)
        time.sleep(0.05)          # let line settle high
        lgpio.gpio_write(chip, pin, 0)
        time.sleep(0.02)          # pull low for 20ms (DHT11 needs >18ms)
        lgpio.gpio_write(chip, pin, 1)
        time.sleep(0.00004)       # pull high, wait 40µs

        # ── Switch to input and wait for DHT11 response ───────────────
        lgpio.gpio_claim_input(chip, pin, lgpio.SET_PULL_UP)

        # Wait for DHT11 to pull line low (response start)
        timeout = time.time() + 0.1
        while lgpio.gpio_read(chip, pin) == 1:
            if time.time() > timeout:
                return None, None   # no response

        # Wait for DHT11 to pull line high
        timeout = time.time() + 0.1
        while lgpio.gpio_read(chip, pin) == 0:
            if time.time() > timeout:
                return None, None

        # Wait for DHT11 to pull line low again (data start)
        timeout = time.time() + 0.1
        while lgpio.gpio_read(chip, pin) == 1:
            if time.time() > timeout:
                return None, None

        # ── Read 40 bits ──────────────────────────────────────────────
        bits = []
        for _ in range(40):
            # Each bit starts with a ~50µs low pulse
            timeout = time.time() + 0.001
            while lgpio.gpio_read(chip, pin) == 0:
                if time.time() > timeout:
                    return None, None

            # Then a high pulse: ~26-28µs = 0, ~70µs = 1
            t_start = time.time()
            timeout  = time.time() + 0.001
            while lgpio.gpio_read(chip, pin) == 1:
                if time.time() > timeout:
                    return None, None
            pulse_len = time.time() - t_start

            bits.append(1 if pulse_len > 0.00005 else 0)   # 50µs threshold

        # ── Parse 40 bits into 5 bytes ────────────────────────────────
        data = []
        for i in range(5):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i * 8 + j]
            data.append(byte)

        # ── Checksum ──────────────────────────────────────────────────
        if data[4] != (data[0] + data[1] + data[2] + data[3]) & 0xFF:
            log.debug(f"DHT11 checksum failed: {data}")
            return None, None

        humidity    = data[0] + data[1] * 0.1
        temperature = data[2] + data[3] * 0.1

        return temperature, humidity

    def read(self):
        """
        Returns (temperature_c: float, humidity_pct: float)
        Returns (None, None) after all retries fail.
        """
        if not LGPIO_AVAILABLE or self._chip is None:
            import random
            t = round(random.uniform(24.0, 32.0), 1)
            h = round(random.uniform(50.0, 75.0), 1)
            log.debug(f"[SIM] DHT11 → {t}°C  {h}%")
            return t, h

        for attempt in range(1, self.max_retries + 1):
            try:
                temp, hum = self._read_raw()
                if temp is not None and hum is not None:
                    log.debug(f"DHT11 → {temp}°C  {hum}%")
                    return temp, hum
                else:
                    log.debug(f"DHT11 attempt {attempt}/{self.max_retries}: bad read, retrying...")
                    time.sleep(2)   # DHT11 needs at least 1s between reads
            except Exception as e:
                log.debug(f"DHT11 attempt {attempt}/{self.max_retries}: {e}")
                time.sleep(2)

        log.warning("DHT11 all retries failed — check wiring (VCC=Pin1, DATA=Pin7, GND=Pin6).")
        return None, None

    def cleanup(self):
        if self._chip is not None:
            try:
                lgpio.gpiochip_close(self._chip)
            except Exception:
                pass