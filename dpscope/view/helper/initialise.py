"""
Helper to initialise different views.
"""
from abc import ABC, abstractmethod
from inspect import getmembers, isclass, isabstract
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


def initialiser_get(view):
    """
    Gets the requested initialiser.

    Args:
        view (View): The view instance to be initialised.

    Returns:
        ViewInitialiserBase: An instance of the view initialiser.
    """
    current_module = sys.modules[__name__]
    name_and_class = getmembers(current_module,
                                lambda m: isclass(m) and not isabstract(m)
                                and issubclass(m, ViewInitialiserBase)
                                and m.view_type == view.view_name)
    if len(name_and_class) != 1:
        raise InitialiserTypeException("Expect a unique initialiser for the "
                                       "requested view type (''). Found: '{}'"
                                       "".format(view.view_name,
                                                 name_and_class))
    _, cls = name_and_class[0]
    return cls(view)


class InitialiserTypeException(Exception):
    """
    Cannot identify correct initialiser.
    """


class ViewInitialiserBase(ABC):
    """
    API for view initialisers.
    """
    _view = None

    @property
    @abstractmethod
    def view_type(self):
        """
        Returns:
            str: The view type associated with the current Initialiser.
        """

    def __init__(self, view):
        """
        Instantiate with a view instance.

        Args:
            view (View): The view to be initialised.
        """
        self._view = view

    @abstractmethod
    def set(self):
        """
        Perform initialisation sequence.
        """


class StandardInitialiser(ViewInitialiserBase):
    """
    Initialises the standard view.
    """
    view_type = "Standard"

    def _signal_and_notify(self, ch_name, value):
        """
        Sets a View element and notifies relevant observers.

        Args:
            ch_name (str): The channel name associated with the GUI element.
            value: The value to set the GUI element to.
        """
        self._view.signals[ch_name].set(value)
        for observer in self._view.observers[ch_name]:
            observer.update()

    def set(self):
        """
        Initialises the standard view.
        """
        _LOGGER.info("Initialising '{}' view.".format(self.view_type))
        # Set channel selection
        self._signal_and_notify("Display.Ch1", True)
        self._signal_and_notify("Display.Ch2", True)

        self._signal_and_notify("Horizontal.sample_mode", "Datalog mode")
