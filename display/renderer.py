import math
import os
import json
from PIL import Image, ImageDraw, ImageFont

class DisplayManager:
    def __init__(self, config):
        """
        Initialize the display manager.
        If config.test_mode is True, use dummy mode.
        Otherwise, initialize the actual e-ink display.
        """
        self.test_mode = config.test_mode
        if not self.test_mode:
            import waveshare_epd.epd7in5_V2 as epd
            self.epd = epd.EPD()
            self.epd.init()
            self.epd.Clear()
    
    @staticmethod
    def load_config(config_name):
        """Load JSON configuration file and return the dictionary."""
        with open(config_name, "r") as f:
            return json.load(f)
    
    def render(self, calendar_data, config_name, image_opts=None, width=800, height=480):
        """
        Renders the display layout using parsed ICS event data.
        
        This method:
          - Loads configuration from config_name (a JSON file).
          - Uses the configuration (days, display_mode, rows, image_options) to set up the layout.
          - For "rect" display mode, it draws a grid of day cells and writes the day title at the top of each cell.
          - It then filters calendar_data for events matching the current day (using the computed "day" key)
            and draws each event summary inside the cell.
          - If image_opts indicate an image to include, it loads, resizes, and pastes that image.
          - Finally, if in test mode the image is shown on screen; otherwise it is sent to the e-ink display.
        """
        # Load layout configuration
        config = DisplayManager.load_config(config_name)
        days = config.get("days")
        display_mode = config.get("display_mode")
        rows = config.get("rows")
        config_image_opts = config.get("image_options")
        if image_opts is None:
            image_opts = config_image_opts
        
        # Create a blank white canvas.
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        
        # Set up font.
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        
        if display_mode == "rect":
            # Calculate grid dimensions.
            cols = math.ceil(days / rows)
            cell_width = width // cols
            cell_height = height // rows
            
            for row in range(rows):
                for col in range(cols):
                    day_index = row * cols + col
                    if day_index < days:
                        # Cell coordinates.
                        x0 = col * cell_width
                        y0 = row * cell_height
                        x1 = x0 + cell_width
                        y1 = y0 + cell_height
                        draw.rectangle([x0, y0, x1, y1], outline="black", width=2)
                        
                        # Draw day title.
                        day_title = f"Day {day_index + 1}"
                        bbox = draw.textbbox((0, 0), day_title, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        text_x = x0 + (cell_width - text_w) // 2
                        text_y = y0 + 5
                        draw.text((text_x, text_y), day_title, fill="black", font=font)
                        
                        # Draw event info from calendar_data for this day.
                        # Note: Each event already has a "day" key computed by your ICS parser.
                        events_for_day = [event for event in calendar_data if event.get("day") == day_index + 1]
                        event_y = text_y + text_h + 5
                        for event in events_for_day:
                            event_text = event.get("summary", "No Title")
                            draw.text((x0 + 5, event_y), event_text, fill="blue", font=font)
                            event_y += 20
        else:  # List mode.
            line_height = 20
            y_pos = 10
            for day in range(days):
                text = f"Day {day + 1}: [Event 1, Event 2, ...]"
                draw.text((10, y_pos), text, fill="black", font=font)
                y_pos += line_height
                if y_pos > height - line_height:
                    break
        
        # Process image options, if an image is to be included.
        if image_opts and image_opts.get("include_image"):
            try:
                image_file = image_opts.get("image_name")
                if not os.path.isabs(image_file):
                    image_file = os.path.join("data", "images", image_file)
                img_to_include = Image.open(image_file)
            except Exception as e:
                print(f"Error opening image {image_opts.get('image_name')}: {e}")
                img_to_include = None
            
            if img_to_include:
                # Determine new width based on size option.
                if image_opts.get("image_size") == "half":
                    new_width = width / 2
                elif image_opts.get("image_size") == "third":
                    new_width = width / 3
                else:
                    new_width = width / 2
                
                orig_width, orig_height = img_to_include.size
                ratio = orig_height / orig_width
                new_height = int(new_width * ratio)
                new_width = int(new_width)
                resized_img = img_to_include.resize((new_width, new_height))
                
                # Determine placement.
                pos = image_opts.get("image_position", "left")
                if pos == "left":
                    x = 0
                elif pos == "center":
                    x = (width - new_width) // 2
                elif pos == "right":
                    x = width - new_width
                else:
                    x = 0
                y = (height - new_height) // 2
                img.paste(resized_img, (x, y))
        
        # Output the final image.
        if self.test_mode:
            img.show()
        else:
            self.epd.display(self.epd.getbuffer(img))
            self.epd.sleep()
        
        return img