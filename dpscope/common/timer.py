"""
Measures loop rates, timers etc in standalone processes.
"""
import logging
from multiprocessing import Queue
from queue import Empty
from time import monotonic

from common.concurrent import ProcessLoop

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class RateInTimeWindow(object):
    """
    Measures rolling average rates in a rolling time window.
    """
    _time_window_ms = None
    _time_stamps = []  # A history of monotonic time stamps

    # The independent process that runs the timer mechanism shall run its
    # internal loop as quickly as possible.
    _loop_runner = ProcessLoop(0)

    _ping_signal = Queue()
    _rate_results = Queue()

    def __init__(self, time_window_ms):
        """
        Instantiate and set the rolling time window.

        Args:
            time_window_ms (int, float): The rolling time window over which
            the average is calculated.
        """
        self._time_window_ms = float(time_window_ms)

    @property
    def _time_window_s(self):
        """
        Returns:
            float: Time window in seconds.
        """
        return float(self._time_window_ms)/1000

    def _timer_c(self, ping_signal, rate_results):
        """
        The main timer implementation, to be looped in separate process.

        Args:
            ping_signal (multiprocessing.Queue): How the signal for marking
            time is sent into the timer loop.
            rate_results (multiprocessing.Queue): How the rate measurement
            results are returned to the caller.
        """
        t_now_s = monotonic()  # Time now in float

        try:
            ping_signal.get(timeout=0.1)
            # Trim timestamp buffer
            self._trim_timestamps_c(t_now_s - self._time_window_s)
            self._time_stamps.append(t_now_s)
            # Calculate 'samples/sec' results and put into results queue.
            rate_results.put_nowait(float(len(self._time_stamps))
                                    / self._time_window_s)
        except Empty:
            pass
        except ValueError:
            _LOGGER.warning("Cannot insert rate calculation result into "
                            "queue.")

    def _trim_timestamps_c(self, t_ref_s):
        """
        Trim the time stamp buffer.

        Assumes the timestamp buffer is already in temporal order. All time
        stamps earlier than the reference time is trimmed from start of buffer.

        Args:
            t_ref_s (float):  The reference time which defines the earliest
            time stamp after the trimming process.
        """
        if len(self._time_stamps) > 0:
            try:
                while self._time_stamps[0] < t_ref_s:
                    self._time_stamps.pop(0)
            except IndexError:
                _LOGGER.warning("Event rate lower than the defined rolling "
                                "time window of '{} ms'."
                                "".format(self._time_window_ms))

    def start(self):
        """
        Start the timer measuring process.
        """
        _LOGGER.info("Starting measurement rate characterisation.")
        self._loop_runner.start(self._timer_c,
                                (self._ping_signal, self._rate_results))

    def mark(self):
        """
        Record time period.
        """
        self._ping_signal.put_nowait(True)

    def rate_get(self):
        """
        Returns:
            float: The latest rate information (samples per second). None if
            no results are available yet.
        """
        rtn_rate = None
        while not self._rate_results.empty():
            rtn_rate = self._rate_results.get_nowait()
        return rtn_rate

    def stop(self):
        """
        Stop the timer measuring process and clear internal buffer.
        """
        _LOGGER.info("Ending measurement rate characterisation.")
        self._loop_runner.stop()
        self._time_stamps.clear()
