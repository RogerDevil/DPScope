from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ObserverTypeException(Exception):
    """
    Error in identifying the correct observer.
    """


class ViewObserverBase(ABC):
    """
    API for observing changes in GUI and reacting.
    """
    _view = None
    _controller = None

    @property
    @abstractmethod
    def channel(self):
        """
        Returns:
            str: The observer channel name that the current instance should
            be attached to.
        """

    def __init__(self, view, controller):
        """
        Instantiate with views and controller from MVC design pattern.

        Args:
            view (View): The app view.
            controller: The app controller.
        """
        self._view = view
        self._controller = controller

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


class StopObserver(ViewObserverBase):
    """
    Reacting to Stop activation.
    """
    channel = "Acquisition.Stop"

    def update(self):
        _LOGGER.info("Stop button pressed")


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
        _LOGGER.info("Clear bcsutton pressed")
