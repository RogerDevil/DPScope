"""
Structure for holding 2 channels data.
"""

import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class ChannelData(object):
    """
    Holder for data from dual channel device such as the DPScope.
    """
    ch1 = None
    ch2 = None

    def __init__(self, ch1, ch2):
        """
        Instantiates channel data with the appropriate data types.

        Args:
            ch1 (list, lines.Line2D): Object of appropriate data type
            ch2 (list, lines.Line2D): Object of appropriate data type
        """
        self.ch1 = ch1
        self.ch2 = ch2

    @property
    def x1(self):
        """
        Returns:
            range: A range spanning same length as ch1.
        """
        return range(len(self.ch1))

    @property
    def x2(self):
        """
        Returns:
            range: A range spanning same length as ch2.
        """
        return range(len(self.ch2))