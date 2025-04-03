# calendar/manager.py
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import requests
from icalendar import Calendar, Event
from caldav import DAVClient

# Import your custom ICS parser (assume it exposes a parse_ics function)
from .ics_parser import parse_ics

class CalendarManager:
    def __init__(self, config):
        self.ical_dir = Path(config.ical_files_dir)
        self.merged_calendar_file = Path(config.merged_calendar_file)
        self.credentials_file = Path(config.credentials_file)
        self.holiday_api_url = config.holiday_api_url
        self.ical_dir.mkdir(parents=True, exist_ok=True)

    def _load_credentials(self):
        with open(self.credentials_file, "r") as f:
            creds = json.load(f)
        return creds["username"], creds["password"]

    def discover_calendars(self):
        """Discover calendars via CalDAV."""
        username, password = self._load_credentials()
        client = DAVClient("https://caldav.icloud.com", username=username, password=password)
        principal = client.principal()
        calendars = principal.calendars()
        calendar_data = [
            {"index": idx, "name": cal.name, "url": str(cal.url)}
            for idx, cal in enumerate(calendars)
        ]
        logging.info("Discovered calendars: %s", calendar_data)
        return calendars

    def fetch_all_calendars(self):
        """Fetch events from each discovered calendar and save them as ICS files."""
        username, password = self._load_credentials()
        client = DAVClient("https://caldav.icloud.com", username=username, password=password)
        principal = client.principal()
        calendars = principal.calendars()

        for calendar in calendars:
            try:
                events = calendar.date_search(datetime.now(), datetime.now() + timedelta(days=30))
                cal = Calendar()
                cal.add("prodid", "-//E-ink Calendar//EN")
                cal.add("version", "2.0")
                for event in events:
                    comp = Calendar.from_ical(event.data)
                    cal.add_component(comp)
                ics_path = self.ical_dir / f"{calendar.name.replace(' ', '_')}.ics"
                with open(ics_path, "wb") as f:
                    f.write(cal.to_ical())
                logging.info("Saved calendar '%s' to %s", calendar.name, ics_path)
            except Exception as e:
                logging.error("Error fetching calendar %s: %s", calendar.name, e)

    def fetch_holidays(self, country_code="US", year=None):
        """Fetch public holidays and save them as an ICS file."""
        if year is None:
            year = datetime.now().year
        try:
            response = requests.get(f"{self.holiday_api_url}/{year}/{country_code}")
            response.raise_for_status()
            holidays = response.json()

            cal = Calendar()
            cal.add("prodid", "-//E-ink Calendar//EN")
            cal.add("version", "2.0")
            for holiday in holidays:
                event = Event()
                event.add("summary", holiday["name"])
                dt = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
                event.add("dtstart", dt)
                event.add("dtend", dt + timedelta(days=1))
                cal.add_component(event)
            ics_path = self.ical_dir / "holidays.ics"
            with open(ics_path, "wb") as f:
                f.write(cal.to_ical())
            logging.info("Holidays saved to %s", ics_path)
        except Exception as e:
            logging.error("Error fetching holidays: %s", e)

    def merge_calendars(self):
        """
        Merge all ICS files in the directory into a single JSON file.
        (Assumes parse_ics returns a list of event dictionaries.)
        """
        all_events = []
        for ics_file in self.ical_dir.glob("*.ics"):
            try:
                with open(ics_file, "r") as f:
                    ics_content = f.read()
                events = parse_ics(ics_content)
                all_events.extend(events)
            except Exception as e:
                logging.error("Error parsing %s: %s", ics_file, e)
        with open(self.merged_calendar_file, "w") as f:
            json.dump(all_events, f, indent=4)
        logging.info("Merged calendar data saved to %s", self.merged_calendar_file)
        return all_events

    def update(self):
        """Orchestrate the update process: discover, fetch, and merge."""
        self.discover_calendars()
        self.fetch_all_calendars()
        self.fetch_holidays()
        merged_data = self.merge_calendars()
        return merged_data