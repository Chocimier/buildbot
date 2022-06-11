# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import subprocess
import time

from twisted.internet import defer
from twisted.python import log

from buildbot.changes import base
from buildbot.util import epoch2datetime

class XbpsMirrorPoller(base.PollingChangeSource):
    def __init__(self, rsync_url, local_dir, arch,
            ssh_host=None, pollInterval=120, pollAtLaunch=False):
        log.msg("Constructing poller of {}".format(rsync_url))
        name = '{} {}'.format(arch, rsync_url)
        base.PollingChangeSource.__init__(self, name=name, pollInterval=pollInterval, pollAtLaunch=pollAtLaunch)
        self.rsync_url = rsync_url
        self.local_dir = local_dir
        self.ssh_host = ssh_host
        self.arch = arch
        self.lastChange = time.time()
        self.lastPoll = time.time()

    def describe(self):
        str = "Getting changes for arch {} from xbps mirror {}".format(
            self.arch, self.rsync_url)
        return str

    def poll(self):
        log.msg("Defer for rsync {}".format(self.rsync_url))
        self.lastPoll = time.time()
        d = defer.succeed(None)
        d.addCallback(self._sync_and_yield)
        return d

    @defer.inlineCallbacks
    def _sync_and_yield(self, *args, **kwargs):
        log.msg("Polling rsync mirror {}, {}, {}".format(self.rsync_url, args, kwargs))
        cmd = [
            './new_on_mirror.bash',
            self.rsync_url, self.local_dir
        ]
        if self.ssh_host:
            cmd = ['ssh', self.ssh_host] + cmd
        rsync = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = rsync.communicate()
        response = result[0]
        files = []
        for line in response.split('\n'):
            log.msg("Found {} on rsync mirror".format(line))
            if line.strip().endswith('.{}.xbps'.format(self.arch)):
                pkgname = line.rpartition('-')[0]
                files.append('srcpkgs/{}/template'.format(pkgname))
        yield self.master.addChange(
            author='someone',
            files=files,
            comments='----',
            branch='master',
        )
