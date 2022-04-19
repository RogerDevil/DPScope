from abc import ABC, abstractmethod
from inspect import getmembers, isclass, isabstract
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


def observers_get_all():
    """
    Returns:
        list(ViewObserverBase): List of all view observer classes.
    """
    current_module = sys.modules[__name__]
    name_and_class = getmembers(current_module,
                                lambda m: isclass(m) and not isabstract(m))
    names = [name for name, cls in name_and_class
             if issubclass(cls, ViewObserverBase)]
    classes = [cls for _, cls in name_and_class
               if issubclass(cls, ViewObserverBase)]
    _LOGGER.info("Retrieved observers: {}".format(names))
    return classes


class ObserverTypeException(Exception):
    """
    Error in identifying the correct observer.
    """


class ViewObserverBase(ABC):
    """
    API for observing changes in GUI and reacting.
    """
    _view = None
    _model = None

    @property
    @abstractmethod
    def channel(self):
        """
        Returns:
            str: The observer channel name that the current instance should
            be attached to.
        """

    def __init__(self, view, model):
        """
        Instantiate with views and controller from MVC design pattern.

        Args:
            view (View): The app view.
            model (DPScopeController): The DPScope controller.
        """
        self._view = view
        self._model = model

    @abstractmethod
    def update(self):
        """
        React to View events.
        """


class StartObserver(ViewObserverBase):
    """
    Reacting to Start activation.
    """
    channel = "Acquisition.Start"

    def update(self):
        _LOGGER.info("Start button pressed")
        stream_period_ms = self._model.stream_period_get()
        self._view.voltage_getter.period_ms = stream_period_ms
        self._model.stream_voltages_start()
        self._view.voltage_getter.start()


class StopObserver(ViewObserverBase):
    """
    Reacting to Stop activation.
    """
    channel = "Acquisition.Stop"

    def update(self):
        _LOGGER.info("Stop button pressed")
        self._model.stream_voltages_stop()
        self._view.voltage_getter.stop()


class PollObserver(ViewObserverBase):
    """
    Reacting to Poll activation.
    """
    channel = "Acquisition.Poll"

    def update(self):
        _LOGGER.info("Poll button pressed")


class ClearObserver(ViewObserverBase):
    """
    Reacting to Clear activation.
    """
    channel = "Acquisition.Clear"

    def update(self):
        _LOGGER.info("Clear button pressed")
