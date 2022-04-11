"""
Controls concurrent tasks, by threads or multiprocess.
"""

from abc import ABC, abstractmethod
import logging
from queue import Queue, Empty
from threading import Thread
from time import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ConcurrentException(Exception):
    """
    General concurrency exception.
    """


class ConcurrentBase(ABC):
    """
    API for running concurrent tasks.
    """
    thread_process = None  # Holds the thread or multiprocess to run.

    _stop_command = Queue()  # Triggers termination of concurrent process.
    _period_ms = None  # Looping periodicity (in concurrent function) in msec.
    _t_next = None  # Target time of next concurrent function loop.

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

    def __init__(self, period_ms):
        """
        Instantiate and set the looping periodicity.

        Args:
            period_ms (int, float): Looping period in msec.
        """
        self.period_ms = float(period_ms)
        self._t_next = time()

    def _main_loop_c(self):
        """
        The main concurrency loop.
        """
        self._t_next = time()
        while True:
            try:
                if self._stop_command.get_nowait():
                    _LOGGER.info("Concurrent process terminating.")
                    self._stop_command.task_done()
                    break
            except Empty:
                pass
            t_now = time()
            if t_now >= self._t_next:
                self._looped_function_c()
                self._t_next += self.period_ms/1000

    @abstractmethod
    def _looped_function_c(self):
        """
        Defines the single iteration of function to be run.
        """

    def start(self):
        """
        Starts the concurrent process.
        """
        if self.thread_process is None:
            self.thread_process = Thread(target=self._main_loop_c)
            self.thread_process.start()
        else:
            raise ConcurrentException("Concurrent task already running. "
                                      "Stop task before re-initiating.")

    def stop(self):
        """
        Stops the concurrent process
        """
        if self.thread_process is not None:
            _LOGGER.info("Stopping concurrent task.")
            self._stop_command.put(True)
            self.thread_process.join()
            self.thread_process = None
            _LOGGER.info("Concurrent task stopped.")

    def close(self):
        """
        Closing queues.
        """
        if not self._stop_command.empty():
            raise ConcurrentException("Cannot end process - not stopping "
                                      "queue.")
        self._stop_command.join()
