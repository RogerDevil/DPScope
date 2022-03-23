"""
Defines the basic View.
"""
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class View(object):
    """
    The app view.
    """
    window = None
    fig = None

    plot_area = None
    acq_ctrl = None
    lvl_adj = None
    disp_ctrl = None
    vert_ctrl = None
    hor_ctrl = None
    trig_ctrl = None
