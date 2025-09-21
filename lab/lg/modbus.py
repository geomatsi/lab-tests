#!/usr/bin/env python3

from importlib import import_module

import functools
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

    retry_delay = attr.ib(default=1.0, validator=attr.validators.instance_of(float))
    retries = attr.ib(default=3, validator=attr.validators.instance_of(int))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self._modbus = import_module('umodbus.client.tcp')
        self.sock = None
        self.port = 0
        self.host = 0

    def modbus_connect(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # try to connect to Modbus TCP server with retries
            sock = None
            for t in range(1, self.retries + 1):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self.host, int(self.port)))
                    break
                except OSError as e:
                    sock.close()

                    if t < self.retries:
                        time.sleep(self.retry_delay)
                    else:
                        raise e

            try:
                self.sock = sock
                # ready to go: perform the requested power mgmt operation
                func(self, *args, **kwargs)
            finally:
                self.sock.close()
                self.sock = None

        return wrapper

    def on_activate(self):
        # we can only forward if the backend knows which port to use
        self.host, self.port = proxymanager.get_host_and_port(self.coil, default_port=502)

    def on_deactivate(self):
        if self.sock:
            self.sock.close()

    @Driver.check_active
    @step()
    @modbus_connect
    def on(self):
        value = (((1 << self.coil.coil) << 8) | (1 << self.coil.coil))
        req = self._modbus.write_single_register(slave_id=1, address=2, value=value)
        self._modbus.send_message(req, self.sock)
        time.sleep(self.delay)

    @Driver.check_active
    @step()
    @modbus_connect
    def off(self):
        value = ((1 << self.coil.coil) << 8)
        req = self._modbus.write_single_register(slave_id=1, address=2, value=value)
        self._modbus.send_message(req, self.sock)
        time.sleep(self.delay)

    @Driver.check_active
    @step()
    @modbus_connect
    def get(self):
        req = self._modbus.read_holding_registers(slave_id=1, starting_address=1, quantity=1)
        rsp = self._modbus.send_message(req, self.sock)
        return int(rsp[0]) & (1 << self.coil.coil)

    @Driver.check_active
    @step()
    def cycle(self):
        self.off()
        time.sleep(self.downtime)
        self.on()


