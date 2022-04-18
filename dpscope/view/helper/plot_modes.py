"""
Implements different plotting modes, through an independent process.
"""
from abc import ABC
import logging

from view.helper.data import ChannelData
from view.helper.queue_observer import QueueObserverBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class PlotModeBase(QueueObserverBase, ABC):
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
    _window = None  # The window manager.

    def __init__(self, view):
        """
        Sets up plot mode for streaming.

        Args:
            view (View): The app view.
        """
        self.plot_data = ChannelData(view.ch1, view.ch2)
        self.show_ch1 = view.signals["Display.Ch1"]
        self.show_ch2 = view.signals["Display.Ch2"]
        self._axes = view.axes
        self._fig = view.fig
        self._window = view.window

    def _refresh_graphics_c(self):
        """
        Refresh plot area with the updated data.

        This is called from behind a thread.
        """
        self._axes.relim()
        self._axes.autoscale_view()
        self._fig.canvas.draw()

    def window_get(self):
        """
        Returns:
            The window manager.
        """
        return self._window


class DataLogger(PlotModeBase):
    """
    Persistent plotting.
    """
    def update(self, results):
        """
        Updates internal buffer and plot data with the latest results.

        Args:
            results (float, float): Tuple of ch1, ch2 results.
        """
        v_ch1, v_ch2 = results
        print(v_ch1)
        print(v_ch2)
        self.buffer.ch1.append(v_ch1)
        self.buffer.ch2.append(v_ch2)
        self.plot_data.ch1.set_data(self.buffer.x1, self.buffer.ch1)
        self.plot_data.ch2.set_data(self.buffer.x2, self.buffer.ch2)
        self._refresh_graphics_c()
