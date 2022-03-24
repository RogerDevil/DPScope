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

    _ctrl_panel = None
    _ctrl_left = None
    _ctrl_right = None

    def _add_button(self, container, label):
        """
        Add button to a particular frame in a view.

        Args:
            container (LabelFrame): The frame that holds the buttons
            label (str): The button label.
        """
        Button(container, text=label,
               command=
               lambda event: self._view.observers_notify(label)).pack(fill=X)

    def make_window(self):
        """
        Creates Tkinter window and embed a matplotlib Figure().
        """
        self._view.window = Tk()
        self._view.window.title(self.window_title)
        self._view.fig = Figure()

    def build_plot_area(self):
        """
        Add matplotlib plot and control panel spaces to window.
        """
        canvas = FigureCanvasTkAgg(self._view.fig, master=self._view.window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1, side=LEFT)
        self._ctrl_panel = Frame(self._view.window)
        self._ctrl_panel.pack(side=LEFT)
        self._ctrl_left = Frame(self._ctrl_panel)
        self._ctrl_left.pack(fill=BOTH, expand=1, side=LEFT)
        self._ctrl_right = Frame(self._ctrl_panel)
        self._ctrl_right.pack(fill=BOTH, expand=1, side=LEFT)

    def build_acquisition_controls(self):
        """
        Add start/stop etc. buttons.
        """
        self._view.acq_ctrl = LabelFrame(self._ctrl_left, text="Acquisition")
        self._view.acq_ctrl.pack(fill=BOTH, expand=1)

        self._add_button(self._view.acq_ctrl, "Start")
        self._add_button(self._view.acq_ctrl, "Poll")
        self._add_button(self._view.acq_ctrl, "Stop")
        self._add_button(self._view.acq_ctrl, "Clear")
        Label(self._view.acq_ctrl, text="Average").pack(fill=X)
        Spinbox(self._view.acq_ctrl, from_=1, to=100, width=4).pack(fill=X)

    def build_level_adjusts(self):
        """
        Add channel and trigger levels sliders.
        """
        self._view.lvl_adj = LabelFrame(self._ctrl_left, text="Levels")
        self._view.lvl_adj.pack(fill=BOTH, expand=1)

        Label(self._view.lvl_adj, text="Ch1").grid(sticky=E, row=0, column=0)
        Label(self._view.lvl_adj, text="Ch1").grid(sticky=E, row=0, column=1)
        Label(self._view.lvl_adj, text="Trg").grid(sticky=E, row=0, column=2)
        Scale(self._view.lvl_adj, from_=-100, to=100, length=300
              ).grid(sticky=E, row=1, column=0)
        Scale(self._view.lvl_adj, from_=-100, to=100, length=300
              ).grid(sticky=E, row=1, column=1)
        Scale(self._view.lvl_adj, from_=-100, to=100, length=300
              ).grid(sticky=E, row=1, column=2)
