import logging

from model.interface import DPScopeInterface
from helper import VoltageCalc, Gain, PreGain

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
    _voltage_calc = None  # Holds the converter from raw readings to voltages.

    _gain = None  # gain codes for 2 channels, stored as a list

    @property
    def usb_voltage(self):
        """
        Returns:
            float: USB voltage.
        """
        return self._voltage_calc.usb_voltage

    @property
    def gain(self):
        """
        Reads gain from DPScope.

        Returns:
            [int, int]: Channel 1, channel 2 gain values
        """

    @gain.setter
    def gain(self, gains):
        """
        Sets gain into DPScope.

        Also sets gain value in the voltage calculator.

        Args:
            gains ([int, int]): Gain for the 2 channels.
        """

    def __init__(self, port):
        """
        Instantiates DPScope controller.

        Args:
            port (int): Port num to create socket with.
        """
        self._interface = DPScopeInterface(port=port)
        self._voltage_calc = VoltageCalc(self._interface)
