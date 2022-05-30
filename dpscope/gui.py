import logging

from model.controller.helper.trigger import TriggerSource
from model.controller.helper.voltage_measure import VoltageResolution
from controller.app import DPScopeApp

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

if __name__ == "__main__":
    with DPScopeApp() as app:
        with app.model_get() as dpscope:
            # defaults
            dpscope.trigger.source = TriggerSource.auto
            dpscope.voltages.resolution = VoltageResolution.low

            app.show()
