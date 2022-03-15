"""
Helper functions and classes for DPScopeController.
"""
from collections import namedtuple
import logging
from abc import ABC, abstractmethod

from model.command import CommsException

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


Gain = namedtuple('Gain', ['code', 'val'])


class GainException(Exception):
    """
    Invalid gain setting.
    """


class GainBase(ABC):
    """
    Defines API for converting gains between codes and values.
    """
    @abstractmethod
    @property
    def set(self):
        """
        List of possible gains values and codes.
        """

    def code_for_val(self, val):
        """
        Looks for gain code for a given gain value.

        Args:
            val (int): Gain value.

        Returns:
            int: Gain code.
        """
        filtered_gain = [gain.code for gain in self.set if gain.val == val]
        if len(filtered_gain) != 1:
            raise GainException("Invalid gain value provided. Possible gain "
                                "values are '{}'. Requested gain value = {}."
                                "".format([gain.val for gain in self.set],
                                          val))
        return filtered_gain[0]

    def val_for_code(self, code):
        """
        Looks for gain value for a given gain code.

        Args:
            code (int): Gain code.

        Returns:
            int: Gain value.
        """
        filtered_gain = [gain.val for gain in self.set if gain.code == code]
        if len(filtered_gain) != 1:
            raise GainException("Invalid gain code provided. Possible gain "
                                "codes are '{}'. Requested gain code = {}."
                                "".format([gain.code for gain in self.set],
                                          code))
        return filtered_gain[0]


class Gain(GainBase):
    """
    Manages gain codes and values.
    """
    set = [Gain(code=0, val=1),
           Gain(code=1, val=2),
           Gain(code=2, val=4),
           Gain(code=3, val=5),
           Gain(code=4, val=8),
           Gain(code=5, val=10),
           Gain(code=6, val=16),
           Gain(code=7, val=32)
           ]


class PreGain(GainBase):
    """
    Manages pregain codes and values.
    """
    set = [Gain(code=0, val=1),
           Gain(code=1, val=10)
           ]


class VoltageCalc(object):
    """
    Helper for calculating voltages from raw readings.
    """
    _interface = None  # Holds DPScope interface
    _usb_voltage = None  # Cache for storing the calculated USB voltage
    gain = None  # Gain value, to be set exclusively from external code
    pregain = None  # Pregain value, to be set exclusively from external code

    def __init__(self, interface):
        """
        Instantiates with interface.

        Args:
            interface (DPScopeInterface): The DPScope interface.
        """
        self._interface = interface

    @property
    def usb_voltage(self):
        """
        Returns:
            float: The USB voltage (value is returned from cache if it's
            already been calculated).
        """
        if not self._usb_voltage:
            self._interface.adcon_from(0)
            self._interface.set_dac(0, 3000)
            self._interface.set_dac(1, 3000)
            real_dac = sum(self._interface.measure_offset()) / 2
            self._interface.set_dac(0, 0)
            self._interface.set_dac(1, 0)
            nominal_dac = 3. * (1023 / 5.)
            self._usb_voltage = 5. * (nominal_dac / real_dac)
            _LOGGER.info("Real USB voltage measured to be {}."
                         "".format(real_dac))

        return self._usb_voltage

    def read_volt(self):
        """
        Read ADC values for both channels, and convert to voltage

        Returns:
            [float, float]: Channel 1, channel 2 voltages.
        """
        adc_vals = self._interface.read_adc()
        multiplier = (self.USB_voltage/5.) * (20./256) * (self.pregain *
                                                          self.gain)
        voltages = [multiplier * adc for adc in adc_vals]
        if len(voltages) != 2:
            raise CommsException("There should be 2 voltages returned by "
                                 "DPScope. Received '{}' instead."
                                 "".format(voltages))
        return voltages
