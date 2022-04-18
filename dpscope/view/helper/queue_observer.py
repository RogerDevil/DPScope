"""
Reacts to new result obtained by queue_getters.
"""
from abc import ABC, abstractmethod
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class QueueObserverBase(ABC):
    """
    API for reacting to getting new data from Queue.
    """
    @abstractmethod
    def window_get(self):
        """
        Returns:
            The window manager.
        """

    @abstractmethod
    def update(self, data):
        """
        Reacts to new data being retrieved.

        Args:
            data: Data retrieved from Queue.
        """
