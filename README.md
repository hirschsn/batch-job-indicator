# Batch Job Indicator

Places icons for jobs on foreign batch systems (read: HPC systems)
in your notification area and notifies you about state changes
with libnotify.

![screenshot](https://raw.githubusercontent.com/hirschsn/batch-job-indicator/master/screenshot.png)

(The notification in this screenshot is handled by the dunst notification-daemon.)

## Installation

I currently don't feel like writing some fancy setup.py-thingy.
Thus, clone the repo and do:
```sh
$ PYTHONPATH=".:$PYTHONPATH" ./bji.py ARGS...
```

### Prereqs

- Python 2.x (maybe 3 works?)
- python-gi (Notify, GObject, Gtk, AppIndicator3)

## Usage

$ ./bji.py --help
```
usage: bji.py [-h] [--user USER] [-n SEC] MACHINE

Watch batch jobs on foreign machines and display a tray icons.

positional arguments:
  MACHINE      Machine to watch

optional arguments:
  -h, --help   show this help message and exit
  --user USER  Username on the foreign machine
  -n SEC       Number of seconds between two checks
```

## License

For the code see LICENSE for details. The icons are public domain.

