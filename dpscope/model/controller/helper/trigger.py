import logging
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class TriggerSettingsException(Exception):
    """
    Bad trigger settings.
    """


class TriggerSource(Enum):
    """
    Trigger source types
    """
    auto = 0,
    ch1 = 1,
    ch2 = 2,
    LIMIT = 3


class TriggerPol(Enum):
    """
    Trigger polarisation
    """
    rising = 0,
    falling = 1
    LIMIT = 2


class TriggerSettings(object):
    """
    Manages trigger settings
    """
    _interface = None  # DPScope interface
    _source = None  # Trigger source
    _pol = None  # Trigger polarisation

    def __init__(self, interface):
        """
        Instantiate with DPScope interface.

        Args:
            interface (DPScopeInterface): The DPScope interface.
        """
        self._interface = interface

    @property
    def source(self):
        """
        Returns:
            TriggerSource: The trigger source. Sets to a default value of
            'auto' if it's not already set.
        """
        if self._source is None:
            self.source = TriggerSource.auto
        return self._source

    @source.setter
    def source(self, trigger_src):
        """
        Runs trigger source DPScope command.

        Args:
            trigger_src (TriggerSource): The trigger source
        """
        if trigger_src >= TriggerSource.LIMIT:
            raise TriggerSettingsException("Trigger source must be one of "
                                           "'auto', 'channel 1', 'channel "
                                           "2'. Requested trigger source = "
                                           "{}".format(trigger_src))
        self._interface.trig_source(trigger_src)
        self._source = trigger_src
        _LOGGER.info("Trigger source set to '{}'.".format(trigger_src))

    @property
    def pol(self):
        """
        Returns:
            TriggerPol: The trigger polarisation (rising or falling edge).
            Sets to a default value of 'rising' if it's not already set.
        """
        if self._pol is None:
            self.pol = TriggerPol.rising
        return self._pol

    @pol.setter
    def pol(self, trigger_pol):
        """
        Runs the trigger polarisation settings DPSope command.

        Args:
            trigger_pol (TriggerPol): The trigger polarisation.
        """
        if trigger_pol >= TriggerPol.LIMIT:
            raise TriggerSettingsException("Trigger polarisation must be one "
                                           "of 'rising', 'falling'. "
                                           "Requested trigger pol = {}"
                                           "".format(trigger_pol))
        self._interface.trig_pol(trigger_pol)
        self._pol = trigger_pol
        _LOGGER.info("Trigger polarisation set to '{}'."
                     "".format("rising" if trigger_pol == TriggerPol.rising
                               else "falling"))
