#!/usr/bin/python2
#
# See LICENSE for license details.
#
from __future__ import print_function
from jindicator import JIndicator
from machines.machine import parser_maker

import argparse
import gi
import threading
import sys
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
from gi.repository import GObject

class JobRegistry(object):
    jobs = {}
    parsed_once = False

    def close_callback(self, jobid):
        del self.jobs[jobid]

    def empty(self):
        return self.parsed_once and not bool(self.jobs)

    def handle_job(self, jobid, state):
        self.parsed_once = True
        if jobid in self.jobs:
            self.jobs[jobid].set_state(state)
        else:
            self.jobs[jobid] = JIndicator(jobid, state, self.close_callback)

def run(machine, user_name, every_sec=60):
    jreg = JobRegistry()
    jparser = parser_maker(machine)(user_name, jreg.handle_job)
    # Don't mess with escapes or quotes
    cmd = "ssh {mach} 'sh -c '\\''while :; do {cmd}; sleep {s}; done'\\'''".format(mach=machine, cmd=jparser.command(), s=every_sec)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # TODO: reopen connection if ssh dies.
    while not jreg.empty() and p.poll() is None:
        jparser.parse(p.stdout.readline())
    p.terminate()
    gtk.main_quit()

def main():
    parser = argparse.ArgumentParser(description="Watch batch jobs on foreign machines and display a tray icons.")
    parser.add_argument("--user", dest="user", help="Username on the foreign machine", type=str, default=r"$(whoami)")
    parser.add_argument("-n", dest="every_n", metavar="SEC", help="Number of seconds between two checks", type=int, default=60)
    parser.add_argument("machine", metavar="MACHINE", help="Machine to watch", type=str)
    args = parser.parse_args()

    GObject.threads_init()
    t = threading.Thread(target=run, args=(args.machine, args.user, args.every_n))
    t.start()
    gtk.main()
    t.join()

if __name__ == '__main__':
    main()
