from abc import ABC, abstractmethod
from inspect import getmembers, isclass, isabstract
import logging
import sys

from view.helper.data import InfiniteDataArray, FiniteDataArray
from view.helper.plot_modes import TimePlot
from view.helper.status import MeasurementRateObserver

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


def observers_get_all():
    """
    Returns:
        list(ViewObserverBase): List of all view observer classes.
    """
    current_module = sys.modules[__name__]
    name_and_class = getmembers(current_module,
                                lambda m: isclass(m) and not isabstract(m))
    names = [name for name, cls in name_and_class
             if issubclass(cls, ViewObserverBase)]
    classes = [cls for _, cls in name_and_class
               if issubclass(cls, ViewObserverBase)]
    _LOGGER.info("Retrieved observers: {}".format(names))
    return classes


class ObserverTypeException(Exception):
    """
    Error in identifying the correct observer.
    """


class ViewObserverBase(ABC):
    """
    API for observing changes in GUI and reacting.
    """
    _view = None
    _model = None

    @property
    @abstractmethod
    def channel(self):
        """
        Returns:
            str: The observer channel name that the current instance should
            be attached to.
        """

    def __init__(self, view, model):
        """
        Instantiate with views and controller from MVC design pattern.

        Args:
            view (View): The app view.
            model (DPScopeController): The DPScope controller.
        """
        self._view = view
        self._model = model

    @abstractmethod
    def update(self):
        """
        React to View events.
        """


class WinCloseObserver(ViewObserverBase):
    """
    Reacting to main window being closed.
    """
    channel = "Window.close"

    def update(self):
        _LOGGER.info("Closing main window.")
        self._view.observers_notify("Acquisition.Stop")
        self._view.window.destroy()


class StartObserver(ViewObserverBase):
    """
    Reacting to Start activation.
    """
    channel = "Acquisition.Start"

    def update(self):
        _LOGGER.info("Start button pressed")
        stream_period_ms = self._model.stream_period_get()
        self._view.voltage_getter.period_ms = stream_period_ms
        self._view.plot_mode.buffer.clear()
        self._model.stream_voltages_start()
        self._view.voltage_getter.start()
        self._view.rate_observer = MeasurementRateObserver(self._view)


class StopObserver(ViewObserverBase):
    """
    Reacting to Stop activation.
    """
    channel = "Acquisition.Stop"

    def update(self):
        _LOGGER.info("Stop button pressed")
        self._model.stream_voltages_stop()
        self._view.voltage_getter.stop()
        self._view.rate_observer = None


class PollObserver(ViewObserverBase):
    """
    Reacting to Poll activation.
    """
    channel = "Acquisition.Poll"

    def update(self):
        _LOGGER.info("Poll button pressed")


class ClearObserver(ViewObserverBase):
    """
    Reacting to Clear activation.
    """
    channel = "Acquisition.Clear"

    def update(self):
        _LOGGER.info("Clear button pressed")
        self._view.plot_mode.buffer.clear()


class SampleModeObserver(ViewObserverBase):
    """
    Reacting to Scope/Datalog radio button activation.
    """
    channel = "Horizontal.sample_mode"

    def update(self):
        sample_mode = self._view.signals[self.channel].get()
        _LOGGER.info("'{}' selected.".format(sample_mode))
        if sample_mode == "Datalog mode":
            self._view.plot_mode.buffer_trim_mode = InfiniteDataArray
        elif sample_mode == "Scope mode":
            self._view.plot_mode.buffer_trim_mode = FiniteDataArray
        else:
            raise TypeError("Sample mode option must be one of 'Datalog "
                            "mode', 'Scope mode'. Requested mode: '{}'."
                            "".format(sample_mode))


class FftPlotModeObserver(ViewObserverBase):
    """
    Reacting to FFT checkbox being triggered.
    """
    channel = "Display.FFT"

    def update(self):
        fft_checkbox = self._view.signals[self.channel]
        xy_checkbox = self._view.signals["Display.X/Y"]

        if fft_checkbox.get():
            _LOGGER.info("Activating FFT mode.")
            xy_checkbox.set(False)
        else:
            _LOGGER.info("Activating time plot mode.")
            self._view.plot_mode = TimePlot(self._view)


class XyPlotModeObserver(ViewObserverBase):
    """
    Reacting to X/Y checkbox being triggered.
    """
    channel = "Display.X/Y"

    def update(self):
        xy_checkbox = self._view.signals[self.channel]
        fft_checkbox = self._view.signals["Display.FFT"]

        if xy_checkbox.get():
            _LOGGER.info("Activating X/Y mode.")
            fft_checkbox.set(False)
        else:
            _LOGGER.info("Activating time plot mode.")
            self._view.plot_mode = TimePlot(self._view)


class SampleSpeedObserver(ViewObserverBase):
    """
    Reacting to changes in sampling speed selection.
    """
    channel = "Horizontal.sample_speed"

    def update(self):
        selected_speed = self._view.signals[self.channel].get()
        acq_rate_ctrl = self._view.acq_rate
        _LOGGER.info("Selected acquisition speed '{}'".format(selected_speed))
        acq_rate_ctrl.selected_speed = selected_speed
        stream_period = acq_rate_ctrl.period_get()
        _LOGGER.info("Setting acquisition period as '{}' ms."
                     "".format(stream_period))
        self._model.stream_period_set(stream_period)
        # Reset plot
        self._view.observers_notify("Acquisition.Clear")


class GainCh1Observer(ViewObserverBase):
    """
    Reacts to changes in Channel 1 gain.
    """
    channel = "Vertical.ch1gain"

    def update(self):
        gain_settings = self._view.gain_options.ch1
        gain_settings.selected_gain = self._view.signals[self.channel].get()
        selected_gain = gain_settings.selected_gain
        _LOGGER.info("Ch1 gain '{}' selected from app."
                     "".format(selected_gain.display_str))
        self._model.gain_set(0, selected_gain.gain)
        self._model.pregain_set(0, selected_gain.pregain)


class GainCh2Observer(ViewObserverBase):
    """
    Reacts to changes in Channel 2 gain.
    """
    channel = "Vertical.ch2gain"

    def update(self):
        gain_settings = self._view.gain_options.ch2
        gain_settings.selected_gain = self._view.signals[self.channel].get()
        selected_gain = gain_settings.selected_gain
        _LOGGER.info("Ch2 gain '{}' selected from app."
                     "".format(selected_gain.display_str))
        self._model.gain_set(1, selected_gain.gain)
        self._model.pregain_set(1, selected_gain.pregain)
