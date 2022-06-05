"""
Defines the basic View.
"""
import logging

from controller.observer import ObserverTypeException, ViewObserverBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class View(object):
    """
    The app view.

    This view should always be constructed using a Director and
    ViewBuilderBase.
    """
    view_name = None  # Name of the view.
    window = None  # Holds the Tkinter window Tk()

    # Handles for matplotlib objects
    fig = None  # Holds the matplotlib figure figure.Figure()
    ax_ch1 = None  # Holds the matplotlib axes.Axes() from within the Figure.
    ax_ch2 = None  # Holds the matplotlib axes.Axes() from within the Figure.
    ch1 = None  # Holds the matplotlib lines.Line2D() for channel 1 plotted
    # data
    ch2 = None  # Holds the matplotlib lines.Line2D() for channel 2 plotted
    # data

    # Handles for tkinter objects holding different parts of the view window.
    plot_area = None
    acq_ctrl = None
    lvl_adj = None
    disp_ctrl = None
    vert_ctrl = None
    hor_ctrl = None
    trig_ctrl = None
    status_1 = None  # 1st text status display slot
    status_2 = None  # 2nd text status display slot

    # Define different observer channels
    observers = {}

    # Holds user signals
    signals = {}

    _plot_mode = None  # Holds the active plotting mode.
    voltage_getter = None  # Gets voltages from Queue.

    initialiser = None  # Manager for initialising this view.
    acq_rate = None  # Manager for controlling acquisition rates.
    gain_options = None  # Manager for controlling measurement gains.

    _rate_observer = None  # Measures data acquisition rate.

    def status_1_update(self, disp_txt):
        """
        Displays text in status slot 1.

        Args:
            disp_txt (str): Text to display.
        """
        self.status_1.config(text=disp_txt)

    def status_2_update(self, disp_txt):
        """
        Displays text in status slot 2.

        Args:
            disp_txt (str): Text to display.
        """
        self.status_2.config(text=disp_txt)

    @property
    def rate_observer(self):
        """
        Returns:
            MeasurementRateObserver: The measurement rate observer.
        """
        return self._rate_observer

    @rate_observer.setter
    def rate_observer(self, rate_observer):
        """
        Sets the rate observer and attach/detacg to the voltage getter.

        Args:
            rate_observer (MeasurementRateObserver, None): If provided with
            a valid MeasurementRateObserver instance, this is attached to
            the voltage getter. If None, any existing
            MeasurementRateObserver is detached from the voltage getter.
        """
        if rate_observer is None:
            if self._rate_observer is not None:
                self.voltage_getter.detach(self._rate_observer)
                self._rate_observer.stop()
                self._rate_observer = None
        else:
            if self._rate_observer is not None:
                self.voltage_getter.detach(self._rate_observer)
                self._rate_observer.stop()
            self._rate_observer = rate_observer
            self._rate_observer.start()
            self.voltage_getter.attach(self._rate_observer)

    @property
    def plot_mode(self):
        """
        Returns:
            PlotModeBase: The active plot mode.
        """
        return self._plot_mode

    @plot_mode.setter
    def plot_mode(self, plot_mode):
        """
        Sets the plot mode, amend the results_observers set and
        attach/detach to any existing voltage_getter accordingly.

        Args:
            plot_mode (PlotModeBase): Can be a valid plot mode, or None.
        """
        if self._plot_mode is not None:
            self.voltage_getter.detach(self._plot_mode)
        self.voltage_getter.attach(plot_mode)
        self._plot_mode = plot_mode

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

    def results_stream_set(self, results_stream):
        """
        Registers the results stream with the view.

        Args:
            results_stream (Queue): The Queue where the results from the model
            is piped over.
        """
        self.voltage_getter.queue_set(results_stream)
