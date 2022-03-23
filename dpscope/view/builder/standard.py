"""
Defines a builder for the standard view.
"""
from abc import ABC, abstractmethod
import logging

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import (Tk, Frame, LabelFrame, BOTH, Button, Label, Spinbox, X,
                     LEFT, Scale, Checkbutton, BooleanVar, W, StringVar,
                     OptionMenu, Radiobutton, HORIZONTAL, IntVar, E)

from view.base import View

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


matplotlib.use('TkAgg')


class ViewBuilderBase(ABC):
    """
    API for View constructors.
    """
    _view = None  # Holds the View object

    @abstractmethod
    def make_window(self):
        """
        Creates the app window/frame.
        """

    @abstractmethod
    def build_plot_area(self):
        """
        Build the main display plot area.
        """

    @abstractmethod
    def build_acquisition_controls(self):
        """
        Build start/stop etc. controls
        """

    @abstractmethod
    def build_level_adjusts(self):
        """
        Build level adjusters. e.g. channel and trigger levels
        """

    @abstractmethod
    def build_display_controls(self):
        """
        Build display controls. e.g. channel selections, fft
        """

    @abstractmethod
    def build_vertical_controls(self):
        """
        Build vertical scaling controls.
        """

    @abstractmethod
    def build_horizontal_controls(self):
        """
        Build horizontal timing controls.
        """

    @abstractmethod
    def build_trigger_controls(self):
        """
        Build trigger controls.
        """

    def make_view(self):
        """
        Instantiates a View.
        """
        self._view = View()

    def get_view(self):
        """
        Returns:
            View: The app View.
        """
        return self._view


class StandardViewBuilder(ViewBuilderBase):
    """
    Constructor for the standard view.
    """
    window_title = "DPScope"

    def make_window(self):
        """
        Creates Tkinter window and embed a matplotlib Figure().
        """
        self._view.window = Tk()
        self._view.window.title(self.window_title)
        self._view.fig = Figure()

    def build_plot_area(self):
        """
        Add matplotlib plot to the Figure().
        """
        canvas = FigureCanvasTkAgg(self._view.fig, master=self._view.window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1, side=LEFT)

    def build_acquisition_controls(self):
        """
        Add start/stop etc. buttons.
        """

