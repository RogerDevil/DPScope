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


class DataArrayBase(list, ABC):
    """
    Holds list data and allows for in place edits.
    """
    _max_len = None  # Cache for max data length

    def __init__(self, in_data, *args, **kwargs):
        """
        Calls parents' instantiation, transfers the max length cache.
        """
        super().__init__(in_data, *args, **kwargs)
        self._max_len = getattr(in_data, '_max_len', 512)

    @property
    def data_len(self):
        """
        Returns:
            int: Length of stored data.
        """
        return len(self)

    @property
    def x(self):
        """
        Returns:
            range: Array range with same length as underlying data.
        """
        return range(len(self))

    @property
    @abstractmethod
    def max_len(self):
        """
        Returns:
            int: Max length or data.
        """

    @abstractmethod
    def _trim_data(self):
        """
        Trims the start of internal data till its length is smaller than the
        max length limit.
        """

    def append(self, new_data):
        """
        Append new data elements.

        Args:
            new_data: New data to be appended.
        """
        super().append(new_data)
        self._trim_data()


class InfiniteDataArray(DataArrayBase):
    """
    Data array of unrestricted length.
    """
    @property
    def max_len(self):
        """
        Returns:
            None: No max length
        """
        return None

    def _trim_data(self):
        """
        Null op for an infinite data length.
        """
        pass


class FiniteDataArray(DataArrayBase):
    """
    Data array of finite length.
    """
    @property
    def max_len(self):
        """
        Returns:
            int: Max length of data.
        """
        return self._max_len

    @max_len.setter
    def max_len(self, max_len):
        """
        Sets the max length of data, and trim if necessary.

        Args:
            max_len (int): max length of data.
        """
        self._max_len = max_len
        self._trim_data()

    def _trim_data(self):
        """
        Trims the start of internal data till its length is smaller than the
        max length limit.
        """
        while self.data_len > self.max_len:
            self.pop(0)


class ChannelData(object):
    """
    Holder for data from dual channel device such as the DPScope.
    """
    _ch1 = None
    _ch2 = None

    _trim_mode = InfiniteDataArray

    @property
    def ch1(self):
        """
        Returns:
            Channel 1 data.
        """
        return self._ch1

    @ch1.setter
    def ch1(self, ch1):
        """
        Sets channel 1 data.

        This attrib can only be set once. If it's a subtype of list,
        apply the data trimming, otherwise, set attrib as is.

        Args:
            ch1 (list, lines.Line2D): Object of appropriate data type.
        """
        self._ch1 = self._verify_and_trim_data('ch1', ch1)

    @property
    def ch2(self):
        """
        Returns:
            Channel 2 data.
        """
        return self._ch2

    @ch2.setter
    def ch2(self, ch2):
        """
        Sets channel 2 data.

        This attrib can only be set once. If it's a subtype of list,
        apply the data trimming, otherwise, set attrib as is.

        Args:
            ch2 (list, lines.Line2D): Object of appropriate data type.
        """
        self._ch2 = self._verify_and_trim_data('ch2', ch2)

    def _verify_and_trim_data(self, ch_name, in_data):
        """
        Check the selected attr does not already contain data, and set if so.

        Args:
            ch_name (str): The ch1 or ch2 attrib where data is to be written.
            in_data (list, lines.Line2D): Object of appropriate data type.

        Returns:
            DataArrayBase/lines.Line2D: Object of appropriate data type.
        """
        if getattr(self, ch_name) is not None:
            raise DataInputException("Cannot overwrite self.{} data: '{}'."
                                     "".format(ch_name,
                                               getattr(self, ch_name)))
        if isinstance(in_data, list):
            return self._trim_mode(in_data)
        else:
            return in_data

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
        return self.ch1.x

    @property
    def x2(self):
        """
        Returns:
            range: A range spanning same length as ch2.
        """
        return self.ch2.x

    @property
    def trim_mode(self):
        """
        Returns:
            class: The data trimming mode.
        """
        return self._trim_mode

    @trim_mode.setter
    def trim_mode(self, trim_mode):
        """
        Sets trim mode and applies to data.

        Raises exception if underlying data is not DataArrayBase type.

        Args:
            trim_mode (class): Class name, must be subclass of DataArrayBase.
        """
        if issubclass(trim_mode, DataArrayBase):
            raise TypeError("trim_mode must be a class name of subclass "
                            "DataArrayBase. Input value = '{}'"
                            "".format(trim_mode))
        if (not isinstance(self.ch1, DataArrayBase)
                or not isinstance(self.ch2, DataArrayBase)):
            raise AttributeError("Both ch1, ch2 data must be a subtype of "
                                 "DataArrayBase. ch1 type = '{}'; ch2 type = "
                                 "'{}'".format(self.ch1, self.ch2))
        self._trim_mode = trim_mode
        self._ch1 = self._trim_mode(self._ch1)
        self._ch2 = self._trim_mode(self._ch2)
