"""
Coordinates model and view interactions.

This is the controller from the MVC design pattern.
"""
import logging

from controller.observer import observers_get_all
from model.controller import DPScopeController
from portselect import get_port
from view.builder.director import Director
from view.builder.standard import StandardViewBuilder

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

    def model_set(self, model):
        """
        Set model into app.

        Creates and attaches observers to View. Register results stream with
        the View.

        Args:
            model (DPScopeController): The DPScope controller.
        """
        self._model = model
        self._observers = [observer(self._view, self._model)
                           for observer in observers_get_all()]
        for observer in self._observers:
            self._view.attach(observer)
        _LOGGER.debug("Attached observers: '{}'".format(self._view.observers))

        self._view.results_stream_set(self._model.stream_queue_get())

    def model_get(self):
        """
        Returns:
            DPScopeController: The DPScope controller.
        """
        return self._model

    def __enter__(self):
        """
        Creates port selection window and initialise DPScope model.

        Returns:
            DPScopeApp: This app instance.
        """
        port_num = get_port(self._view.window)
        self.model_set(DPScopeController(port_num))
        self._view.initialiser.set()
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