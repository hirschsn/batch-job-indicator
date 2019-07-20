# See LICENSE for license details.
from __future__ import print_function
import re


class MachineHazelhen(object):
    """Parser for HLRS's `Hazel Hen'."""
    _CMD = "qstat -u \"{}\""
    _jobre = re.compile(r"^\d+\.hazelhen-batch.*")

    def __init__(self, user_name, handle_job):
        self._cmd = self._CMD.format(user_name)
        self._handle_job = handle_job

    def command(self):
        """Returns the job queue list command."""
        return self._cmd

    def parse(self, line):
        """Parses output of the command given by command().
        Calls handle_job (see constructor) for parsed jobs."""
        if self._jobre.match(line):
            data = line.split()
            jobid, state = data[0], data[9]
            print("[Hazelhen] Job {} state: {}".format(jobid, state))
            self._handle_job(jobid, state)
