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
    def __init__(self, pin=4, max_retries=3):
        self.pin = pin
        self.max_retries = max_retries
        self._device = None

        if not DHT_AVAILABLE:
            log.warning("adafruit_dht not installed — DHT11 simulated.")
            return

        board_pin_name = BCM_TO_BOARD.get(pin)
        if not board_pin_name:
            raise ValueError(f"BCM pin {pin} not in board mapping.")

        board_pin = getattr(board, board_pin_name)
        self._device = adafruit_dht.DHT11(board_pin, use_pulseio=False)
        log.info(f"DHT11 initialised on BCM GPIO{pin}.")

    def read(self):
        if not DHT_AVAILABLE or self._device is None:
            import random
            return round(random.uniform(22.0, 30.0), 1), round(random.uniform(40.0, 70.0), 1)

        for attempt in range(1, self.max_retries + 1):
            try:
                temp = self._device.temperature
                hum  = self._device.humidity
                if temp is not None and hum is not None:
                    # Sanity check — DHT11 range is 0-50°C, 20-90% RH
                    if 0 <= temp <= 50 and 20 <= hum <= 90:
                        return float(temp), float(hum)
                    else:
                        log.warning(f"DHT11 out-of-range: temp={temp} hum={hum}, retrying...")
            except RuntimeError as e:
                log.debug(f"DHT11 attempt {attempt}/{self.max_retries}: {e}")
                time.sleep(2)
            except Exception as e:
                log.error(f"DHT11 unexpected error: {e}")
                break

        return None, None

    def cleanup(self):
        if self._device:
            self._device.exit()
