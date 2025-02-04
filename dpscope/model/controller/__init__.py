import logging

from model.interface import DPScopeInterface
from model.controller.helper.voltage_measure import (VoltageSingleRead,
                                                     VoltageStreamer)
from model.controller.helper.gain import Gain, PreGain
from model.controller.helper.poll import make_poll, PollType
from model.controller.helper.trigger import TriggerSettings

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class DPScopeController(object):
    """
    High level controller for DPScope.

    This class provides high level access to the controller and delegates
    the low level interface with the DPScope to the DPScopeInterface()
    class. Data manipulation and other control logic is performed here to
    provide, for instance, scaled voltage readings to external code.
    """
    _interface = None  # Holds the interface to DPScope (sends serial
    # command to DPScope).
    _voltages = None  # Single voltage measurer.
    _poll_controller = None  # Holds the controller for implementing polling.
    trigger = None  # Trigger settings manager.
    _voltage_streamer = None  # Controls continuous measurements.

    @property
    def voltages(self):
        """
        Returns:
            VoltageSingleRead: Controller for acquiring single voltage
            measurement.
        """
        return self._voltages_private

    @voltages.setter
    def voltages(self, voltage_measurer):
        """
        Sets the voltage measurer, and the associated results streamer.

        Args:
            voltage_measurer (VoltageSingleRead): The controller for
            acquiring a single voltage data point.
        """
        self._voltages_private = voltage_measurer
        if self._voltage_streamer is None:
            self._voltage_streamer = VoltageStreamer(voltage_measurer)
        else:
            VoltageStreamer.voltage_reader_set(voltage_measurer)

    def __init__(self, port):
        """
        Instantiates DPScope controller.

        Args:
            port (int): Port num to create socket with.
        """
        self._interface = DPScopeInterface(port=port)
        self.voltages = VoltageSingleRead(self._interface)
        self.poll_type_set(PollType.Time)
        self.trigger = TriggerSettings(self._interface)

    def __enter__(self):
        """
        Opens connection to DPScope.

        Returns:
            This instance of controller
        """
        self._interface.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes connection.
        """
        self._interface.close()

    def poll_type_set(self, poll_type):
        """
        Sets the polling mode.

        Args:
            poll_type (PollType): Time or fft.
        """
        self._poll_controller = make_poll(poll_type, self._interface)

    def poll(self):
        """
        Make an instantaneous polling measurement and returns data.

        Returns:
            list(int), list(int): Channel 1, channel 2 results lists.
        """
        return self._poll_controller.do()

    def gain_get(self, ch):
        """
        Reads gain from DPScope.

        Updates the gain value in the voltage calculator if required.

        Args:
            ch (int): Channel number (0 or 1).

        Returns:
            int: Gain factor for the requested channel.
        """
        return self.voltages.gain[ch]

    def gain_set(self, ch, gain_factor):
        """
        Sets gain into DPScope.

        Also sets gain value in the voltage calculator.

        Args:
            ch (int): Channel number (0 or 1).
            gain_factor (int): Gain factor for the requested channel.
        """
        # Set gain factor value in logic
        gain_convert = Gain()
        gain_code = gain_convert.val_to_code(gain_factor)
        # Sends DPScope command for setting the gain. The DPScope MCU use
        # 1-indexed channel labelling.
        self._interface.gain(ch + 1, gain_code)
        try:
            self.voltages.gain[ch] = gain_factor
            _LOGGER.info("Setting channel '{}' gain code to '{}' (x{})"
                         "".format(ch, gain_code, gain_factor))
        except IndexError as ie:
            raise ie("Attempting to set gain on channel {}; Channel "
                     "specifier can only be (0, 1).".format(ch))

    def volt_read(self):
        """
        Read ADC values for both channels, and convert to voltage

        Returns:
            [float, float]: Channel 1, channel 2 voltages.
        """
        return self.voltages.read()

    def pregain_get(self, ch):
        """
        Reads pregain from DPScope.

        Updates the pregain value in the voltage calculator if required.

        Args:
            ch (int): Channel number (0 or 1).

        Returns:
            int: Pregain factor for the requested channel.
        """
        return self.voltages.pregain[ch]

    def pregain_set(self, ch, pregain_factor):
        """
        Sets pregain into DPScope.

        Also sets pregain value in the voltage calculator.

        Args:
            ch (int): Channel number (0 or 1).
            pregain_factor (int): Pregain factor for the requested channel.
        """
        # Set pregain code in logic.
        pregain_convert = PreGain()
        pregain_code = pregain_convert.val_to_code(pregain_factor)
        # Sends DPScope command to set pregain. The DPScope MCU use
        # 1-indexed channel labelling.
        self._interface.pre_gain(ch + 1, pregain_code)
        try:
            self.voltages.pregain[ch] = pregain_factor
            _LOGGER.info("Setting channel '{}' pre-gain code to '{}' (x{})"
                         "".format(ch, pregain_code, pregain_factor))
        except IndexError as ie:
            raise ie("Attempting to set gain on channel {}; Channel "
                     "specifier can only be (0, 1).".format(ch))

    def stream_voltages_start(self):
        """
        Start streaming voltages to Queue from a thread.
        """
        self._voltage_streamer.start()

    def stream_voltages_stop(self):
        """
        Stop streaming voltages to Queue.
        """
        self._voltage_streamer.stop()

    def stream_queue_get(self):
        """
        Returns:
            queue.Queue: The voltages results stream.
        """
        return self._voltage_streamer.stream_queue_get()

    def stream_period_get(self):
        """
        Returns:
            float: Results measuring periodicity.
        """
        return self._voltage_streamer.stream_period_get()

    def stream_period_set(self, period_ms):
        """
        Sets the results measuring periodicity.

        Args:
            period_ms (int, float): Measuring periodicity in ms.
        """
        self._voltage_streamer.stream_period_set(period_ms)
