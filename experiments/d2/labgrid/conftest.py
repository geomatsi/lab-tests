import pytest

from src.modbus import ModbusTCPPowerDriver


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
