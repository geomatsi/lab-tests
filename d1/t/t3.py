#!/usr/bin/env python

import time

from serial import Serial, PARITY_NONE
from umodbus.client.serial import rtu


def get_serial_port(name):
    """ Return serial.Serial instance, ready to use for RS485."""
    port = Serial(port=name, baudrate=9600, parity=PARITY_NONE,
                  stopbits=1, bytesize=8, timeout=1)
    # Note: the following rs485 devices work right out of the box w/o additional fcntl settings:
    # - https://aliexpress.ru/item/33054455522.html
    # - https://aliexpress.ru/item/1005002115304015.html

    return port


# test3: enable/disable relays

serial_port = get_serial_port('/dev/ttyUSB0')

# turn on relay 7
req = rtu.write_single_coil(slave_id=1, address=7, value=0xff00)
print("request: {}".format(':'.join(format(x, '02x') for x in req)))
rsp = rtu.send_message(req, serial_port)
print("response: {}".format(rsp))
time.sleep(1)

# read all relays status
req = rtu.read_coils(slave_id=1, starting_address=0, quantity=8)
print("request: {}".format(':'.join(format(x, '02x') for x in req)))
rsp = rtu.send_message(req, serial_port)
print("response: {}".format(':'.join("ON" if x else "OFF" for x in rsp)))
time.sleep(3)

# turn off relay 7
req = rtu.write_single_coil(slave_id=1, address=7, value=0x0)
print("request: {}".format(':'.join(format(x, '02x') for x in req)))
rsp = rtu.send_message(req, serial_port)
print("response: {}".format(rsp))

serial_port.close()
