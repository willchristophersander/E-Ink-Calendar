"""
panel.py

Defines the base Panel class that all display panel types should inherit from.
Each subclass must implement the render() method to produce an image, and can optionally override configure().
"""

__all__ = ["Panel"]

from typing import Any

class Panel:
    def __init__(self, weight: int = 1) -> None:
        self.weight: int = weight

    def render(self, width: int, height: int) -> Any:
        """
        Render the panel into an image of size (width x height).
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement render()")

    def configure(self) -> None:
        """
        Optionally configure the panel (e.g., prompt the user for settings).
        """
        pass