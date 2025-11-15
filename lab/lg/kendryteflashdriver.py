import attr

from labgrid.exceptions import InvalidConfigError
from labgrid.factory import target_factory
from labgrid.driver import Driver

from labgrid.util.managedfile import ManagedFile
from labgrid.util.helper import processwrapper


@target_factory.reg_driver
@attr.s(eq=False)
class KendryteFlashDriver(Driver):
    bindings = {
        "device": {
            "SerialPort",
            "NetworkSerialPort",
        }
    }

    flasher = attr.ib(
        default='kflash',
        validator=attr.validators.optional(attr.validators.instance_of(str)),
    )

    board = attr.ib(
        default='bit_mic',
        validator=attr.validators.instance_of(str)
    )

    baudrate = attr.ib(
        default=1500000,
        validator=attr.validators.instance_of(int)
    )

    image = attr.ib(
        default=None,
        validator=attr.validators.instance_of(str)
    )

    prompt = attr.ib(
        default='The ISP stub tells us the k210 is rebooting ...',
        validator=attr.validators.instance_of(str)
    )

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.image is None:
            raise InvalidConfigError("Image is not specified")

    def on_activate(self):
        cmd = [self.flasher, '--version']
        self.logger.info("Running version command '%s'", " ".join(cmd))
        processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True)

    def on_deactivate(self):
        pass

    @Driver.check_active
    def flash(self):
        """
        Use Kendryte kflash to write binary to the SPI flash on Sipeed K210 boards
        """
        image = self.target.env.config.get_image_path(self.image)
        mf = ManagedFile(image, self.device)
        mf.sync_to_resource()
        remote_image = mf.get_remote_path()

        # kflash -b 1500000 -B bit_mic -p /dev/ttyUSB1 /path/to/loader.bin
        cmd = [self.flasher, '-B', self.board, '-b', str(self.baudrate), '-p', self.device.extra.get("path"), remote_image]
        self.logger.info(f"Running exec command {cmd}")
        output = processwrapper.check_output(self.device.command_prefix + cmd, print_on_silent_log=True).decode('ascii')

        if self.prompt:
            assert self.prompt in output
