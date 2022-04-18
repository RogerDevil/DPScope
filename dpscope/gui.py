import logging

from portselect import get_port

import high
from model.controller.helper.trigger import TriggerSource
from model.controller.helper.voltage_measure import VoltageResolution
from controller import DPScopeApp


logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    with DPScopeApp() as app:
        pltr = high.Plotter(app._view.fig)
        pltr.scope = get_port(app._view.window)
        app.model_set(pltr.scope)

        with pltr.scope as dpscope:
            # defaults
            dpscope.trigger.source = TriggerSource.auto
            dpscope.voltages.resolution = VoltageResolution.low
            dpscope.gain_set(0, 0)
            dpscope.gain_set(1, 0)
            dpscope.pregain_set(0, 0)
            dpscope.pregain_set(1, 0)

            app.show()
