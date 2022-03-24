"""
Defines the basic View.
"""
import logging

# Set up logging
from view.observer import ObserverTypeException

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class View(object):
    """
    The app view.

    This view should always be constructed using a Director and
    ViewBuilderBase.
    """
    window = None
    fig = None

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
