# iCloud_calendar_panel.py
from PIL import Image, ImageDraw, ImageFont
import math
import random
import lorem
__package__ = "display.display_panel_types"
from .panel import Panel  # relative import of base class

PANEL_NAME = "iCloud Calendar Panel"

class iCloudCalendarPanel(Panel):
    def __init__(self, weight: int = 1):
        super().__init__(weight)
        self.days_allocated = 7
        self.rows = 2

    def configure(self) -> None:
        try:
            self.days_allocated = int(input("Enter number of days for iCloud Calendar Panel: "))
            self.rows = int(input("Enter number of rows for iCloud Calendar Panel: "))
        except Exception as e:
            print("Invalid input, using default values.")

    def render(self, width, height):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        cols = math.ceil(self.days_allocated / self.rows)
        cell_w = width // cols if cols else width
        cell_h = height // self.rows if self.rows else height

        for row in range(self.rows):
            for col in range(cols):
                day_index = row * cols + col
                if day_index < self.days_allocated:
                    x0 = col * cell_w
                    y0 = row * cell_h
                    x1 = x0 + cell_w
                    y1 = y0 + cell_h
                    draw.rectangle([x0, y0, x1, y1], outline="green", width=2)
                    day_title = f"iCloud Day {day_index+1}"
                    bbox = draw.textbbox((0, 0), day_title, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                    text_x = x0 + (cell_w - text_w) // 2
                    text_y = y0 + 5
                    draw.text((text_x, text_y), day_title, fill="green", font=font)
                    num_events = random.randint(1, 2)
                    event_y = text_y + text_h + 5
                    for _ in range(num_events):
                        event_text = "iCloud: " + lorem.sentence()
                        draw.text((x0+5, event_y), event_text, fill="purple", font=font)
                        event_y += 20
        return img

PANEL_CLASS = iCloudCalendarPanel

if __name__ == "__main__":
    panel = iCloudCalendarPanel()
    panel.configure()
    img = panel.render(400, 480)
    img.show()