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

from twisted.internet import error
from twisted.trial import unittest

from buildbot import config
from buildbot.process import remotetransfer
from buildbot.process.results import RETRY
from buildbot.process.results import SUCCESS
from buildbot.steps.source import darcs
from buildbot.test.fake.remotecommand import ExpectCpdir
from buildbot.test.fake.remotecommand import ExpectDownloadFile
from buildbot.test.fake.remotecommand import ExpectRemoteRef
from buildbot.test.fake.remotecommand import ExpectRmdir
from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.test.fake.remotecommand import ExpectStat
from buildbot.test.util import sourcesteps
from buildbot.test.util.misc import TestReactorMixin


class TestDarcs(sourcesteps.SourceStepMixin, TestReactorMixin,
                unittest.TestCase):

    def setUp(self):
        self.setUpTestReactor()
        return self.setUpSourceStep()

    def tearDown(self):
        return self.tearDownSourceStep()

    def test_no_empty_step_config(self):
        with self.assertRaises(config.ConfigErrors):
            darcs.Darcs()

    def test_incorrect_method(self):
        with self.assertRaises(config.ConfigErrors):
            darcs.Darcs(repourl='http://localhost/darcs', mode='full',
                        method='fresh')

    def test_incremental_invalid_method(self):
        with self.assertRaises(config.ConfigErrors):
            darcs.Darcs(repourl='http://localhost/darcs', mode='incremental',
                        method='fresh')

    def test_no_repo_url(self):
        with self.assertRaises(config.ConfigErrors):
            darcs.Darcs(mode='full', method='fresh')

    def test_mode_full_clobber(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='clobber'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_copy(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='copy'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True, timeout=1200)
            .add(0),
            ExpectStat(file='source/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectCpdir(fromdir='source', todir='build', logEnviron=True, timeout=1200)
            .add(0),
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_no_method(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True, timeout=1200)
            .add(0),
            ExpectStat(file='source/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectCpdir(fromdir='source', todir='build', logEnviron=True, timeout=1200)
            .add(0),
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectStat(file='wkdir/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_patched(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(0),
            ExpectRmdir(dir='wkdir', logEnviron=True, timeout=1200)
            .add(0),
            ExpectStat(file='source/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectCpdir(fromdir='source', todir='build', logEnviron=True, timeout=1200)
            .add(0),
            ExpectStat(file='build/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='build',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_patch(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='incremental'),
            patch=(1, 'patch'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectStat(file='wkdir/_darcs', logEnviron=True)
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'pull', '--all', '--verbose'])
            .add(0),
            ExpectDownloadFile(blocksize=32768, maxsize=None,
                               reader=ExpectRemoteRef(remotetransfer.StringFileReader),
                               workerdest='.buildbot-diff', workdir='wkdir', mode=None)
            .add(0),
            ExpectDownloadFile(blocksize=32768, maxsize=None,
                               reader=ExpectRemoteRef(remotetransfer.StringFileReader),
                               workerdest='.buildbot-patched', workdir='wkdir', mode=None)
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['patch', '-p1', '--remove-empty-files',
                                 '--force', '--forward', '-i', '.buildbot-diff'])
            .add(0),
            ExpectRmdir(dir='wkdir/.buildbot-diff', logEnviron=True)
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_clobber_retry(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='clobber', retry=(0, 2)))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_clobber_revision(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='clobber'),
            dict(revision='abcdef01'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectDownloadFile(blocksize=32768, maxsize=None,
                               reader=ExpectRemoteRef(remotetransfer.StringFileReader),
                               workerdest='.darcs-context', workdir='wkdir', mode=None)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', '--context',
                                 '.darcs-context', 'http://localhost/darcs'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_clobber_revision_worker_2_16(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='clobber'),
            dict(revision='abcdef01'),
            worker_version={'*': '2.16'})
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectRmdir(dir='wkdir', logEnviron=True)
            .add(0),
            ExpectDownloadFile(blocksize=32768, maxsize=None,
                               reader=ExpectRemoteRef(remotetransfer.StringFileReader),
                               slavedest='.darcs-context', workdir='wkdir', mode=None)
            .add(0),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', '--context',
                                 '.darcs-context', 'http://localhost/darcs'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_no_existing_repo(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(0),
            ExpectStat(file='wkdir/.buildbot-patched', logEnviron=True)
            .add(1),
            ExpectStat(file='wkdir/_darcs', logEnviron=True)
            .add(1),
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            .add(0),
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            .add(ExpectShell.log('stdio', stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com'))
            .add(0)
        )
        self.expectOutcome(result=SUCCESS)
        self.expectProperty(
            'got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_worker_connection_lost(self):
        self.setupStep(
            darcs.Darcs(repourl='http://localhost/darcs',
                        mode='full', method='clobber'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            .add(('err', error.ConnectionLost()))
        )
        self.expectOutcome(result=RETRY, state_string="update (retry)")
        return self.runStep()
