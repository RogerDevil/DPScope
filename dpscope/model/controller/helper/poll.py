"""
Implements various polling modes.
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class InvalidPollType(Exception):
    """
    Invalid Polling type requested.
    """


class PollType(Enum):
    Time = 0
    Fft = 1
    LIMIT = 2


def make_poll(poll_type, interface):
    """
    Instantiate a results polling controller.

    Args:
        poll_type (PollType): Specifies a time or freq domain polling.
        interface (DPScopeInterface): DPScope interface, for the Poll class
        to work with.

    Returns:
        PollBase: an instance of time or freq Polling controller.
    """
    if poll_type == PollType.Time:
        rtn_poll = PollTime(interface)
    elif poll_type == PollType.Fft:
        rtn_poll = PollFft(interface)
    else:
        raise InvalidPollType("Requested polling type must be smaller < {}; "
                              "the requested poll type is {}"
                              "".format(PollType.LIMIT, poll_type))

    return rtn_poll


class PollBase(ABC):
    """
    API of polling modes.
    """
    interface = None
    raadback_bytes = 205  # 205 is the max num of bytes that can be returned
    # by the DPScope's readback command.

    def __init__(self, interface):
        """
        Instantiate with DPScope interface.

        Args:
            interface (DPScopeInterface): The DPScope interface.
        """
        self.interface = interface

    @abstractmethod
    def _arm(self):
        """
        Sends the relevant DPScope arm command to take measurement (stored
        in DPScope's buffer).
        """

    def do(self):
        """
        Takes measurement, returns results, and send abort signal to DPScope.

        Returns:
            list(int), list(int): Channel 1, channel 2 results lists.
        """
        self._arm()
        data = None
        while not data:
            data = self.interface.read_back(self.raadback_bytes)
        self.interface.abort()
        return self._parse(data)

    @classmethod
    @abstractmethod
    def _parse(cls, data):
        """
        Parses bytes data returned from the DPScope's readback command.

        This is expected to be dependent on whether the data acquisition is
        done via the arm, or arm_fft DPScope command.

        Args:
            data: Data from readback command.

        Returns:
            list(int), list(int): Channel 1, channel 2 results list.
        """


class PollTime(PollBase):
    """
    Implements results polling in time domain.
    """
    def _arm(self):
        """
        Sends the arm DPScope command.
        """
        self.interface.arm(0)

    @classmethod
    def _parse(cls, data):
        """
        Parses bytes data returned from the readback command.

        Args:
            data (bytes): Data returned from the readback command.

        Returns:
            list(int), list(int): Channel 1, channel 2 results.
        """
        # Strips first byte
        data = data[1:]
        # bytes data is arranged in form:
        # CH1 val1, CH2 val1, CH1 val2, CH2 val2, CH1 val3, CH2 val3,...
        return data[0::2], data[1::2]


class PollFft(PollBase):
    """
    Implements results polling in freq domain.
    """
    def _arm(self):
        """
        Sends the arm_fft DPScope command.
        """
        self.interface.arm_fft()

    @classmethod
    def _parse(cls, data):
        """
        Parses bytes data returned from the readback command.

        Args:
            data (bytes): Data returned from the readback command.

        Returns:
            list(int), list(int): Channel 1, channel 2 results.
        """
        # Strips first byte
        data = data[1:]
        # bytes data is arranged in form:
        # CH1 val1, CH1 val2, CH1 val3,..., CH2 val1, CH2 val2, CH2 val3,...
        split_index = len(data)/2 + 1
        return data[0:split_index], data[split_index:]
