import enum
import attr


from labgrid.strategy import Strategy, StrategyError
from labgrid.factory import target_factory
from labgrid.step import step


class Status(enum.Enum):
    unknown = 0
    off = 1
    flash = 2
    shell = 3


@target_factory.reg_driver
@attr.s(eq=False)
class KendryteStrategy(Strategy):
    """Strategy to boot Sunxi boards using FEL"""
    bindings = {
        "power": "PowerProtocol",
        "console": "ConsoleProtocol",
        "flasher": "KendryteFlashDriver",
        "shell": "ShellDriver",
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    @step(args=['status'])
    def transition(self, status, *, step):  # pylint: disable=redefined-outer-name
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.status:
            step.skip("nothing to do")
            return
        elif status == Status.off:
            self.target.deactivate_all_drivers()
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.flash:
            self.transition(Status.off)
            self.power.on()
            # wait for serial device to appear after power-on
            self.target.await_resources(self.target.resources)
            # hack: flush console
            self.target.activate(self.console)
            self.target.deactivate(self.console)
            # now use serial port to flash kendryte board
            self.target.activate(self.flasher)
            self.flasher.flash()
        elif status == Status.shell:
            self.transition(Status.flash)
            self.target.activate(self.console)
            self.target.activate(self.shell)
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    @step(args=['status'])
    def force(self, status, *, step):  # pylint: disable=redefined-outer-name
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not force state {status}")
        if status == Status.off:
            self.target.deactivate_all_drivers()
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.flash:
            self.target.activate(self.flasher)
            self.flasher.flash()
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
