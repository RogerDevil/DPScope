"""
Controls how gain options are shown in view, and converted into gain and
pre-gain settings for DPScope.
"""
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class GainSetting(object):
    """
    Contains information on an individual gain setting.
    """
    display_str = None  # Text to display in view
    pregain = None  # Pregain setting in circuit
    gain = None  # Gain setting in circuit
    mV_per_div = None  # mV per division in plot

    _nominal_vcc = 5.  # Nominal usb voltage
    _scale_down = 4.  # Scaling ratio from the first pot divider in circuit

    @property
    def cumulative_gain(self):
        """
        Returns:
            int: Total gain factor from combination of pregain and gain in
            the circuit.
        """
        return self.gain * self.pregain

    @property
    def voltage_max(self):
        """
        Returns:
            float: Max voltage that can be measured given the current settings.
        """
        return self._nominal_vcc * self._scale_down / self.cumulative_gain

    def __init__(self, display_str, mV_per_div, pregain, gain):
        """
        Instantiate settings for an individual gain option.

        Args:
            display_str (str): Display name of this gain setting in view.
            mV_per_div (int, float): mV per division in plot view.
            pregain (int): Pregain factor in circuit.
            gain (int): Gain factor in circuit.
        """
        self.display_str = display_str
        self.mV_per_div = float(mV_per_div)
        self.pregain = pregain
        self.gain = gain

    def add_to_gain_options(self, gain_manager):
        """
        Add the current gain setting to the gain manager.

        Args:
            gain_manager (GainOptions): The gain manager that holds all gain
            options.
        """
        gain_manager.gain_option_add(self)


class GainOptions(object):
    """
    Manages a set of gain options.
    """
    gain_options = {}  # Dictionary of gain options

    _selected_gain = None  # The selected gain option. Must be a key of the
    # gain_options dictionary.

    @property
    def gains(self):
        """
        Returns:
            list(str): gain options to be shown in view.
        """
        return list(self.gain_options)

    @property
    def selected_gain(self):
        """
        Returns:
            GainSetting: The selected gain setting.
        """
        return self.gain_options[self._selected_gain]

    @selected_gain.setter
    def selected_gain(self, selected_gain):
        """
        Sets the selected gain option.

        Args:
            selected_gain (str): The gain option, which must be a key from
            the internal gain_options dictionary.
        """
        if selected_gain not in self.gain_options:
            raise ValueError("Requested acquisition gain '{}' is not one of "
                             "'{}'".format(selected_gain,
                                           self.gain_options))
        self._selected_gain = selected_gain

    def __init__(self):
        """
        Creates gain options to be managed.
        """
        gain_options = [
            GainSetting("1 V/div", 1000, 1, 4),
            GainSetting("0.5 V/div", 500, 1, 8),
            GainSetting("0.2 V/div", 200, 10, 2),
            GainSetting("0.1 V/div", 100, 10, 4),
            GainSetting("50 mV/div", 50, 10, 8),
            GainSetting("20 mV/div", 20, 10, 16),
            GainSetting("10 mV/div", 10, 10, 32)
        ]

        for gain_option in gain_options:
            gain_option.add_to_gain_options(self)

    def gain_option_add(self, gain_option):
        """
        Add a gain option to this gain manager.

        Args:
            gain_option (GainSetting): One particular gain option.
        """
        self.gain_options.update({gain_option.display_str: gain_option})


class GainManager(object):
    """
    Gain settings manager for the dual channel device.
    """
    ch1 = None  # Channel 1 gain options
    ch2 = None  # Channel 2 gain options

    def __init__(self):
        """
        Creates gain options for the 2 channels.
        """
        self.ch1 = GainOptions()
        self.ch2 = GainOptions()
