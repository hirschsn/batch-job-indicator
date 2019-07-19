#!/usr/bin/python2
from __future__ import print_function

import os
import gi
import threading
import sys
import subprocess
import re
gi.require_version ("Gtk", "3.0")
gi.require_version ("AppIndicator3", "0.1")
gi.require_version ("Notify", "0.7")
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository.AppIndicator3 import IndicatorStatus
from gi.repository import GObject
from gi.repository import Notify

ICONS = {
    "Q": os.path.realpath("./icons/queued.svg"),
    "R": os.path.realpath("./icons/running.svg"),
    "C": os.path.realpath("./icons/completed.svg"),
}

JOBS = {}

QUIT = False

class JIndicator(object):
    def __init__ (self, jobid, state):
        self.jobid = jobid
        self.state = state
        self.indicator = appindicator.Indicator.new("Job-Indicator", ICONS[state], category=appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.new_menu())

    def new_menu(self):
        menu = gtk.Menu()
        item_quit = gtk.MenuItem("Close")
        item_quit.connect("activate", self.close)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def close(self, _):
        # Immediately hide icon. Application will quit only from parse(), i.e. the next time qstat gets executed
        self.indicator.set_status(appindicator.IndicatorStatus.PASSIVE)
        del JOBS[self.jobid]
        if len(JOBS) == 0:
            QUIT = True

    def set_state(self, new_state):
        if self.state == new_state:
            return
        self.indicator.set_icon(ICONS[new_state])
        #self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
        notf = Notify.Notification.new("Hazelhen Job Watcher", "{} switched to state {}".format(self.jobid, new_state), ICONS[new_state])
        notf.show()


def parse(user_name, every_sec=60):
    jre = re.compile(r"^\d+\.hazelhen-batch.*")
    p = subprocess.Popen("ssh hazelhen 'sh -c \"while :; do qstat -u {}; sleep {}; done\"'".format(user_name, every_sec), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while not QUIT:
        if p.poll() is not None:
            print("ssh terminated.")
            return

        l = p.stdout.readline()
        #print("Got line: '{}'".format(l))
        if jre.match(l):
            data = l.split()
            jobid, state = data[0], data[9]
            print("Job {} state: {}".format(jobid, state))
            if jobid in JOBS:
                JOBS[jobid].set_state(state)
            else:
                JOBS[jobid] = JIndicator(jobid, state)
    p.terminate()
    gtk.main_quit()


def main():
    if len(sys.argv) != 2:
        print("Usage: {} FOREIGN-USER-NAME".format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)
    GObject.threads_init()

    t = threading.Thread(target=parse, args=(sys.argv[1],))
    t.start()
    gtk.main()
    t.join()

if __name__ == '__main__':
    main()
