import pytest
import re

from labgrid.driver import ExecutionError


def test_poweron(target, in_shell):
    """Boot the board and check console"""
    command = target.get_driver('ShellDriver')
    stdout, stderr, returncode = command.run('cat /proc/version')
    assert returncode == 0
    assert stdout
    assert not stderr
    assert 'Linux' in stdout[0]
