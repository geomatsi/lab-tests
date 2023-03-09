#!/usr/bin/env python3

from importlib import import_module

import time
import attr

from labgrid.driver import Driver
from labgrid.factory import target_factory
from labgrid.protocol import PowerProtocol
from labgrid.step import step


@target_factory.reg_driver
@attr.s(eq=False)
class ModbusRTUPowerDriver(Driver, PowerProtocol):
    bindings = {"resource": "ModbusRTU", }

    downtime = attr.ib(default=1.0, validator=attr.validators.instance_of(float))
    delay = attr.ib(default=0.5, validator=attr.validators.instance_of(float))
    coil = attr.ib(default=0, validator=attr.validators.instance_of(int))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self._modbus = import_module('minimalmodbus')
        self.instrument = None

    def on_activate(self):
        self.instrument = self._modbus.Instrument(
            self.resource.port,
            self.resource.address,
            debug=False)

        self.instrument.serial.baudrate = self.resource.speed
        self.instrument.serial.timeout = self.resource.timeout
        self.instrument.mode = self._modbus.MODE_RTU
        self.instrument.clear_buffers_before_each_transaction = True

    def on_deactivate(self):
        self.instrument = None

    @Driver.check_active
    @step()
    def on(self):
        self.instrument.write_bit(self.coil, 1, 5)
        time.sleep(self.delay)

    @Driver.check_active
    @step()
    def off(self):
        self.instrument.write_bit(self.coil, 0, 5)
        time.sleep(self.delay)

    @Driver.check_active
    @step()
    def cycle(self):
        self.off()
        time.sleep(self.downtime)
        self.on()

    @Driver.check_active
    @step()
    def get(self):
        return self.instrument.read_bit(self.coil, 1)
