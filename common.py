#!/usr/bin/env python
# ===--- common.py --------------------------------------------------------===
#
#  This source file is part of the Swift.org open source project
#
#  Copyright (c) 2014 - 2017 Apple Inc. and the Swift project authors
#  Licensed under Apache License v2.0 with Runtime Library Exception
#
#  See https://swift.org/LICENSE.txt for license information
#  See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ===----------------------------------------------------------------------===

"""A library containing common utility functionality."""
from __future__ import print_function

import multiprocessing
import os
import pipes
import platform
import signal
import subprocess
import sys
import shlex

try:
    basestring        # Python 2
except NameError:
    basestring = str  # Python 3

DEFAULT_EXECUTE_TIMEOUT = 10*60

branches = {
    'main': {
        'llvm-project': 'stable/20211026',
        'swift': 'main',
        'cmark': 'main',
        'ninja': 'release',
        'llbuild': 'main',
        'swiftpm': 'main',
        'swift-corelibs-libdispatch': 'main',
        'swift-corelibs-foundation': 'main',
        'swift-corelibs-xctest': 'main',
        'swift-argument-parser': '1.0.3',
        'swift-driver': 'main',
        'yams': '4.0.2',
        'swift-tools-support-core': 'main',
        'swift-crypto': '1.1.5',
        'swift-atomics': '1.0.2',
        'swift-collections': '1.0.1',
        'swift-numerics': '1.0.1',
        'swift-system': '1.1.1',
        'swift-experimental-string-processing': 'dev/6',
    },
    'release/5.6': {
        'llvm-project': 'swift/release/5.6',
        'swift': 'release/5.6',
        'cmark': 'release/5.6',
        'ninja': 'release',
        'llbuild': 'release/5.6',
        'swiftpm': 'release/5.6',
        'swift-corelibs-libdispatch': 'release/5.6',
        'swift-corelibs-foundation': 'release/5.6',
        'swift-corelibs-xctest': 'release/5.6',
        'swift-argument-parser': '1.0.3',
        'swift-driver': 'release/5.6',
        'yams': '4.0.2',
        'swift-tools-support-core': 'release/5.6',
        'swift-crypto': '1.1.5',
        'swift-atomics': '1.0.2',
        'swift-collections': '1.0.1',
        'swift-numerics': '1.0.1',
        'swift-system': '1.1.1',
    },
    'release/5.5': {
        'llvm-project': 'swift/release/5.5',
        'swift': 'release/5.5',
        'cmark': 'release/5.5',
        'ninja': 'release',
        'llbuild': 'release/5.5',
        'swiftpm': 'release/5.5',
        'swift-corelibs-libdispatch': 'release/5.5',
        'swift-corelibs-foundation': 'release/5.5',
        'swift-corelibs-xctest': 'release/5.5',
        'swift-argument-parser': '0.4.3',
        'swift-driver': 'release/5.5',
        'yams': '4.0.2',
        'swift-tools-support-core': 'release/5.5',
        'swift-crypto': '1.1.5',
        'swift-atomics': '0.0.3',
        'swift-collections': '0.0.4',
        'swift-numerics': '0.1.0',
        'swift-system': '0.0.2',
    },
    'release/5.4': {
        'llvm-project': 'swift/release/5.4',
        'swift': 'release/5.4',
        'cmark': 'release/5.4',
        'ninja': 'release',
        'llbuild': 'release/5.4',
        'swiftpm': 'release/5.4',
        'swift-corelibs-libdispatch': 'release/5.4',
        'swift-corelibs-foundation': 'release/5.4',
        'swift-corelibs-xctest': 'release/5.4',
        'swift-argument-parser': '0.3.0',
        'swift-driver': 'release/5.4',
        'yams': '3.0.1',
        'swift-tools-support-core': 'release/5.4',
        'swift-crypto': '1.1.5',
        'swift-atomics': '0.0.3',
        'swift-collections': '0.0.4',
        'swift-numerics': '0.1.0',
        'swift-system': '0.0.2',
    },
}

swiftc_operation = {
    'main': '-typecheck',
    'swift-3.1-branch': '-typecheck',
    'swift-3.0-branch': '-parse',
}

swiftc_version = {
    'main': '3',
    'swift-3.1-branch': '3',
    'swift-3.0-branch': None,
}

swift_branch = None


def set_swift_branch(branch):
    """Configure the common library for a specific branch.

    >>> set_swift_branch('main')
    """
    global swift_branch
    swift_branch = branch


