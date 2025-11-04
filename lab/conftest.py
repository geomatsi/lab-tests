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


@pytest.fixture(scope='session', autouse=True)
def poweroff(target, request):
    # session startup
    yield
    # session teardown
    if request.config.getoption("--poweroff"):
        strategy = target.get_strategy()

        # try gracefull shutdown if Linux shell is running
        try:
            console = target.get_driver("ConsoleProtocol")
            console.write(b'uname\n')
            lines = console.read(size=100, timeout=5).decode(errors='ignore')
            if "Linux" in lines:
                shell = target.get_driver("ShellDriver")
                shell.run('uname -a')
                shell.run('sync')
                shell.run('sync')
        except:
            # ignore anything here, just turn off the power
            pass
        finally:
            strategy.transition("off")


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
    parser.addoption('--poweroff', action='store_const', const=True, help='Power off device after test completion')


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)
        metafunc.fixturenames.append('tmp_ct')
        metafunc.parametrize('tmp_ct', range(count))
