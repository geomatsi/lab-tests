def test_uboot_version(target, in_uboot):
    command = target.get_driver('UBootDriver')
    stdout, stderr, returncode = command.run("version")
    assert returncode == 0
    assert stdout
    assert not stderr
    # check uboot version output
    assert 'U-Boot' in stdout[0]