def set_default_execute_timeout(timeout):
    """Override the default execute timeout"""
    global DEFAULT_EXECUTE_TIMEOUT
    DEFAULT_EXECUTE_TIMEOUT = timeout


def clone_repos():
    """Clone Swift and dependencies in parallel.

    >>> import tempfile
    >>> set_swift_branch('main')
    >>> tmpdir = tempfile.mkdtemp()
    >>> with DirectoryContext(tmpdir):
    ...     clone_repos()
    >>> repos = os.listdir(tmpdir)
    >>> check_execute(['rm', '-rf', tmpdir])
    0
    >>> repos #doctest: +NORMALIZE_WHITESPACE
    ['llvm-project', 'cmark', 'llbuild', 'ninja', 'swift',
     'swift-corelibs-foundation', 'swift-corelibs-libdispatch',
     'swift-corelibs-xctest', 'swiftpm', 'swift-experimental-string-processing']
    """
    cpu_count = multiprocessing.cpu_count()
    workspace = private_workspace('.')
    repos = [
        '{} git@github.com:apple/llvm-project.git '
        '{}/llvm-project '.format(
            branches[swift_branch]['llvm-project'], workspace
        ),
        '{} git@github.com:apple/swift.git {}/swift '.format(
            branches[swift_branch]['swift'], workspace
        ),
        '{} git@github.com:apple/swift-cmark.git {}/cmark '.format(
            branches[swift_branch]['cmark'], workspace
        ),
        '{} git@github.com:ninja-build/ninja.git {}/ninja '.format(
            branches[swift_branch]['ninja'], workspace
        ),
        '{} git@github.com:apple/swift-llbuild.git {}/llbuild '.format(
            branches[swift_branch]['llbuild'], workspace
        ),
        '{} git@github.com:apple/swift-package-manager.git '
        '{}/swiftpm '.format(
            branches[swift_branch]['swiftpm'], workspace
        ),
        '{} git@github.com:apple/swift-corelibs-foundation.git '
        '{}/swift-corelibs-foundation '.format(
            branches[swift_branch]['swift-corelibs-foundation'], workspace
        ),
        '{} git@github.com:apple/swift-corelibs-libdispatch.git '
        '{}/swift-corelibs-libdispatch '.format(
            branches[swift_branch]['swift-corelibs-libdispatch'], workspace
        ),
        '{} git@github.com:apple/swift-corelibs-xctest.git '
        '{}/swift-corelibs-xctest '.format(
            branches[swift_branch]['swift-corelibs-xctest'], workspace
        ),
        '{} git@github.com:apple/swift-argument-parser.git '
        '{}/swift-argument-parser '.format(
            branches[swift_branch]['swift-argument-parser'], workspace
        ),
        '{} git@github.com:apple/swift-driver.git '
        '{}/swift-driver '.format(
            branches[swift_branch]['swift-driver'], workspace
        ),
        '{} git@github.com:jpsim/Yams.git '
        '{}/yams '.format(
            branches[swift_branch]['yams'], workspace
        ),
        '{} git@github.com:apple/swift-tools-support-core.git '
        '{}/swift-tools-support-core '.format(
            branches[swift_branch]['swift-tools-support-core'], workspace
        ),
        '{} git@github.com:apple/swift-crypto.git '
        '{}/swift-crypto '.format(
            branches[swift_branch]['swift-crypto'], workspace
        ),
        '{} git@github.com:apple/swift-atomics.git '
        '{}/swift-atomics '.format(
            branches[swift_branch]['swift-atomics'], workspace
        ),
        '{} git@github.com:apple/swift-collections.git '
        '{}/swift-collections '.format(
            branches[swift_branch]['swift-collections'], workspace
        ),
        '{} git@github.com:apple/swift-numerics.git '
        '{}/swift-numerics '.format(
            branches[swift_branch]['swift-numerics'], workspace
        ),
        '{} git@github.com:apple/swift-system.git '
        '{}/swift-system '.format(
            branches[swift_branch]['swift-system'], workspace
        ),
        '{} git@github.com:apple/swift-experimental-string-processing.git '
        '{}/swift-experimental-string-processing '.format(
            branches[swift_branch]['swift-experimental-string-processing'], workspace
        ),
    ]

    process0 = subprocess.Popen([
        'xargs', '-P%s' % cpu_count, '-n3',
        'bash', '-c', 'set -x; git clone -q -b "$0" --recursive "$1" "$2"'
    ], stdin=subprocess.PIPE)

    for repo in repos:
        process0.stdin.write(repo)

    process0.stdin.close()

    assert process0.wait() == 0


