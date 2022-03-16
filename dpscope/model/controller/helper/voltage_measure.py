from enum import Enum
import logging

from model.command import CommsException

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class ResolutionSettingsException(Exception):
    """
    Error with resolution settings.
    """


class VoltageResolution(Enum):
    high = 0,  # high resolution, for a max of 1/4 of full range
    low = 1,  # 1/4 resolution, but can measure full range
    LIMIT = 2


class VoltageSingleRead(object):
    """
    Supports a single data point voltage measurement.
    """
    _interface = None  # Holds DPScope interface
    _usb_voltage = None  # Cache for storing the calculated USB voltage
    gain = [None, None]  # Gain value, to be set exclusively from external code
    pregain = [None, None]  # Pregain value, to be set exclusively from
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
        self._interface.adcon_from(adc_res)
        self._resolution = adc_res
        _LOGGER.info("ADC resolution set to '{}'."
                     "".format("low" if adc_res == VoltageResolution.low
                               else "high"))

    @property
    def usb(self):
        """
        Returns:
            float: The USB voltage (value is returned from cache if it's
            already been calculated).
        """
        if not self._usb_voltage:
            self.resolution = VoltageResolution.high
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

    def read(self):
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
