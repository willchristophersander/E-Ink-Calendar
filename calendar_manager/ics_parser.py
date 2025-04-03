from datetime import date
import icalendar

def parse_ics(ics_content):
    """
    Parses ICS content and returns a list of event dictionaries.
    
    Each event dictionary contains:
      - summary: The event title.
      - start_time: ISO formatted start date/time.
      - end_time: ISO formatted end date/time.
      - description: Event description (if any).
      - location: Event location (if any).
    """
    events = []
    try:
        cal = icalendar.Calendar.from_ical(ics_content)
        base_date = date.today()
        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    "summary": str(component.get('summary', '')),
                    "start_time": (dt := component.get('dtstart')) and dt.dt.isoformat() or None,
                    "end_time": (et := component.get('dtend')) and et.dt.isoformat() or None,
                    "description": str(component.get('description', '')),
                    "location": str(component.get('location', '')),
                    "day": (dt and ((dt.dt.date() if hasattr(dt.dt, "date") else dt.dt) - base_date).days + 1) or None
                }
                events.append(event)
    except Exception as e:
        print("Error parsing ICS content:", e)
    return events