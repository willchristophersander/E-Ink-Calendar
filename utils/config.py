# utils/config.py
import os
import json

class Config:
    def __init__(self, config_file="config.json"):
        with open(config_file, "r") as f:
            data = json.load(f)
        
        # Check if we are in test mode; if so, override the base directory.
        self.test_mode = data.get("test_mode", False)
        if self.test_mode:
            self.base_dir = os.getcwd()  # Use the current directory when testing
        else:
            self.base_dir = data.get("base_dir", os.getcwd())
        
        self.update_interval = data.get("update_interval", 3600)
        self.ical_files_dir = os.path.join(self.base_dir, data.get("ical_files_dir", "data/ics"))
        self.merged_calendar_file = os.path.join(self.base_dir, data.get("merged_calendar_file", "data/merged_calendar.json"))
        self.credentials_file = os.path.join(self.base_dir, data.get("credentials_file", "data/credentials.json"))
        self.holiday_api_url = data.get("holiday_api_url", "https://date.nager.at/api/v3/PublicHolidays")
        self.display_width = data.get("display_width", 800)
        self.display_height = data.get("display_height", 480)
        self.font_path = data.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        self.output_image = os.path.join(self.base_dir, data.get("output_image", "data/weekly_calendar_output.bmp"))