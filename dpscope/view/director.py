"""
Directs the construction of app Views.
"""
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class Director(object):
    """
    Constructs and returns the app View.
    """
    _builder = None  # Holds the View builder.

    def __init__(self, view_builder):
        """
        Instantiate with a view builder.

        Args:
            view_builder (ViewBuilderBase): Builder that constructs any kind
            of view.
        """
        self._builder = view_builder

    def build_view(self):
        """
        Calls the view building sequence.
        """
        self._builder.make_view()
        self._builder.make_window()
        self._builder.build_plot_area()
        self._builder.build_acquisition_controls()
        self._builder.build_level_adjusts()
        self._builder.build_display_controls()
        self._builder.build_vertical_controls()
        self._builder.build_horizontal_controls()
        self._builder.build_trigger_controls()

    def get_view(self):
        """
        Returns:
            view.base.View: The specific app View, as defined by the View builder.
        """
        return self._builder.get_view()
