Run using python in terminal.

"python main.py"

You need to have "requests" installed.
If not, it could fail to run and try to install te requests package itself - hopefully...

TO install packages, you need to have installed pip
- windows: py -m ensurepip --upgrade
- max: python -m ensurepip --upgrade

You change the configuration in the main file, default configuration:

  "start_date": "2024-01-01"
  "end_date": "2024-12-31"
  "country_code": "CZ"
  "working_days_per_week": 4