class Unreachable(Exception):
    """An exception to be thrown at an unreachable."""
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return 'Unreachable("{}")'.format(self.s)


class Unimplemented(Exception):
    """An exception to be thrown at an unimplemented."""
    pass


class UnsupportedPlatform(Exception):
    """An exception to be thrown at an unsupported platform."""
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    """A callback function that raises an alarm."""
    raise Alarm


class Timeout(object):
    """A class to enable timing out a given 'with' block.

    >>> import time
    >>> with Timeout(1):
    ...    time.sleep(0.5)
    >>> with Timeout(1):
    ...    time.sleep(2)
    Traceback (most recent call last):
    Alarm
    """
    def __init__(self, timeout_seconds):
        self.timeout_seconds = timeout_seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(self.timeout_seconds)

    def __exit__(self, etype, value, traceback):
        signal.alarm(0)


def shell_join(command):
    """Return a valid shell string from a given command list.

    >>> shell_join(['echo', 'Hello, World!'])
    "echo 'Hello, World!'"
    """
    return ' '.join([pipes.quote(x) for x in command])


def debug_print(s, stderr=sys.stderr):
    """Print a string to stderr and flush."""
    print(s, file=stderr)
    stderr.flush()


def shell_debug_print(command, stderr=sys.stderr):
    """Print a command list as a shell string to stderr and flush."""
    debug_print('$ ' + shell_join(command), stderr=stderr)


class ExecuteCommandFailure(Exception):
    """An exception to be thrown when check_execute functions fail."""
    def __init__(self, command, returncode):
        self.command = command
        self.returncode = returncode

    def __str__(self):
        return ('ExecuteCommandFailure('
                'command="{}", '
                'returncode={})'.format(
                    shell_join(self.command),
                    self.returncode))


def execute(command, timeout=None,
            stdout=sys.stdout, stderr=sys.stderr,
            **kwargs):
    """Execute a given command with an optional timeout in seconds.

    >>> execute(['echo', 'Hello, World!'])
    0
    """
    if timeout is None:
        timeout = DEFAULT_EXECUTE_TIMEOUT
    shell_debug_print(command, stderr=stderr)
    returncode = 124  # timeout return code
    try:
        with Timeout(timeout):
            returncode = subprocess.call(
                command, stdout=stdout, stderr=stderr, **kwargs
            )
    except Alarm:
        debug_print(command[0] + ': Timed out', stderr=stderr)

    return returncode


def check_execute_output(command, timeout=None,
                         stdout=sys.stdout, stderr=sys.stderr, **kwargs):
    """Check execute a given command and return its output.

    >>> check_execute_output(['echo', 'Hello, World!'])
    'Hello, World!\\n'
    """
    if timeout is None:
        timeout = DEFAULT_EXECUTE_TIMEOUT
    shell_debug_print(command, stderr=stderr)
    try:
        with Timeout(timeout):
            output = subprocess.check_output(
                command, stderr=stderr, **kwargs
            )
    except subprocess.CalledProcessError as e:
        debug_print(e, stderr=stderr)
        raise
    return output


def check_execute(command, timeout=None,
                  sandbox_profile=None, max_retries=1,
                  stdout=sys.stdout, stderr=sys.stderr,
                  **kwargs):
    """Check execute a given command.

    >>> check_execute(['echo', 'Hello, World!'])
    0
    """
    if timeout is None:
        timeout = DEFAULT_EXECUTE_TIMEOUT
    if sandbox_profile:
        if platform.system() == 'Darwin':
            command = ['sandbox-exec', '-f', sandbox_profile] + command
        elif platform.system() == 'Linux':
            # TODO: remove explicit dns after Firejail bug is resolved
            command = ['firejail', '--quiet', '--profile=%s' % sandbox_profile,
                       '--private=.', '--overlay-tmpfs',
                       '--dns=8.8.8.8'] + command
    returncode = -1
    for retry in range(max_retries):
        returncode = execute(command, timeout=timeout,
                             stdout=stdout, stderr=stderr,
                             **kwargs)
        if returncode == 0:
            return returncode
    raise ExecuteCommandFailure(command, returncode)


def git_submodule_update(path, stdout=sys.stdout, stderr=sys.stderr):
    """Perform a git submodule update operation on a path."""
    command = ['git', '-C', path, 'submodule', 'update', '--init',
               '--recursive']
    return check_execute(command, stdout=stdout, stderr=stderr)


