import attr

from labgrid.exceptions import InvalidConfigError
from labgrid.factory import target_factory
from labgrid.driver import Driver

from labgrid.util.managedfile import ManagedFile
from labgrid.util.helper import processwrapper


@target_factory.reg_driver
@attr.s(eq=False)
class SunxiFELDriver(Driver):
    bindings = {
        "device": {
            "USBFlashableDevice",
            "NetworkUSBFlashableDevice",
        },
        "console": {
            "ConsoleProtocol",
        }
    }

    flasher = attr.ib(
        default='xfel',
        validator=attr.validators.optional(attr.validators.instance_of(str)),
    )

    dram_type = attr.ib(
        default=None,
        validator=attr.validators.instance_of(str)
    )

    dram_prompt = attr.ib(
        default=None,
        validator=attr.validators.instance_of(str)
    )

    images = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(dict)),
    )

    exec = attr.ib(
        default=None,
        validator=attr.validators.optional(attr.validators.instance_of(str)),
    )

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.exec is None:
            raise InvalidConfigError("Start execution address is not specified")

    def on_activate(self):
        cmd = [self.flasher, 'version']
        self.logger.info("Running version command '%s'", " ".join(cmd))
        processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True)

    def on_deactivate(self):
        pass

    @Driver.check_active
    def flash(self):
        """
        Use Sunxi FEL to load binaries and start execution
        """
        if self.dram_type:
            cmd = [self.flasher, 'ddr', self.dram_type]
            self.logger.info("Running dram setup command '%s'", " ".join(cmd))
            processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True)
            if self.dram_prompt:
                self.console.expect(self.dram_prompt)

        if self.images:
            for image, addr in self.images.items():
                image = self.target.env.config.get_image_path(image)
                mf = ManagedFile(image, self.device)
                mf.sync_to_resource()
                remote_image = mf.get_remote_path()

                cmd = [self.flasher, 'write', addr, remote_image]
                self.logger.info("Running exec command '%s'", " ".join(cmd))
                processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True)

        if self.exec:
            cmd = [self.flasher, 'exec', self.exec]
            self.logger.info("Running exec command '%s'", " ".join(cmd))
            processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True)
