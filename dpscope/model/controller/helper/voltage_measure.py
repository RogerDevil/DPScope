from enum import Enum
from functools import total_ordering
import logging
from queue import Queue

from concurrent import ThreadLoop
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
    _voltage_reader = None  # The object for performing single voltage read
    # measurement.
    _voltage_stream = Queue()  # Where the voltage results are placed.
    _thread_runner = None  # The controller for running function in
    # continuous loop.

    @property
    def voltage_stream(self):
        """
        Returns:
            Queue: Queue where voltage measurements are pumped into.
        """
        return self._voltage_stream

    def __init__(self, voltage_reader, period_ms=10):
        """
        Instantiate streamer with the voltage measurer.

        Args:
            voltage_reader (VoltageSingleRead): Single data point reader for
            measuring voltage.
            period_ms (int, float): Measurement period in msec.
        """
        self._thread_runner = ThreadLoop(period_ms)
        self._voltage_reader = voltage_reader

    def _voltage_acquire_c(self):
        """
        Periodically acquire voltages from scope.

        This method is run from within a thread. Measurements are put
        into the _voltage_stream Queue.
        """
        voltages = self._voltage_reader.read()
        self.voltage_stream.put(voltages)

    def _stream_queue_clear(self):
        """
        Removes any final data in the results stream.
        """
        from_buffer = []
        while not self._voltage_stream.empty():
            from_buffer.append(self._voltage_stream.get())
            self._voltage_stream.task_done()
        if len(from_buffer) > 0:
            _LOGGER.debug("Emptying results stream during clean up: '{}'"
                          "".format(from_buffer))

    def stream_queue_get(self):
        """
        Returns:
            queue.Queue: The Queue where voltages are streams to. Each
            element is in the form of [V_ch1, V_ch2], a list of floats for
            the 2 channels measured.
        """
        return self._voltage_stream

    def stream_period_get(self):
        """
        Returns:
            float: Streaming period.
        """
        return self._thread_runner.period_ms

    def voltage_reader_set(self, voltage_reader):
        """
        Refresh the voltage reader.

        Args:
            voltage_reader (VoltageSingleRead): The controller for acquiring a
            single voltage data point.
        """
        self._voltage_reader = voltage_reader

    def start(self):
        """
        Start the voltage measuring function in a loop in a thread.
        """
        self._thread_runner.start(self._voltage_acquire_c)

    def stop(self):
        """
        Stop the voltage measuring thread.
        """
        self._thread_runner.stop()
        self._stream_queue_clear()
