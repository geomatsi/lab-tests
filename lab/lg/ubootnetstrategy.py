import enum
import attr
import logging


from labgrid.factory import target_factory
from labgrid.strategy import Strategy, StrategyError


class Status(enum.Enum):
    unknown = 0
    off = 1
    uboot = 2
    shell = 3


@target_factory.reg_driver
@attr.s(eq=False)
class UBootNetStrategy(Strategy):
    """Strategy to boot to U-Boot, download Linux/rootfs via TFTP and finally boot to shell"""
    bindings = {
        "power": "PowerProtocol",
        "console": "ConsoleProtocol",
        "uboot": "UBootDriver",
        "shell": "ShellDriver",
        "tftp": "TFTPProviderDriver"
    }

    status = attr.ib(default=Status.unknown)
    late_console = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(bool))
    )

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        self.logger = logging.getLogger(f"{self}")

        config = self.target.env.config

        if config.data['images'].get('kernel', '') != '':
            self.kernel = config.get_image_path('kernel')
        else:
            self.kernel = None

        if config.data['images'].get('dtb', '') != '':
            self.dtb = config.get_image_path('dtb')
        else:
            self.dtb = None

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
            self.target.deactivate_all_drivers()
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.uboot:
            self.transition(Status.off)
            if not self.late_console:
                self.target.activate(self.console)
            # cycle power
            self.power.cycle()
            if self.late_console:
                # wait for serial device to appear after power-on
                self.target.await_resources(self.target.resources)
                self.target.activate(self.console)
            # interrupt uboot
            self.target.activate(self.uboot)
        elif status == Status.shell:
            # transition to uboot
            self.transition(Status.uboot)

            self.target.activate(self.tftp)

            # copy Linux kernel to tftp directory on exporter if it exists
            if self.kernel:
                self.tftp.stage(self.kernel)

            # copy Linux DTB to tftp directory on exporter if it exists
            if self.dtb:
                self.tftp.stage(self.dtb)

            # copy Linux rootfs to tftp directory on exporter if it exists
            if self.rootfs:
                self.tftp.stage(self.rootfs)

            self.uboot.boot("")
            self.uboot.await_boot()
            self.target.activate(self.shell)
            self.shell.run("systemctl is-system-running --wait")
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.deactivate_all_drivers()
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.uboot:
            self.target.activate(self.console)
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
