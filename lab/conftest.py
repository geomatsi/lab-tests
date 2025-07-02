import pytest

from lg.modbus import ModbusTCPPowerDriver
from lg.ubootnetstrategy import UBootNetStrategy


@pytest.fixture(scope='session')
def command(target):
    return target


@pytest.fixture(scope="function")
def in_uboot(strategy, capsys):
    with capsys.disabled():
        strategy.transition("uboot")


@pytest.fixture(scope="function")
def in_shell(strategy, capsys):
    with capsys.disabled():
        strategy.transition("shell")


@pytest.fixture(scope="function")
def restart_shell(strategy, capsys):
    with capsys.disabled():
        strategy.transition("shell")


@pytest.fixture(scope="function")
def assume_shell(strategy, capsys):
    pass
