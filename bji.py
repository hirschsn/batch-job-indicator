#!/usr/bin/python
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
gi.require_version("Notify", "0.7")
from gi.repository import Notify
from gi.repository import Gtk as gtk
from gi.repository import GObject

class JobRegistry(object):
    jobs = {}
    parsed_once = False

    class CancelledJob(object):
        """Dummy class indicating a manually closed job indicator.
        Allows to call set_state which is a no-op."""
        def set_state(self, *args):
            pass

    def close_callback(self, jobid):
        # Indicator closed: Replace JIndicator
        # with dummy class allowing to call set_state() on it
        # and indicating that the job indicator has been closed manually.
        self.jobs[jobid] = JobRegistry.CancelledJob()

    def _all_jobs_cancelled(self):
        return all(map(lambda v: type(v) is JobRegistry.CancelledJob, self.jobs.values()))

    def empty(self):
        # Holds only closed jobs and at least one job has been registered in the past
        return self.parsed_once and self._all_jobs_cancelled()

    def handle_job(self, jobid, state):
        if not self.parsed_once and state != "C":
            self.parsed_once = True

        if jobid in self.jobs:
            # May also be called on manually closed jobs indicators
            # (class Cancelled Job)
            self.jobs[jobid].set_state(state)
        elif state != "C":
            # Don't open a new indicator for an already completed job
            self.jobs[jobid] = JIndicator(jobid, state, self.close_callback)

SHOULD_QUIT = False
def run(machine, user_name, every_sec=60):
    jreg = JobRegistry()
    jparser = parser_maker(machine)(user_name, jreg.handle_job)
    cmd = "sh -c 'while :; do {cmd}; sleep {s}; done'".format(cmd=jparser.command(), s=every_sec)
    argv = ["ssh", machine, cmd]
    p = None
    while not jreg.empty() and not SHOULD_QUIT:
        # Initially open or(!) reopen the connection
        # p.poll() returns the exit state of the process or None if it is still running.
        if (p is None or p.poll() is not None) and not SHOULD_QUIT:
            print("(Re-)opening remote connection.")
            p = subprocess.Popen(argv, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        jparser.parse(p.stdout.readline().decode())
    if p is not None:
        p.terminate()
    if not SHOULD_QUIT:
        gtk.main_quit()

def main():
    Notify.init("Batch Job Watcher")
    parser = argparse.ArgumentParser(description="Watch batch jobs on foreign machines and display a tray icons.")
    parser.add_argument("--user", dest="user", help="Username on the foreign machine", type=str, default=r"$(whoami)")
    parser.add_argument("-n", dest="every_n", metavar="SEC", help="Number of seconds between two checks", type=int, default=10)
    parser.add_argument("machine", metavar="MACHINE", help="Machine to watch", type=str)
    args = parser.parse_args()

    GObject.threads_init()
    t = threading.Thread(target=run, args=(args.machine, args.user, args.every_n))
    t.start()
    try:
        gtk.main()
    except KeyboardInterrupt:
        print("Caught SIGINT. Quitting...")
        # Continue quitting normally
        pass
    global SHOULD_QUIT
    SHOULD_QUIT = True
    t.join()

if __name__ == '__main__':
    main()
