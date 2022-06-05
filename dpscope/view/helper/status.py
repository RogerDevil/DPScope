"""
Controls how the status bars react to new result obtained by queue_getters.
"""
import logging

from common.timer import RateInTimeWindow
from view.helper.queue_observer import QueueObserverBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class MeasurementRateObserver(QueueObserverBase):
    """
    Rolling measurement of data acquisition rate.
    """
    t_window_ms = 200  # Time window over which to measurement data
    # acquisition rate.

    _rate_measurer = None

    _window = None  # Holds the window manager
    _view = None  # The view

    def __init__(self, view):
        """
        Instantiate with the window manager, and the status bar where
        information will be shown.

        Args:
            view (View): The view object.
        """
        self._window = view.window
        self._view = view
        self._rate_measurer = RateInTimeWindow(self.t_window_ms)

    def start(self):
        """
        Start the underlying data rate measurer.
        """
        self._rate_measurer.start()

    def stop(self):
        """
        Stop the underlying data rate measurer.
        """
        self._rate_measurer.stop()

    def window_get(self):
        """
        Returns:
            Tk: The window manager.
        """
        return self._window

    def update(self, data):
        """
        Display measurement rate to status area.

        Args:
            data: Measurement result.
        """
        self._rate_measurer.mark()
        rate = self._rate_measurer.rate_get()
        if rate is not None:
            self._view.status_2_update("Measurement rate: {} sample/s"
                                       "".format(rate))
