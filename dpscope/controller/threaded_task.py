"""
Class for running threaded process.
"""
from abc import ABC, abstractmethod
import logging
from threading import Semaphore

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ThreadedTaskBase(ABC):
    """
    API for running a task in a separate thread.
    """
    view = None  # The View() object
    interval = None  # Refresh time interval (ms)

    @property
    def widget(self):
        """
        Returns:
            tkinter.Tk: Handle for app window from the associated view.
        """
        return self.view.window

    def __init__(self, view, interval):
        """
        Instantiate with a View and the refresh time interval.

        Args:
            view (View): View object.
            interval (int): The refresh time window.
        """
        self.view = view
        self.interval = interval
        self.timer = None
        self.s = Semaphore()

    @abstractmethod
    def task(self):
        """
        The task to run from the independent thread.
        """

    def start(self):
        """
        Periodically repeat run the task associated with this instance.
        """
        self.s.acquire()
        self.timer = self.widget.after(self.interval, self.start)
        self.s.release()
        self.task()

    def stop(self):
        """
        Stop the independent thread.
        """
        if self.timer:
            self.s.acquire()
            self.widget.after_cancel(self.timer)
            self.s.release()
