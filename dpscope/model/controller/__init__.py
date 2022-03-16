import logging

from model.interface import DPScopeInterface
from model.controller.helper.voltage_measure import VoltageSingleRead
from helper.gain import Gain, PreGain
from helper.poll import make_poll, PollType
from helper.trigger import TriggerSettings

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
    voltages = None  # Single voltage measurer.
    _poll_controller = None  # Holds the controller for implementing polling.
    trigger = None  # Trigger settings manager.

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
        self._poll_controller = make_poll(poll_type)

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
        try:
            if self.voltages.gain[ch] is None:
                self.gain_set(ch, 1)
        except IndexError as ie:
            raise ie("Attempting to set gain on channel {}; Channel "
                     "specifier can only be (0, 1).".format(ch))
        return self.voltages.gain[ch]

    def gain_set(self, ch, gain):
        """
        Sets gain into DPScope.

        Also sets gain value in the voltage calculator.

        Args:
            ch (int): Channel number (0 or 1).
            gain (int): Gain factor for the requested channel.
        """
        gain_convert = Gain()
        gain_factor = gain_convert.code_to_val(self._interface.gain(ch, gain))
        try:
            self.voltages.gain[ch] = gain_factor
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
