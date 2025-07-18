import pexpect
import pytest
import re

from labgrid.driver import ExecutionError

from utils import linux
from utils import mgmt


def test_boot(target, in_shell):
    """Basic Linux boot test"""
    command = target.get_driver('ShellDriver', name='test')
    stdout, stderr, returncode = command.run('dmesg')

    assert returncode == 0
    assert not stderr

    splats = linux.check_kernel_bootlog(stdout)
    if splats:
        pytest.fail(f"Kernel boot log issues: {splats}")


def test_version(target, in_shell):
    """Basic Linux prompt test"""
    command = target.get_driver('ShellDriver', name='test')
    stdout, stderr, returncode = command.run('cat /proc/version')
    assert returncode == 0
    assert stdout
    assert not stderr
    assert 'Linux' in stdout[0]


def test_linux_hackbench(target, in_shell):
    """Basic hackbench test"""
    command = target.get_driver('ShellDriver', name='test')

    try:
        command.run_check('which hackbench')
    except ExecutionError:
        pytest.skip("hackbench missing")

    stdout, stderr, returncode = command.run('hackbench')
    assert returncode == 0
    assert stdout
    assert not stderr
    assert 'Time:' in stdout[-1]

    result = stdout[-1].strip()
    pattern = r"Time:\s+(?P<time>\w+)"
    time, = map(int, re.search(pattern, result).groups())
    assert time < 60  # max 60 seconds


def test_net_ping(target, in_shell):
    """Basic ping test"""
    command = target.get_driver('ShellDriver', name='test')

    try:
        command.run_check("ping -c 3 {}".format(mgmt.MGMT_SERVER_ADDR))
    except ExecutionError:
        pytest.fail("Failed to execute ping")
    except pexpect.exceptions.TIMEOUT:
        pytest.fail("Ping command timed out")
