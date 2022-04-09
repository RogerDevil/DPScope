from enum import Enum
from functools import total_ordering
import logging
from threading import Thread
from time import time
from queue import Queue

from model.command import CommsException

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class ResolutionSettingsException(Exception):
    """
    Error with resolution settings.
    """


@total_ordering
class VoltageResolution(Enum):
    high = 0,  # high resolution, for a max of 1/4 of full range
    low = 1,  # 1/4 resolution, but can measure full range
    LIMIT = 2

    def __lt__(self, other):
        return self.value[0] < other.value


class VoltageSingleRead(object):
    """
    Supports a single data point voltage measurement.
    """
    _interface = None  # Holds DPScope interface
    _usb_voltage = None  # Cache for storing the calculated USB voltage
    gain = [None, None]  # Gain factor, to be set exclusively from external
    # code
    pregain = [None, None]  # Pregain factor, to be set exclusively from
    # external code
    _resolution = None  # ADC resolution

    def __init__(self, interface):
        """
        Instantiates with interface.

        Args:
            interface (DPScopeInterface): The DPScope interface.
        """
        self._interface = interface

    @property
    def resolution(self):
        """
        Returns:
            VoltageResolution: The ADC read resolution. Sets to default
            value of 'low' if it's not already set.
        """
        if self._resolution is None:
            self.resolution = VoltageResolution.low
        return self._resolution

    @resolution.setter
    def resolution(self, adc_res):
        """
        Runs the adcon_from DPScope command to set resolution.

        Args:
            adc_res (VoltageResolution): The ADC resolution.
        """
        if adc_res >= VoltageResolution.LIMIT:
            raise ResolutionSettingsException("ADC resolution can be 'low' "
                                              "or 'high'. Requested "
                                              "resolution is '{}'."
                                              "".format(adc_res))
        self._interface.adcon_from(adc_res.value[0])
        self._resolution = adc_res
        _LOGGER.info("ADC resolution set to '{}'.".format(adc_res))

    @property
    def usb(self):
        """
        Returns:
            float: The USB voltage (value is returned from cache if it's
            already been calculated).
        """
        if not self._usb_voltage:
            old_res = self.resolution
            dac_mV = 3000
            self.resolution = VoltageResolution.high
            # The Set DAC DPScope commands actually works different from
            # documentation.
            self._interface.set_dac(0, dac_mV)
            self._interface.set_dac(1, dac_mV)
            adcs = self._interface.measure_offset()
            real_dac = sum(adcs) / 2
            _LOGGER.info("Measured ADC offsets = '{}' for DAC output = '{}"
                         "mV'".format(adcs, dac_mV))
            self._interface.set_dac(0, 0)
            self._interface.set_dac(1, 0)
            nominal_dac = float(dac_mV)/1000 * (256 / 1.25)
            self._usb_voltage = 5. * (nominal_dac / real_dac)
            _LOGGER.info("Real USB voltage measured to be {}."
                         "".format(self._usb_voltage))
            if old_res != self.resolution:
                self.resolution = old_res

        return self._usb_voltage

    def read(self):
        """
        Read ADC values for both channels, and convert to voltage

        Returns:
            [float, float]: Channel 1, channel 2 voltages.
        """
        max_adc = 255  # Max possible value for the 8-bit ADC
        # Factor to take into account of pot at probe entry point.
        pot_ratio = 4
        # Maximum voltage range given the resolution setting.
        max_V = (self.usb if self.resolution == VoltageResolution.low
                 else self.usb / 4)
        adc_vals = self._interface.read_adc()
        if len(adc_vals) != 2:
            raise CommsException("There should be 2 ADC values returned by "
                                 "DPScope. Received '{}' instead."
                                 "".format(adc_vals))
        voltages = []
        for ch, adc in enumerate(adc_vals):
            multiplier = ((max_V * pot_ratio / max_adc)
                          * (self.pregain[ch]*self.gain[ch]))
            voltages.append(multiplier * adc)

        return voltages


class VoltageStreamer(object):
    """
    Streams voltage reading continuously into a thread queue.
    """
    _period_ms = None  # Measurement periodicity in msec.

    _voltage_reader = None  # The object for performing single voltage read
    # measurement.
    _t_next = None  # Target time of next results measurement.
    _voltage_stream = Queue()  # Where the voltage results are placed.
    _thread = None  # Thread in which continuous measurement is made.
    _cmd_queue = Queue()  # Submits commands to the measurement thread.

    @property
    def period_ms(self):
        """
        Returns:
            float: Measurement periodicity in msec.
        """
        return self._period_ms

    @period_ms.setter
    def period_ms(self, period_ms):
        """
        Sets measurement periodicity as float.
        """
        self._period_ms = float(period_ms)

    @property
    def voltage_stream(self):
        """
        Returns:
            Queue: Queue where voltage measurements are pumped into.
        """
        return self._voltage_stream

    def __init__(self, voltage_reader, period_ms=100):
        """
        Instantiate streamer with the voltage measurer.

        Args:
            voltage_reader (VoltageSingleRead): Single data point reader for
            measuring voltage.
            period_ms (int, flaot): Measurement period in msec.
        """
        self.period_ms = float(period_ms)
        self._voltage_reader = voltage_reader
        self._t_next = time()

    def _periodic_read_t(self):
        """
        Periodically acquire voltages from scope.

        This method should be run from within a thread. Measurements are put
        into the _voltage_stream Queue.
        """
        while True:
            if self._cmd_queue.get_nowait():
                _LOGGER.info("Suspending measurement thread.")
                break
            t_now = time()
            if t_now >= self._t_next:
                voltages = self._voltage_reader.read()
                self._voltage_stream.put(voltages)
                self._t_next += self.period_ms

    def start(self):
        """
        Start streaming voltage acquisition.
        """
        if self._thread is None:
            self._thread = Thread(target=self._periodic_read_t)
            self._thread.start()

    def stop(self):
        """
        Stop streaming voltage acquisition.
        """
        if self._thread is not None:
            self._cmd_queue.put(True)
            self._thread.join()
            self._thread = None
