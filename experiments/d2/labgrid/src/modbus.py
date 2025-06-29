#!/usr/bin/env python3

from importlib import import_module

import socket
import time
import attr

from labgrid.driver import Driver
from labgrid.factory import target_factory
from labgrid.protocol import PowerProtocol
from labgrid.step import step
from labgrid.util.proxy import proxymanager


@target_factory.reg_driver
@attr.s(eq=False)
class ModbusTCPPowerDriver(Driver, PowerProtocol):
    bindings = {"coil": "ModbusTCPCoil", }

    downtime = attr.ib(default=1.0, validator=attr.validators.instance_of(float))
    delay = attr.ib(default=0.5, validator=attr.validators.instance_of(float))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self._modbus = import_module('umodbus.client.tcp')
        self.sock = None

    def on_activate(self):
        # we can only forward if the backend knows which port to use
        host, port = proxymanager.get_host_and_port(self.coil, default_port=502)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))

    def on_deactivate(self):
        self.sock.close()

    @Driver.check_active
    @step()
    def on(self):
        value = (self.coil.coil << 8 | self.coil.coil)
        req = self._modbus.write_single_register(slave_id=1, address=2, value=value)
        self._modbus.send_message(req, self.sock)
        time.sleep(self.delay)

    @Driver.check_active
    @step()
    def off(self):
        value = (self.coil.coil << 8)
        req = self._modbus.write_single_register(slave_id=1, address=2, value=value)
        self._modbus.send_message(req, self.sock)
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
        req = self._modbus.read_holding_registers(slave_id=1, starting_address=1, quantity=1)
        rsp = self._modbus.send_message(req, self.sock)
        return int(rsp[0]) & self.coil.coil
