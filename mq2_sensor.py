"""
sensors/mq2_sensor.py
Reads gas concentration (LPG / Smoke / CO approx.) from MQ2 via MCP3008 ADC.

The MQ2 outputs an ANALOG voltage — the Raspberry Pi has no native ADC,
so we use an MCP3008 SPI ADC chip (cheap, ~$2).

Wiring — MCP3008 → Raspberry Pi (BCM):
  VDD  → 3.3V  (Pin 1)
  VREF → 3.3V  (Pin 1)
  AGND → GND   (Pin 6)
  CLK  → GPIO11 SCLK (Pin 23)
  DOUT → GPIO9  MISO (Pin 21)
  DIN  → GPIO10 MOSI (Pin 19)
  CS   → GPIO8  CE0  (Pin 24)
  DGND → GND   (Pin 6)

Wiring — MQ2 → MCP3008:
  VCC  → 5V
  GND  → GND
  AOUT → CH0 (or whichever channel set in config)
"""

import logging
import math

try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False

from config import Config

log = logging.getLogger(__name__)


class MQ2Sensor:
    def __init__(self, channel: int = 0):
        self.channel = channel
        self._spi = None

        if not SPI_AVAILABLE:
            log.warning("spidev not installed — MQ2 will return SIMULATED data.")
            return

        try:
            self._spi = spidev.SpiDev()
            self._spi.open(0, 0)          # Bus 0, Device 0 (CE0)
            self._spi.max_speed_hz = 1_350_000
            log.info(f"MQ2 (MCP3008) initialised on SPI CH{channel}.")
        except Exception as e:
            log.error(f"SPI init failed: {e}")
            self._spi = None

    # ── Internal helpers ───────────────────────────────

    def _read_adc(self) -> int:
        """Read raw 10-bit ADC value from MCP3008."""
        if self._spi is None:
            return 0
        adc = self._spi.xfer2([1, (8 + self.channel) << 4, 0])
        return ((adc[1] & 3) << 8) + adc[2]

    def _adc_to_voltage(self, raw: int) -> float:
        return (raw / Config.MQ2_ADC_MAX) * Config.MQ2_VCC

    def _voltage_to_rs(self, voltage: float) -> float:
        """Sensor resistance Rs from voltage divider formula."""
        if voltage == 0:
            return float("inf")
        return (Config.MQ2_VCC - voltage) / voltage * Config.MQ2_RL_VALUE

    def _rs_to_ppm(self, rs: float) -> float:
        """
        Approximate LPG/Smoke PPM using MQ2 datasheet curve.
        log(ppm) = m * log(Rs/Ro) + b   (log-log linear approximation)
        Coefficients below are for LPG curve; adjust for your gas target.
        """
        if rs <= 0 or Config.MQ2_RO_CLEAN_AIR <= 0:
            return 0.0
        ratio = rs / Config.MQ2_RO_CLEAN_AIR
        # LPG curve coefficients (from MQ2 datasheet graph)
        ppm = math.pow(10, (-2.3 * math.log10(ratio) + 2.9))
        return max(0.0, ppm)

    def _classify(self, ppm: float) -> str:
        if ppm < Config.MQ2_WARNING_PPM:
            return "Safe"
        elif ppm < Config.MQ2_DANGER_PPM:
            return "Warning"
        else:
            return "Danger"

    # ── Public API ─────────────────────────────────────

    def read(self):
        """
        Returns (raw_adc: int, gas_ppm: float, gas_level: str)
        """
        if not SPI_AVAILABLE or self._spi is None:
            # Simulated
            import random
            raw = random.randint(100, 600)
            ppm = random.uniform(50, 800)
            level = self._classify(ppm)
            log.debug(f"[SIM] MQ2 → raw={raw}  ppm={ppm:.1f}  level={level}")
            return raw, ppm, level

        raw     = self._read_adc()
        voltage = self._adc_to_voltage(raw)
        rs      = self._voltage_to_rs(voltage)
        ppm     = self._rs_to_ppm(rs)
        level   = self._classify(ppm)

        log.debug(f"MQ2 → raw={raw}  V={voltage:.3f}  Rs={rs:.2f}kΩ  ppm={ppm:.1f}  {level}")
        return raw, ppm, level

    def cleanup(self):
        if self._spi:
            self._spi.close()
