"""
Daily Bible Reading Utility

Prints the daily Bible reading schedule based on the current day of the year.
"""

import datetime
import os

# Configuration - use environment variables or defaults
DATA_DIR = os.environ.get('JW_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
BIBLE_FILE = os.path.join(DATA_DIR, 'bible.txt')
DAYS_FILE = os.path.join(DATA_DIR, 'days.txt')


def get_daily_reading():
    """Get the daily Bible reading for today."""
    try:
        with open(BIBLE_FILE) as f:
            bible = f.readlines()

        with open(DAYS_FILE) as f:
            reading_links = f.readlines()
    except FileNotFoundError as e:
        print(f"Error: Required file not found: {e.filename}")
        return None, None

    now = datetime.datetime.now()
    day_of_year = int(now.strftime("%j"))

    # Convert to 0-based index (day 1 = index 0)
    index = day_of_year - 1

    # Bounds checking
    if index < 0 or index >= len(bible) or index >= len(reading_links):
        print(f"Error: Day {day_of_year} is out of range for the data files")
        return None, None

    day = bible[index].strip()
    script = reading_links[index].strip()

    return script, day


if __name__ == '__main__':
    script, day = get_daily_reading()
    if script and day:
        print(script)
        print(day)