def git_clean(path, stdout=sys.stdout, stderr=sys.stderr):
    """Perform a git clean operation on a path."""
    command = ['git', '-C', path, 'clean', '-ffdx']
    if platform.system() == 'Darwin':
        check_execute(['chflags', '-R', 'nouchg', path], stdout=stdout, stderr=stderr)
    return check_execute(command, stdout=stdout, stderr=stderr)


def git_pull(path, stdout=sys.stdout, stderr=sys.stderr):
    """Perform a git pull operation on a path."""
    command = ['git', '-C', path, 'pull']
    return check_execute(command, stdout=stdout, stderr=stderr)


def git_clone(url, path, tree=None, recursive=True,
              stdout=sys.stdout, stderr=sys.stderr):
    """Perform a git clone operation on a url to a path."""
    returncodes = []
    command = ['git', 'clone', url, path]
    returncodes.append(check_execute(command, stdout=stdout, stderr=stderr))
    if tree:
        returncodes.append(git_checkout(tree, path,
                                        force=True,
                                        stdout=stdout, stderr=stderr))
    if recursive:
        returncodes.append(git_submodule_update(path,
                                                stdout=stdout, stderr=stderr))
    return 0 if all(rc == 0 for rc in returncodes) else 1


def git_checkout(tree, path, force=False,
                 stdout=sys.stdout, stderr=sys.stderr):
    """Perform a git checkout operation on a path."""
    command = ['git', '-C', path, 'checkout', tree]
    if force:
        command.insert(4, '-f')
    return check_execute(command, stdout=stdout, stderr=stderr)


def git_sha(path, stdout=sys.stdout, stderr=sys.stderr):
    """Return the current sha of a Git repo at a path."""
    command = ['git', '-C', path, 'rev-parse', 'HEAD']
    return check_execute_output(command, stdout=stdout, stderr=stderr).strip()


def git_update(url, configured_sha, path,
               incremental=False,
               stdout=sys.stdout, stderr=sys.stderr):
    """Update a repository to a given sha if necessary."""
    returncodes = []
    try:
        if not incremental:
            git_clean(path, stdout=stdout, stderr=stderr)
        current_sha = git_sha(path, stdout=stdout, stderr=stderr)
        debug_print('current_sha: ' + current_sha, stderr=stderr)
        debug_print('configured_sha: ' + configured_sha, stderr=stderr)
        if current_sha != configured_sha:
            debug_print('current_sha != configured_sha', stderr=stderr)
            command_fetch = ['git', '-C', path, 'fetch']
            returncodes.append(check_execute(command_fetch,
                                             stdout=stdout, stderr=stderr))
            returncodes.append(git_checkout(configured_sha, path,
                                            force=True,
                                            stdout=stdout, stderr=stderr))
            returncodes.append(git_submodule_update(
                path, stdout=stdout, stderr=stderr
            ))
        else:
            debug_print('current_sha == configured_sha', stderr=stderr)
            returncodes.append(git_checkout(configured_sha, path,
                                            force=True,
                                            stdout=stdout, stderr=stderr))
    except ExecuteCommandFailure:
        debug_print("warning: Unable to update. Falling back to a clone.",
                    stderr=stderr)
        check_execute(['rm', '-rf', path], stdout=stdout, stderr=stderr)
        return git_clone(url, path, tree=configured_sha,
                         stdout=stdout, stderr=stderr)
    return 0 if all(rc == 0 for rc in returncodes) else 1


class DirectoryContext(object):
    """Change to a given directory for the duration of a given 'with' block."""
    def __init__(self, path, stderr=sys.stderr):
        self.path = os.path.expanduser(path)
        self.stderr = stderr

    def __enter__(self):
        self.previous_path = os.getcwd()
        shell_debug_print(['pushd', self.path], stderr=self.stderr)
        os.chdir(self.path)

    def __exit__(self, etype, value, traceback):
        shell_debug_print(['popd'], stderr=self.stderr)
        os.chdir(self.previous_path)


def private_workspace(path):
    """Return a path relative to a private workspace."""
    if 'WORKSPACE' in os.environ:
        workspace = os.environ['WORKSPACE']
        return os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(workspace)),
            'workspace-private',
            os.path.basename(workspace), path
        ))
    else:
        return os.path.abspath(path)


def popen(*args, **kwargs):
    formatted = [x.format(**os.environ) for x in args[0]]
    shell_debug_print(args[0])
    args = (formatted,) + args[1:]
    return subprocess.Popen(*args, **kwargs)


def call(c):
    if isinstance(c, basestring):
        c = shlex.split(c)
    formatted = [x.format(**os.environ) for x in c]
    shell_debug_print(c)
    return subprocess.call(formatted)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
