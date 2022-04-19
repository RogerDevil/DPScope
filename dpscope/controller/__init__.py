"""
Coordinates model and view interactions.

This is the controller from the MVC design pattern.
"""
import logging

from view.builder.director import Director
from view.builder.standard import StandardViewBuilder
from controller.observer import observers_get_all

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

    def __enter__(self):
        """
        Returns:
            DPScopeApp: This app instance.
        """
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
