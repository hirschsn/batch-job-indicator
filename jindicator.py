# See LICENSE for license details.

import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
gi.require_version("Notify", "0.7")
from gi.repository import Notify
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk

_ICONS = {
    "Q": os.path.realpath("./icons/queued.svg"),
    "R": os.path.realpath("./icons/running.svg"),
    "C": os.path.realpath("./icons/completed.svg"),
    "H": os.path.realpath("./icons/hold.svg"),
}

_TEXT = {
    "Q": "Queued",
    "R": "Running",
    "C": "Completed",
    "H": "Hold",
}


def _make_menu(close_callback):
    """Returns a menu with one item (Close)."""
    menu = gtk.Menu()
    item_close = gtk.MenuItem("Close Indicator")
    item_close.connect("activate", close_callback)
    menu.append(item_close)
    menu.show_all()
    return menu


class JIndicator(object):
    """Places an indicator for a job in the notification area."""

    def __init__(self, jobid, state, close_cb):
        self.jobid = jobid
        self.close_callback = close_cb
        self.indicator = appindicator.Indicator.new(
            "Job-Indicator", _ICONS[state], category=appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(_make_menu(self.close))
        # Notification
        self.state = None
        self.set_state(state)

    def close(self, _):
        """Callback for the "Close" menu item.
        Hides the tray icon and calls the close callback."""
        # Immediately hide icon. Application will quit only from parse(), i.e. the next time qstat gets executed
        self.indicator.set_status(appindicator.IndicatorStatus.PASSIVE)
        self.close_callback(self.jobid)

    def set_state(self, new_state):
        """Sets the tray icon and notifies if new_state is different than the current state. Otherwise, this is a no-op."""
        if self.state == new_state:
            return
        self.state = new_state
        self.indicator.set_icon(_ICONS[new_state])
        # self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
        notf = Notify.Notification.new("Batch Job Watcher", "{}\n{}".format(
            self.jobid, _TEXT[new_state]), _ICONS[new_state])
        notf.set_timeout(0)
        notf.show()
