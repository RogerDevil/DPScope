"""
Run tasks in loop.
"""
import logging

from tkinter import Tk

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class QueueStartError(Exception):
    """
    Error in running the queue getter.
    """


class TkQueueGetter(object):
    """
    Allows Tkinter widget to interact with an asynchronous queue.

    Tkinter does not interact well with python thread or multiprocessing
    processes. It runs its own internal loop, which should never be blocked
    by any blocking calls, which prevents, for instance, the use of an
    unbounded Queue.get() method.

    This class gets around it by periodically polling intensively polling
    around a nominal time interval.
    """
    _period_ms = None  # Nominal polling period (msec).
    _queue = None  # The queue where this instance gets from.
    _observers = set()  # observers that react to new results obtained from
    # the queue.

    _after = None  # The "after" timer ID to be used for cancelling the
    # scheduled event.
    _window = None  # The Tkinter window manager.

    @property
    def period_ms(self):
        """
        Returns:
            float: Looping periodicity in concurrent function in msec.
        """
        return self._period_ms

    @period_ms.setter
    def period_ms(self, period_ms):
        """
        Sets looping periodicity in concurrent function as float.
        """
        self._period_ms = float(period_ms)

    @property
    def window(self):
        """
        Returns:
            Tk: The Tkinter window manager.
        """
        if self._window is None:
            raise ValueError("A TKinter window manager must be set before it "
                             "can be read.")
        return self._window

    @window.setter
    def window(self, window):
        """
        Sets the Tkinter window manager.

        This is a one-time setting operation. The first time it's set,
        it must be a Tkinter Tk() object, if any subsequent attempt were
        made to set it to some other value, it will be refused.

        Args:
            window (Tk): The Tkinter window manager.
        """
        if not isinstance(window, Tk):
            raise TypeError("'window' attribute must be set with a Tkinter "
                            "Tk instance. '{}' is set instead."
                            "".format(type(window)))
        if self._window is None:
            self._window = window
        elif self._window is not window:
            raise ValueError("An existing Tkinter window {} already exist. "
                             "Cannot be replaced by a different Tkinter "
                             "window {}.".format(self._window, window))

    def __init__(self, queue=None, period_ms=None):
        """
        Instantiate with the basic parameters.

        Args:
            queue (Queue): The thread or multiprocessing queue where we get
            data from.
            period_ms (int, float): The nominal period where results are
            expected to appear in the queue.
        """
        if queue is not None:
            self._queue = queue
        if period_ms is not None:
            self.period_ms = period_ms

    def attach(self, observer):
        """
        Attach an observer that reacts to every new measurement value
        received from the results stream.

        Args:
            observer: The observer.
        """
        self.window = observer.window_get()
        self._observers.add(observer)

    def detach(self, observer):
        """
        Remove a particular observer from the observer queue.

        Args:
            observer: The observer. Must be one already attached to this
            instance.
        """
        self._observers.remove(observer)

    def start(self):
        """
        Start periodically get objects from queue, and call on the attached
        observers to react to each obtained object.
        """
        if self._queue.empty():
            self._after = self.window.after(int(self.period_ms/10),
                                            self.start)
        else:  # Data is available in the Queue.
            self._after = self.window.after(int(0.8*self.period_ms),
                                            self.start)
            data_buffer = []
            while not self._queue.empty():
                data_buffer.append(self._queue.get(0))
            for data in data_buffer:
                for observer in self._observers:
                    observer.update(data)

    def stop(self):
        """
        Stop responding to new results from the queue.
        """
        if self._after:
            self.window.after_cancel(self._after)
            self._after = None
            _LOGGER.debug("Stopped monitoring for data from queue.")

    def queue_set(self, queue):
        """
        Sets the Queue which is monitored by this instance.

        Args:
            queue (Queue): The Queue being monitored.
        """
        self._queue = queue
