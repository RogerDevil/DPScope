from abc import ABC, abstractmethod
import logging

from controller.threaded_task import ThreadedTaskBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


dl = None


class Datalogger(ThreadedTaskBase):
    """
    Runs data logger in separate thread.
    """
    ch1 = []  # Channel 1 data
    ch2 = []  # Channel 2 data

    model = None  # Holds controller for DPScope.

    @property
    def x1(self):
        """
        Returns:
            range: A range spanning same length as ch1.
        """
        return range(len(self.ch1))

    @property
    def x2(self):
        """
        Returns:
            range: A range spanning same length as ch2.
        """
        return range(len(self.ch2))

    def __init__(self, view, interval, model):
        """
        Instantiate with a View, DPScope controller, and data acquisition
        period.
        
        Args:
            view (View): The app View.
            interval (int): Data acquisition period.
            model (DPScopeController): Controller for the DPScope
        """
        super().__init__(view, interval)
        self.model = model

    def task(self):
        """
        Read voltage from DPScope and plot in window.

        This task is run from an independent thread.
        """
        ch1, ch2 = self.model.volt_read()
        self.ch1.append(ch1)
        self.ch2.append(ch2)

        self.view.ch1.set_data(self.x1, self.ch1)
        self.view.ch2.set_data(self.x2, self.ch2)

        self.view.axes.relim()
        self.view.axes.autoscale_view()
        self.view.fig.canvas.draw()


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
        global dl
        dl = Datalogger(self._view, 100, self._model)
        dl.start()


class StopObserver(ViewObserverBase):
    """
    Reacting to Stop activation.
    """
    channel = "Acquisition.Stop"

    def update(self):
        _LOGGER.info("Stop button pressed")
        global dl
        if dl is not None:
            dl.stop()
            dl = None


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
