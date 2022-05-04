"""
Controls how acquistion rates are shown in view, and how it affects actual
measurements.
"""
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class AcquisitionRate(object):
    """
    Controls how acquisition rate options are shown in the View and sets the
    actual acquisition rate for continuous measurements.
    """
    reads_per_div = 10  # Number of data reads per division in view plot

    # Acquisition rate options. dict key controls what gets shown in the view
    # option menu. dict value is the time period spanned across a division
    # in the data plot.
    _rate_options = {"100 ms/div": 100,
                     "200 ms/div": 200,
                     "500 ms/div": 500,
                     "1 s/div": 1000}
    _selected_speed = None
    _period_ms = None

    @property
    def speeds(self):
        """
        Returns:
            list(str): List of all possible acquisition rate options
            displayed in view.
        """
        return list(self._rate_options)

    @property
    def selected_speed(self):
        """
        Returns:
            str: The current selected speed option.
        """
        return self._selected_speed

    @selected_speed.setter
    def selected_speed(self, selected_speed):
        """
        Sets the selected speed option and calculate measurement period.

        Args:
            selected_speed (str): The acquisition speed requested.
        """
        if selected_speed not in self._rate_options:
            raise ValueError("Requested acquisition rate '{}' is not one of "
                             "'{}'".format(selected_speed,
                                           self.selected_speed))
        self._selected_speed = selected_speed
        self._period_ms = \
            float(self._rate_options[self._selected_speed])/self.reads_per_div

    def period_get(self):
        """
        Returns:
            float: Time period between individual data acquisitions, in ms.
        """
        return self._period_ms
