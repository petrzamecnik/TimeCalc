from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    import subprocess
    import sys

    # Implement pip installation
    def install(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    # Install the missing package
    install("requests")
    import requests

# Main Config
config = {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "country_code": "CZ",
    "working_days_per_week": 4  # Add this configuration for working days per week
}

# API For Holidays - https://www.openholidaysapi.org/en/
holiday_api_url = (
    f"https://openholidaysapi.org/PublicHolidays?"
    f"countryIsoCode={config['country_code']}"
    f"&languageIsoCode={config['country_code']}"
    f"&validFrom={config['start_date']}"
    f"&validTo={config['end_date']}")


# Helper Functions
def is_holiday(date, holidays):
    for holiday in holidays:
        if holiday["startDate"] <= date <= holiday["endDate"]:
            return True
    return False


def get_working_days_count(year, month, holidays, working_days_per_week, end_day=None):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, end_day) if end_day else (
        datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1))
    _current_date = start_date

    _working_days_count = 0
    while _current_date <= end_date:
        if _current_date.weekday() < working_days_per_week and not is_holiday(_current_date.strftime("%Y-%m-%d"),
                                                                              holidays):
            _working_days_count += 1
        _current_date += timedelta(days=1)

    return _working_days_count


def calculate_working_hours(working_days):
    working_hours = working_days * 8
    return working_hours


def parse_worked_hours(worked_hours_input):
    parts = worked_hours_input.split(":")
    hours = int(parts[0]) if len(parts) > 0 and parts[0] else 0
    minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    seconds = int(parts[2]) if len(parts) > 2 and parts[2] else 0
    return hours, minutes, seconds


def calculate_worked_days(worked_hours, worked_minutes, worked_seconds):
    total_seconds = worked_hours * 3600 + worked_minutes * 60 + worked_seconds
    worked_days = total_seconds / (8 * 3600)
    return worked_days


def calculate_remaining_time(total_working_days, total_working_hours, worked_days):
    remaining_days = total_working_days - worked_days
    remaining_hours = total_working_hours - (worked_days * 8)
    remaining_minutes = (remaining_hours - int(remaining_hours)) * 60
    remaining_seconds = (remaining_minutes - int(remaining_minutes)) * 60

    return remaining_days, remaining_hours, int(remaining_minutes), int(remaining_seconds)


def calculate_banked_hours(worked_hours, elapsed_working_days):
    expected_hours = elapsed_working_days * 8
    banked_hours = worked_hours - expected_hours
    return banked_hours


# User input for worked hours
worked_hours_input = input("Enter worked hours (HOURS:MINUTES:SECONDS): ")
worked_hours, worked_minutes, worked_seconds = parse_worked_hours(worked_hours_input)

while True:
    additional_hours_input = input(
        "Enter additional hours (Medical Leave / Vacation) [HOURS:MINUTES or HOURS | ENTER to skip]: ")
    if additional_hours_input == '' or additional_hours_input == '0':
        break
    elif ':' in additional_hours_input:
        additional_hours, additional_minutes, _ = parse_worked_hours(additional_hours_input)
        worked_hours += additional_hours
        worked_minutes += additional_minutes
    else:
        try:
            additional_hours = float(additional_hours_input)
            worked_hours += additional_hours
            # break
        except ValueError:
            print("Invalid input. Please enter the hours in the correct format.")

response = requests.get(holiday_api_url)
if response.status_code == 200:
    holidays = response.json()

    current_date = datetime.now()
    year = current_date.year
    month = current_date.month

    # Calculations
    working_days_per_week = config["working_days_per_week"]
    working_days = get_working_days_count(year, month, holidays, working_days_per_week)
    working_hours = calculate_working_hours(working_days)
    worked_days = calculate_worked_days(worked_hours, worked_minutes, worked_seconds)

    remaining_days, remaining_hours, remaining_minutes, remaining_seconds = calculate_remaining_time(
        working_days, working_hours, worked_days)

    elapsed_working_days = get_working_days_count(year, month, holidays, working_days_per_week, current_date.day)
    banked_hours = calculate_banked_hours(worked_hours, elapsed_working_days)

    # Print detailed info
    print(f"You worked for {worked_hours} HOURS | {worked_minutes} MINUTES | {worked_seconds} SECONDS \n")
    print(f"In the current month, there are -> {working_days} DAYS | {working_hours} HOURS")
    print(f"You need to work for            -> {remaining_days:.2f} DAYS | {remaining_hours:.2f} HOURS")
    print(f"Your banked hours are           -> {banked_hours:.2f} HOURS")

else:
    print(f"Failed to get data from {holiday_api_url}")
