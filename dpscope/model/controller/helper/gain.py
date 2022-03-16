from collections import namedtuple
import logging
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


Gain = namedtuple('Gain', ['code', 'val'])


class GainException(Exception):
    """
    Invalid gain setting.
    """


class GainBase(ABC):
    """
    Defines API for converting gains between codes and values.
    """
    @abstractmethod
    @property
    def set(self):
        """
        List of possible gains values and codes.
        """

    def val_to_code(self, val):
        """
        Looks for gain code for a given gain value.

        Args:
            val (int): Gain value.

        Returns:
            int: Gain code.
        """
        filtered_gain = [gain.code for gain in self.set if gain.val == val]
        if len(filtered_gain) != 1:
            raise GainException("Invalid gain value provided. Possible gain "
                                "values are '{}'. Requested gain value = {}."
                                "".format([gain.val for gain in self.set],
                                          val))
        return filtered_gain[0]

    def code_to_val(self, code):
        """
        Looks for gain value for a given gain code.

        Args:
            code (int): Gain code.

        Returns:
            int: Gain value.
        """
        filtered_gain = [gain.val for gain in self.set if gain.code == code]
        if len(filtered_gain) != 1:
            raise GainException("Invalid gain code provided. Possible gain "
                                "codes are '{}'. Requested gain code = {}."
                                "".format([gain.code for gain in self.set],
                                          code))
        return filtered_gain[0]


class Gain(GainBase):
    """
    Manages gain codes and values.
    """
    set = [Gain(code=0, val=1),
           Gain(code=1, val=2),
           Gain(code=2, val=4),
           Gain(code=3, val=5),
           Gain(code=4, val=8),
           Gain(code=5, val=10),
           Gain(code=6, val=16),
           Gain(code=7, val=32)
           ]


class PreGain(GainBase):
    """
    Manages pregain codes and values.
    """
    set = [Gain(code=0, val=1),
           Gain(code=1, val=10)
           ]
