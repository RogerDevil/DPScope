"""
Controls concurrent tasks, by threads or multiprocess.
"""

from abc import ABC, abstractmethod
import logging
import multiprocessing
from multiprocessing import Process
import queue
from queue import Empty
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

    _period_ms = None  # Looping periodicity (in concurrent function) in msec.
    _t_next = None  # Target time of next concurrent function loop.

    @property
    @abstractmethod
    def _stop_command(self):
        """
        Returns:
            queue.Queue, multiprocessing.Queue: The queue instance where the
            stop command is transmitted.
        """

    @property
    @abstractmethod
    def _thread_process_type(self):
        """
        Returns:
            cls: Thread or Multiprocess class.
        """

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

    def _main_loop_c(self, looped_func, args):
        """
        The main concurrency loop.

        Args:
            looped_func (func): The function being run as a loop in a
            separate thread of process.
            args (tuple): The function arguments.
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
                looped_func(*args)
                self._t_next += self.period_ms/1000

    def start(self, looped_func, args):
        """
        Starts the concurrent process.

        Args:
            looped_func (func): The function being run as a loop in a
            separate thread of process.
            args (tuple): The function arguments.
        """
        if self.thread_process is None:
            self.thread_process = \
                self._thread_process_type(target=self._main_loop_c,
                                          args=(looped_func, args))
            self.thread_process.start()
        else:
            raise ConcurrentException("Concurrent task already running. "
                                      "Stop task before re-initiating.")

    def stop(self):
        """
        Stops the concurrent process
        """
        if self.thread_process is not None:
            _LOGGER.debug("Stopping concurrent task.")
            self._stop_command.put(True)
            self.thread_process.join(0.5)
            while self.thread_process.is_alive():
                _LOGGER.debug("Process ending failed. Re-trying.")
                self.thread_process.join(0.5)
            self.thread_process = None
            _LOGGER.debug("Concurrent task stopped.")

    def close(self):
        """
        Closing queues.
        """
        if not self._stop_command.empty():
            raise ConcurrentException("Cannot end process - not stopping "
                                      "queue.")
        self._stop_command.join()


class ThreadLoop(ConcurrentBase):
    """
    Creates a thread to run in loops
    """
    _stop_command = queue.Queue()
    _thread_process_type = Thread


class ProcessLoop(ConcurrentBase):
    """
    Creates a thread to run in loops
    """
    _stop_command = multiprocessing.JoinableQueue()
    _thread_process_type = Process
