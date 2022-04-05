"""
Defines the basic View.
"""
import logging

# Set up logging
from view.observer import ObserverTypeException, ViewObserverBase

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class View(object):
    """
    The app view.

    This view should always be constructed using a Director and
    ViewBuilderBase.
    """
    window = None  # Holds the Tkinter window Tk()
    fig = None  # Holds the matplotlib figure Figure()

    plot_area = None
    acq_ctrl = None
    lvl_adj = None
    disp_ctrl = None
    vert_ctrl = None
    hor_ctrl = None
    trig_ctrl = None

    # Define different observer channels
    observers = {}

    # Holds user signals
    signals = {}

    def show(self):
        """
        Open app window.
        """
        self.window.mainloop()

    def observers_notify(self, ch):
        """
        Notify all event observers from a specified channel.

        Args:
            ch (str): Channel name. This must be from an existing key in the
            observer dictionary.
        """
        if ch not in self.observers:
            raise ObserverTypeException("Unknown triggering event '{}' "
                                        "requested. The allowed observers "
                                        "channels are: ''."
                                        "".format(ch, self.observers.keys()))
        for observer in self.observers[ch]:
            observer.update()

    def _verify_observer(self, observer):
        """
        Verify that the input object is a valid observer.

        Checks that the input object is a subclass of ViewObserverBase,
        and that the observer monitors a valid channel from the View.
        """
        if not isinstance(observer, ViewObserverBase):
            raise TypeError("The input type '{}' is not a subclass of "
                            "ViewObserverBase()".format(type(observer)))
        if observer.channel not in self.observers:
            raise ObserverTypeException("The observer class '{}' requested "
                                        "to observe channel '{}' which does "
                                        "not exist. Available channels from "
                                        "current view: '{}'"
                                        "".format(type(observer),
                                                  observer.name,
                                                  self.observers.keys()))

    def attach(self, observer):
        """
        Attach an observer to the observer queue.

        Args:
            observer (ViewObserverBase): The observer that reacts to events
            generated by the View.
        """
        self._verify_observer(observer)
        self.observers[observer.channel].add(observer)

    def detach(self, observer):
        """
        Detach an observer from the observer queue.

        Args:
            observer (ViewObserverBase): An observer that reacts to events
            generated by the View.
        """
        self._verify_observer(observer)
        self.observers[observer.channel].remove(observer)
