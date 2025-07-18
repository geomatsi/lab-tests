from utils import mgmt


def test_version(target, in_uboot):
    command = target.get_driver('UBootDriver')
    stdout, stderr, ret = command.run("version")
    assert ret == 0
    assert stdout
    assert not stderr
    # check uboot version output
    assert 'U-Boot' in stdout[0]


def test_ping(target, in_uboot):
    strategy = target.get_strategy()
    command = target.get_driver('UBootDriver')
    _, _, ret = command.run(f"setenv serverip {mgmt.MGMT_SERVER_ADDR}")
    assert ret == 0
    _, _, ret = command.run(f"setenv ipaddr {mgmt.MGMT_TEST_ADDR}")
    assert ret == 0
    _, _, ret = command.run(f"ping {mgmt.MGMT_SERVER_ADDR}")
    assert ret == 0

    strategy.transition("off")
