import enum
import attr
import logging


from labgrid.factory import target_factory
from labgrid.strategy import Strategy, StrategyError


class Status(enum.Enum):
    unknown = 0
    off = 1
    setup = 2
    uboot = 3
    shell = 4


@target_factory.reg_driver
@attr.s(eq=False)
class DoubleBootStrategy(Strategy):
    """Strategy TBD"""
    bindings = {
        "power": "PowerProtocol",
        "console": "ConsoleProtocol",
        "uboot": "UBootDriver",
        "setup_shell": "ShellDriver",
        "setup_ssh": "SSHDriver",
        "test_shell": "ShellDriver",
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        self.logger = logging.getLogger(f"{self}")

        config = self.target.env.config

        self.testpath = config.get_path('test')
        self.kernel = config.get_image_path('kernel')
        self.dtb = config.get_image_path('dtb')

        # root.cpio is optional: kernel may already include initramfs
        if config.data['images'].get('rootfs', '') != '':
            self.rootfs = config.get_image_path('rootfs')
        else:
            self.rootfs = None

    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.status:
            return
        elif status == Status.off:
            self.target.deactivate(self.console)
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.setup:
            self.transition(Status.off)
            self.target.activate(self.console)
            self.power.cycle()
            self.target.activate(self.setup_shell)
            self.setup_shell.run("echo 'SETUP BOOT'")

            self.target.activate(self.setup_ssh)

            self.setup_ssh.put(self.kernel, self.testpath)
            self.setup_ssh.put(self.dtb, self.testpath)
            if self.rootfs:
                self.setup_ssh.put(self.rootfs, self.testpath)

            self.target.deactivate(self.setup_ssh)
            self.setup_shell.run("sync")
            self.setup_shell.run("sync")
        elif status == Status.uboot:
            self.transition(Status.setup)
            self.target.activate(self.console)
            # cycle power
            self.power.cycle()
            # interrupt uboot
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.transition(Status.uboot)
            self.uboot.boot("")
            self.uboot.await_boot()
            self.target.activate(self.test_shell)
            self.test_shell.run("echo 'TEST BOOT'")
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.activate(self.power)
        elif status == Status.setup:
            self.target.activate(self.setup_shell)
        elif status == Status.uboot:
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.target.activate(self.test_shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
