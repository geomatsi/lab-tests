import pytest
import re

from labgrid.driver import ExecutionError


def test_poweroff(target, assume_shell):
    """Power off the board gracefully"""
    console = target.get_driver("ConsoleProtocol")
    strategy = target.get_strategy()

    # Send a ping to check if we're in shell or U-Boot
    console.write(b'uname\n')
    lines = console.read(size = 100, timeout = 5).decode(errors='ignore')

    if "Linux" in lines:
        # Linux shell
        shell = target.get_driver("ShellDriver")
        shell.run('uname -a')
        shell.run('sync')
        shell.run('sync')
    elif "=>" in lines:
        # U-Boot shell (most probably)
        shell = target.get_driver("UBootDriver")
        shell.run('version')
    else:
        # Unknown shell
        pytest.fail(f"Unable to determine current console environment: {lines}")

    strategy.transition("off")
