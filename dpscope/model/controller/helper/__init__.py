"""
Helper functions and classes for DPScopeController.
"""
import logging

from model.command import CommsException

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class VoltageCalc(object):
    """
    Helper for calculating voltages from raw readings.
    """
    _interface = None  # Holds DPScope interface
    _usb_voltage = None  # Cache for storing the calculated USB voltage
    gain = [None, None]  # Gain value, to be set exclusively from external code
    pregain = [None, None]  # Pregain value, to be set exclusively from
    # external code

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
        if len(adc_vals) != 2:
            raise CommsException("There should be 2 ADC values returned by "
                                 "DPScope. Received '{}' instead."
                                 "".format(adc_vals))
        voltages = []
        for ch, adc in enumerate(adc_vals):
            multiplier = ((self.USB_voltage/5.)*(20./256)
                          * (self.pregain[ch]*self.gain[ch]))
            voltages.append(multiplier * adc)

        return voltages
