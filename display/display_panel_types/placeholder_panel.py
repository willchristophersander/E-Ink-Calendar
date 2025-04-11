# placeholder_panel.py
from PIL import Image, ImageDraw, ImageFont
# Set package context if running as main
__package__ = "display.display_panel_types"

# Use a relative import to load the base Panel class.
from .panel import Panel

PANEL_NAME = "Placeholder Panel"

class PlaceholderPanel(Panel):
    def __init__(self, panel_number: int = 0, weight: int = 1):
        super().__init__(weight)
        self.panel_number = panel_number

    def render(self, width: int, height: int) -> Image.Image:
        """
        Renders a placeholder panel as a white rectangle with an outline,
        and centers a label indicating the panel's number and that it is unconfigured.
        """
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            font = ImageFont.load_default()
        draw.rectangle([0, 0, width, height], outline="black", width=3)
        label = f"Panel {self.panel_number}: unconfigured"
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (width - text_w) // 2
        text_y = (height - text_h) // 2
        draw.text((text_x, text_y), label, fill="blue", font=font)
        return img

    def configure(self) -> None:
        """
        PlaceholderPanel requires no additional configuration.
        This method is implemented to satisfy the base class interface.
        """
        pass

PANEL_CLASS = PlaceholderPanel