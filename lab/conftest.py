import pytest

from lg.doublebootstrategy import DoubleBootStrategy
from lg.ubootnetstrategy import UBootNetStrategy
from lg.sunxifelstrategy import SunxiFELStrategy
from lg.kendrytestrategy import KendryteStrategy

from lg.modbus import ModbusTCPPowerDriver
from lg.sunxifeldriver import SunxiFELDriver
from lg.kendryteflashdriver import KendryteFlashDriver


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
        strategy.force("off")
        strategy.transition("shell")


@pytest.fixture(scope="function")
def assume_shell(strategy, capsys):
    pass


# options


def pytest_addoption(parser):
    parser.addoption('--repeat', action='store', help='Repeat test the specified number of times')


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)
        metafunc.fixturenames.append('tmp_ct')
        metafunc.parametrize('tmp_ct', range(count))
