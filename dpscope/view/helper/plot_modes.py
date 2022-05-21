"""
Implements different plotting modes, through an independent process.
"""
from abc import ABC
import logging

from numpy import arange

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

    gain_ch1 = None  # The selected gain option for ch1
    gain_ch2 = None  # The selected gain option for ch2

    _axes = None  # Holds the matplotlib axes.Axes() from within the Figure.
    _fig = None  # Holds the matplotlib figure figure.Figure()
    _window = None  # The window manager.

    @property
    def buffer_trim_mode(self):
        """
        Returns:
            class: Class name of the buffer data trimming mode.
        """
        return self.buffer.trim_mode

    @buffer_trim_mode.setter
    def buffer_trim_mode(self, trim_mode):
        """
        Sets the buffer trimming mode.

        Args:
            trim_mode (class): Class (uninstantiated) representing the data
            trimming mode.
        """
        self.buffer.trim_mode = trim_mode

    @property
    def buffer_max_len(self):
        """
        Returns:
            int: Max length of the data buffer array. None if using a plot
            mode that has infinite buffer length.
        """
        return self.buffer.ch1.max_len

    def __init__(self, view):
        """
        Sets up plot mode for streaming.

        Args:
            view (View): The app view.
        """
        self.plot_data = ChannelData(view.ch1, view.ch2)
        self.show_ch1 = view.signals["Display.Ch1"]
        self.show_ch2 = view.signals["Display.Ch2"]
        self.gain_ch1 = view.gain_options.ch1
        self.gain_ch2 = view.gain_options.ch2
        self._axes = view.axes
        self._fig = view.fig
        self._window = view.window

    def _refresh_graphics_c(self, xticks=[], yticks=[]):
        """
        Refresh plot area with the updated data.

        This is called from behind a thread.

        Args:
            xticks (list): Defines x axis tick marks in plot.
            yticks (np.array): Defines y axis tick marks in plot.
        """
        self._axes.relim()
        self._axes.autoscale_view()
        self._axes.set_xticks(xticks)
        self._axes.set_yticks(yticks)
        self._axes.grid(len(xticks) != 0)
        self._fig.canvas.draw()

    def window_get(self):
        """
        Returns:
            The window manager.
        """
        return self._window


class TimePlot(PlotModeBase):
    """
    Persistent plotting.
    """
    def _yticks_make(self):
        """
        Returns:
            np.array(float): y-axis tick marks.
        """
        show_ch1 = self.show_ch1.get()
        show_ch2 = self.show_ch2.get()
        if show_ch1 and show_ch2:
            smallest_gain = self.gain_ch1.selected_gain if (
                self.gain_ch1.selected_gain <
                self.gain_ch2.selected_gain) else self.gain_ch2.selected_gain
        elif show_ch2:
            smallest_gain = self.gain_ch2.selected_gain
        else:
            smallest_gain = self.gain_ch1.selected_gain
        v_per_div = float(smallest_gain.mV_per_div)/1000
        yticks = arange(-v_per_div,
                        float(smallest_gain.voltage_max) + 0.1 * v_per_div,
                        v_per_div)
        return yticks

    def update(self, results):
        """
        Updates internal buffer and plot data with the latest results.

        Args:
            results (float, float): Tuple of ch1, ch2 results.
        """
        v_ch1, v_ch2 = results
        self.buffer.ch1.append(v_ch1)
        self.buffer.ch2.append(v_ch2)
        if self.show_ch1.get():
            self.plot_data.ch1.set_data(self.buffer.x1, self.buffer.ch1)
        else:
            self.plot_data.ch1.set_data([], [])
        if self.show_ch2.get():
            self.plot_data.ch2.set_data(self.buffer.x2, self.buffer.ch2)
        else:
            self.plot_data.ch2.set_data([], [])
        xticks = (list(range(0, self.buffer_max_len, 10))
                  if self.buffer_max_len is not None else [])
        self._refresh_graphics_c(xticks, self._yticks_make())
