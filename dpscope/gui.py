import logging

from portselect import get_port

import high
from model.controller.helper.trigger import TriggerSource
from model.controller.helper.voltage_measure import VoltageResolution
from controller import DPScopeApp


logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class Datalogger(high.Task):
    def __init__(self, widget, interval):
        high.Task.__init__(self, widget, interval)
        self.ch1 = []
        self.ch2 = []

    def task(self):
        data = ch1, ch2 = pltr.volt_read()
        self.ch1.append(ch1)
        self.ch2.append(ch2)
        pltr.plot([], self.ch1, [], self.ch2)

stopfn = lambda: None


with DPScopeApp() as app:
    def start():
        global stopfn
        if "Datalog mode" in app._view.signals['Horizontal.sample_mode']:
            dl = Datalogger(app._view.window, 100)
            stopfn = dl.stop
            dl.start()

    def stop():
        stopfn()

    pltr = high.Plotter(app._view.fig)
    pltr.scope = get_port(app._view.window)

    with pltr.scope as dpscope:
        # defaults
        dpscope.trigger.source = TriggerSource.auto
        dpscope.voltages.resolution = VoltageResolution.low
        dpscope.gain_set(0, 0)
        dpscope.gain_set(1, 0)
        dpscope.pregain_set(0, 0)
        dpscope.pregain_set(1, 0)

        app.show()
