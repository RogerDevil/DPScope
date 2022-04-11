"""
Implements different plotting modes, through an independent process.
"""
from abc import ABC, abstractmethod
import logging
from queue import Empty
from threading import Lock

from concurrent import ConcurrentBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ChannelData(object):
    """
    Holder for data from dual channel device such as the DPScope.
    """
    ch1 = None
    ch2 = None

    def __init__(self, ch1, ch2):
        """
        Instantiates channel data with the appropriate data types.

        Args:
            ch1 (list, lines.Line2D): Object of appropriate data type
            ch2 (list, lines.Line2D): Object of appropriate data type
        """
        self.ch1 = ch1
        self.ch2 = ch2

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


class PlotModeBase(ConcurrentBase, ABC):
    """
    API for various plot modes. Responsible for displaying plots and
    provides mechanisms for reacting to start, stop, polling and display
    clearing.
    """
    buffer = ChannelData([], [])  # Results buffer for storing measurement
    # values.
    plot_data = None  # Holds data to be plotted

    show_ch1 = None  # Holds the GUI element that determines whether ch1 is
    # shown in plot.
    show_ch2 = None  # Holds the GUI element that determines whether ch2 is
    # shown in plot.

    _axes = None  # Holds the matplotlib axes.Axes() from within the Figure.
    _fig = None  # Holds the matplotlib figure figure.Figure()

    results_stream = None  # The Queue where measurement results are
    # streamed into.

    _buffer_lock = Lock()  # Protects against changes to the results buffer.
    _plot_lock = Lock()  # Protects against changes in plot data.

    def __init__(self, view, results_stream=None):
        """
        Sets up plot mode for streaming.

        Args:
            view (View): The app view.
            results_stream (Queue): The results stream.
        """
        super().__init__(period_ms=0)
        self.plot_data = ChannelData(view.ch1, view.ch2)
        self.show_ch1 = view.signals["Display.Ch1"]
        self.show_ch2 = view.signals["Display.Ch2"]
        self.results_stream = results_stream
        self._axes = view.axes
        self._fig = view.fig

    def _refresh_graphics_c(self):
        """
        Refresh plot area with the updated data.

        This is called from behind a thread.
        """
        self._axes.relim()
        self._axes.autoscale_view()
        self._fig.canvas.draw()

    def _looped_function_c(self):
        """
        Updates data and refresh plot. Overrides base class.
        """
        with self._buffer_lock:
            with self._plot_lock:
                self.refresh_data_c()
                self._refresh_graphics_c()

    @abstractmethod
    def refresh_data_c(self):
        """
        Extract data from stream queue into buffer, and define data to be
        drawn.

        This is called from behind a thread.
        """


class DataLogger(PlotModeBase):
    """
    Persistent plotting.
    """
    def refresh_data_c(self):
        """
        Extract voltages from queue, and show in plot.
        """
        try:
            v_ch1, v_ch2 = self.results_stream.get(timeout=0.2)
            self.buffer.ch1.append(v_ch1)
            self.buffer.ch2.append(v_ch2)
            self.plot_data.ch1.set_data(self.buffer.x1, self.buffer.ch1)
            self.plot_data.ch2.set_data(self.buffer.x2, self.buffer.ch2)
            self.results_stream.task_done()
        except Empty:
            pass
