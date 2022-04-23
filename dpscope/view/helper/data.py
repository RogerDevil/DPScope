"""
Structure for holding 2 channels data.
"""
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class DataInputException(Exception):
    """
    Exception in storing data.
    """


class DataArrayBase(ABC):
    """
    Holds list data and allows for in place edits.
    """
    _data = None  # Holds the underlying list.

    @property
    def data(self):
        """
        Returns:
            list: The stored data.
        """
        return self._data

    @data.setter
    def data(self, data):
        """
        Store data in internal buffer.

        Args:
            data (list): Data to be stored.
        """
        self._input_data_verify(data)
        self._data = data

    @property
    def data_len(self):
        """
        Returns:
            int: Length of stored data.
        """
        return len(self._data)

    @property
    def x(self):
        """
        Returns:
            range: Array range with same length as underlying data.
        """
        return range(len(self._data))

    @abstractmethod
    def append(self, new_data):
        """
        Append new data elements.

        Args:
            new_data: New data to be appended.
        """

    def clear(self):
        """
        Clears the underlying data.
        """
        self._data.clear()

    def _input_data_verify(self, input):
        """
        Ensures input is a list and does not overwrite pre-existing data.

        Args:
            input (list): The input to be checked.
        """
        if not isinstance(input, list):
            raise TypeError("Input data must be list type: '{}' detected."
                            "".format(type(input)))
        if self._data is not None:
            raise DataInputException("Cannot overwrite existing data: '{}'."
                                     "".format(self._data))


class InfiniteDataArray(DataArrayBase):
    """
    Data array of unrestricted length.
    """
    def append(self, new_data):
        """
        Append new data elements.

        Args:
            new_data: New data to be appended.
        """
        self._data.append(new_data)


class FiniteDataArray(DataArrayBase):
    """
    Data array of finite length.
    """
    max_len = None  # Max length of data

    def __init__(self, max_len=512):
        """
        Instantiate data buffer.

        Args:
            max_len (int): Maximum length of underlying data.
        """
        self.max_len = max_len

    def _trim_data(self):
        """
        Trims the start of internal data till its length is smaller than the
        max length limit.
        """
        while self.data_len > self.max_len:
            self._data.pop(0)

    @data.setter
    def data(self, data):
        """
        Store data in internal buffer.

        If the length of data to be set exceeds the maximum allowed length,
        trim from the start till length is within limit. This is done as an
        in-place modification.

        Args:
            data (list): Data to be stored.
        """
        self._input_data_verify(data)
        self._data = data
        self._trim_data()

    def append(self, new_data):
        """
        Append new data elements.

        Args:
            new_data: New data to be appended.
        """
        self._data.append(new_data)
        self._trim_data()


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