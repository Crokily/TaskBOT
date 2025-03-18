# utils/date_util.py
from datetime import datetime

def parse_date(date_str: str) -> datetime:
    """
    Parses a date string, supporting the following formats:
    - "DD/MM/YYYY HH:MM"
    - "DD/MM/YYYY" (defaults to 00:00)
    Returns None if parsing fails.
    """
    formats = ["%d/%m/%Y %H:%M", "%d/%m/%Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # If only the date is entered, the default time is 00:00
            if fmt == "%d/%m/%Y":
                dt = dt.replace(hour=0, minute=0)
            return dt
        except ValueError:
            continue
    return None
