# weather_panel.py
from PIL import Image, ImageDraw, ImageFont
import os
__package__ = "display.display_panel_types"
from .panel import Panel  # Use a relative import to get the base class

PANEL_NAME = "Weather Panel"

class WeatherPanel(Panel):
    def __init__(self, weight: int = 1):
        super().__init__(weight)
        # Default configuration:
        self.location = "New York"
        self.show_icon = True
        self.forecast_offset = 0  # 0 means current weather, 1 means one hour forecast, etc.
        self.display_temp = True

    def configure(self) -> None:
        # Prompt user for weather panel configuration
        loc = input("Enter location for weather (e.g., city or zip): ").strip()
        if loc:
            self.location = loc
        icon_input = input("Display weather icon? (y/n, default y): ").strip().lower()
        self.show_icon = (icon_input in ("y", "yes") or icon_input == "")
        offset_input = input("Display current weather or forecast? (Enter 0 for current, or a number for hours ahead, default 0): ").strip()
        if offset_input.isdigit():
            self.forecast_offset = int(offset_input)
        else:
            self.forecast_offset = 0
        temp_input = input("Display temperature? (y/n, default y): ").strip().lower()
        self.display_temp = (temp_input in ("y", "yes") or temp_input == "")

    def fetch_weather(self) -> dict:
        """
        Dummy weather fetch function.
        In a real implementation, this method would query a weather API.
        Returns a dictionary with:
         - 'temperature': The temperature as a string
         - 'icon': The weather icon filename (expected to reside in data/weather_icons)
         - 'description': A short description (optional)
        """
        dummy_data = {
            "temperature": "72°F",
            "icon": "sunny.png",  # Ensure this file exists in data/weather_icons/
            "description": "Sunny"
        }
        return dummy_data

    def render(self, width: int, height: int):
        # Create a new white canvas for this panel.
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        # Fetch weather data (dummy for now)
        weather = self.fetch_weather()

        # Draw the location at the top.
        draw.text((10, 10), f"Location: {self.location}", fill="gray", font=font)

        # Draw the forecast time indication.
        if self.forecast_offset > 0:
            draw.text((10, height - 30), f"Forecast: {self.forecast_offset} hr(s) ahead", fill="gray", font=font)
        else:
            draw.text((10, height - 30), "Current weather", fill="gray", font=font)

        # If show_icon is enabled, load and display the weather icon.
        if self.show_icon:
            icon_file = weather.get("icon", "")
            if not os.path.isabs(icon_file):
                icon_file = os.path.join("data", "weather_icons", icon_file)
            try:
                icon_img = Image.open(icon_file)
                # Resize icon to occupy 50% of the panel's height.
                icon_size = int(height * 0.5)
                icon_img = icon_img.resize((icon_size, icon_size))
                # Paste the icon near the left-hand side, centered vertically.
                img.paste(icon_img, (10, (height - icon_size) // 2))
            except Exception as e:
                print(f"Error loading weather icon '{icon_file}': {e}")

        # If display_temp is enabled, draw the temperature.
        if self.display_temp:
            temp_text = weather.get("temperature", "N/A")
            x_offset = 70 if self.show_icon else 10
            # Draw the temperature in a prominent color.
            draw.text((x_offset, height // 2 - 10), f"Temp: {temp_text}", fill="black", font=font)

        return img

PANEL_CLASS = WeatherPanel

if __name__ == "__main__":
    wp = WeatherPanel()
    wp.configure()
    im = wp.render(400, 480)
    im.show()