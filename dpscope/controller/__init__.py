"""
Coordinates model and view interactions.

This is the controller from the MVC design pattern.
"""
import logging

from view.director import Director
from view.builder.standard import StandardViewBuilder
from view.observer import (PollObserver, StopObserver, ClearObserver,
                           StartObserver)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class DPScopeApp(object):
    """
    Entry point for the DPScope App.
    """
    _view = None  # Holds the view.
    _model = None  # Model for the DPScope.
    _observers = None  # Observers that react to View generated events.

    def __init__(self):
        """
        Builds a standard view.
        """
        view_builder = Director(StandardViewBuilder())
        view_builder.view_build()
        self._view = view_builder.view_get()
        self._observers = [observer(self._view, self)
                           for observer in [PollObserver, StopObserver,
                                            ClearObserver, StartObserver]]

    def __enter__(self):
        """
        Attaches observers to the View.

        Returns:
            DPScopeApp: This app instance.
        """
        for observer in self._observers:
            self._view.attach(observer)

        _LOGGER.debug("Attached observers: '{}'".format(self._view.observers))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Detaches observers from the View.
        """
        for observer in self._observers:
            self._view.detach(observer)

    def show(self):
        """
        Shows the app window.
        """
        self._view.show()
