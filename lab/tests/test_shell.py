import pytest
import re

from labgrid.driver import ExecutionError


def test_linux_version(target, in_shell):
    """Basic Linux prompt test"""
    command = target.get_driver('ShellDriver')
    stdout, stderr, returncode = command.run('cat /proc/version')
    assert returncode == 0
    assert stdout
    assert not stderr
    assert 'Linux' in stdout[0]


def test_linux_hackbench(target, in_shell):
    """Basic hackbench test"""
    command = target.get_driver('ShellDriver')

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
