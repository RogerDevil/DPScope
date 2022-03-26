"""
Defines a builder for the standard view.
"""
from abc import ABC, abstractmethod
from collections import namedtuple
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


# Captures the variable attributes of RadioButtonOptions
RadioBtnSubOptions = namedtuple("RadioBtnSubOptions",
                                ["text", "row", "column"])


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

    @classmethod
    def _make_name(cls, container, input_label):
        """
        Create signal name for a user input.

        Args:
            container (LabelFrame): The frame that holds the
            button/checkbox/any other user input type.
            input_label (str): The label for the user input.

        Returns:
            str: Signal name with the format {container_name}.{input_label}.
        """
        return "{}.{}".format(container["text"], input_label)

    def _add_button(self, container, label):
        """
        Add button to a particular frame in a view.

        Adds a corresponding observer channel.

        Args:
            container (LabelFrame): The frame that holds the buttons
            label (str): The button label.
        """
        signal_name = self._make_name(container, label)
        self._view.observers.update({signal_name: []})
        Button(container, text=label,
               command=
               lambda event: self._view.observers_notify(
                   signal_name)).pack(fill=X)

    def _add_checkbox(self, container, label, row, col=0, **grid_opt):
        """
        Adds checkbox in GUI.

        Also adds boolean variable types in View to store the checkbox values.
        Adds a corresponding observer channel.

        Args:
            container (LabelFrame): The frame that holds the checkbox.
            label (str): The checkbox label.
            row (int): Row position in frame (0-indexed).
            col (int): Column position in frame (0-indexed).
            grid_opt: Any other keyword arguments to pass into the grid
            layout method of the Checkbutton() UI element.
        """
        signal_name = self._make_name(container, label)
        self._view.signals.update({signal_name: BooleanVar()})
        self._view.observers.update({signal_name: []})
        Checkbutton(container, text=label,
                    variable=self._view.signals[signal_name],
                    command=
                    lambda event: self._view.observers_notify(signal_name)
                    ).grid(sticky=W, row=row, column=col, **grid_opt)

    def _add_option_menu(self, container, label, options, row, column,
                         **grid_opt):
        """
        Adds option menu in GUI.

        Also adds string variable type in View to store the chosen option.
        Adds a corresponding observer channel.

        Args:
            container (LabelFrame): The frame that holds the option menu.
            label (str): The option menu label. This is not actually shown
            in the GUI, but used under the hood to make the signal name.
            options (list(str)): The options shown in GUI.
            row (int): Row position in frame (0-indexed).
            column (int): Column position in frame (0-indexed).
            grid_opt: Any other keyword arguments to pass into the grid
            layout method of the OptionMenu() UI element.
        """
        signal_name = self._make_name(container, label)
        self._view.signals.update({signal_name: StringVar()})
        self._view.observers.update({signal_name: []})
        OptionMenu(container, self._view.signals[signal_name], *options,
                   command=
                   lambda event: self._view.observers_notify(signal_name)
                   ).grid(sticky=W, row=row, column=column, **grid_opt)
        self._view.signals[signal_name].set(options[0])

    def _add_radio_button(self, container, label, options):
        """
        Adds radio buttons belonging to the same subgroup to the GUI.

        Args:
            container (LabelFrame): The frame that holds the radio button
            group.
            label (str): The radio button label. This is not actually shown
            in the GUI, but used under the hood to make the signal name.
            options (list(RadioBtnSubOptions)): Defines the individual radio
            buttons within the group.
        """
        signal_name = self._make_name(container, label)
        self._view.signals.update({signal_name: StringVar()})
        self._view.observers.update({signal_name: []})
        for button in options:
            Radiobutton(container, text=button.text, variable=signal_name,
                        value=button.text,
                        command=
                        lambda event: self._view.observers_notify(signal_name)
                        ).grid(sticky=W, row=button.row, column=button.column)

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

    def build_display_controls(self):
        """
        Add channel select, xy, fft checkboxes.
        """
        self._view.disp_ctrl = LabelFrame(self._ctrl_right, text="Display")
        self._view.disp_ctrl.pack(fill=BOTH, expand=1)

        self._add_checkbox(self._view.disp_ctrl, "Ch1", 0)
        self._add_checkbox(self._view.disp_ctrl, "Ch2", 1)
        self._add_checkbox(self._view.disp_ctrl, "X/Y", 2)
        self._add_checkbox(self._view.disp_ctrl, "FFT", 3)

    def build_vertical_controls(self):
        """
        Adds voltage scaling dropdown list; radio buttons for probe
        attenuation.
        """
        self._view.vert_ctrl = LabelFrame(self._ctrl_right, text="Vertical")
        self._view.vert_ctrl.pack(fill=BOTH, expand=1)

        gains = ["1 V/div", "0.5 V/div", "0.2 V/div", "0.1 V/div", "50 mV/div",
                 "20 mV/div", "10 mV/div", "5 mV/div"]
        Label(self._view.vert_ctrl, text="Scale").grid(sticky=W, row=0,
                                                       column=1)
        Label(self._view.vert_ctrl,
              text="Probe Attenuation").grid(sticky=W, row=0, column=2,
                                             columnspan=2)
        Label(self._view.vert_ctrl, text="Ch1").grid(sticky=W, row=2, column=0)

        self._add_option_menu(self._view.vert_ctrl, "ch1gain", gains, 2, 1)
        ch1att_options = [RadioBtnSubOptions("1:1", 2, 2),
                          RadioBtnSubOptions("1:10", 2, 3)]
        self._add_radio_button(self._view.vert_ctrl, "ch1att", ch1att_options)

        Label(self._view.vert_ctrl, text="Ch2").grid(sticky=W, row=4, column=0)
        self._add_option_menu(self._view.vert_ctrl, "ch2gain", gains, 4, 1)
        ch2att_options = [RadioBtnSubOptions("1:1", 4, 2),
                          RadioBtnSubOptions("1:10", 4, 3)]
        self._add_radio_button(self._view.vert_ctrl, "ch2att", ch2att_options)

    def build_horizontal_controls(self):
        """
        Adds time resolution dropdown list, radio buttons for scope vs
        datalogging, checkbox for activating Pre-trigger mode, and slider
        for setting timing offset.
        """
        self._view.hor_ctrl = LabelFrame(self._ctrl_right, text="Horizontal")
        self._view.hor_ctrl.pack(fill=BOTH, expand=1)

        speeds = ["0.5 us/div", "1 us/div", "2 us/div", "5 us/div",
                  "10 us/div", "20 us/div", "50 us/div", "0.1 ms/div",
                  "0.2 ms/div", "0.5 ms/div", "1 ms/div", "2 ms/div",
                  "5 ms/div", "10 ms/div", "20 ms/div", "50 ms/div",
                  "0.1 s/div", "0.2 s/div", "0.5 s/div", "1 s/div"]
        sample_mode_options = [RadioBtnSubOptions("Scope mode", 0, 0),
                               RadioBtnSubOptions("Datalog mode", 0, 1)]
        self._add_radio_button(self._view.hor_ctrl, "sample_mode",
                               sample_mode_options)
        self._add_option_menu(self._view.hor_ctrl, "sample_speed", speeds,
                              1, 0, columnspan=2)
        self._add_checkbox(self._view.hor_ctrl, "Pretrigger mode", 2, 0,
                           columnspan=2)
        Scale(self._view.hor_ctrl, from_=0, to=100, length=200,
              orient=HORIZONTAL).grid(sticky=W, row=3, column=0, columnspan=2)
