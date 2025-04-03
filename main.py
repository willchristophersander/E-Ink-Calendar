# main.py
import time
import logging
from utils.config import Config
from utils.logger import setup_logger
from calendar_manager.manager import CalendarManager
from display.renderer import DisplayManager

def main():
    setup_logger()
    logging.info("Starting e-ink calendar application")
    config = Config("config.json")
    
    calendar_manager = CalendarManager(config)
    display_manager = DisplayManager(config)
    
    while True:
        try:
            # Update calendar data
            calendar_data = calendar_manager.update()
            # Render the updated calendar on the (dummy or real) display
            display_manager.render(calendar_data, "display_configs/default_display.json")
        except Exception as e:
            logging.error("Error in main loop: %s", e, exc_info=True)
        
        logging.info("Sleeping for %s seconds...", config.update_interval)
        time.sleep(config.update_interval)

if __name__ == "__main__":
    main()