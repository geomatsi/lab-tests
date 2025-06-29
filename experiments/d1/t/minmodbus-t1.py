#!/usr/bin/env python

import minimalmodbus
import time


instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1, minimalmodbus.MODE_RTU)
instrument.serial.baudrate = 9600
instrument.serial.timeout = 0.5

# test1: read relays and pins status

# read input pins
state = instrument.read_bits(0, 8, 2)
print("pins: {}".format(':'.join("HIGH" if x else "LOW" for x in state)))
time.sleep(1)

# request all relays status
state = instrument.read_bits(0, 8, 1)
print("relays: {}".format(':'.join("ON" if x else "OFF" for x in state)))
time.sleep(1)

# request relays status one by one
for r in range(0, 8):
    state = instrument.read_bit(r, 1)
    print("relay #{}: {}".format(r, "ON" if state else "OFF"))
    time.sleep(1)

instrument.serial.close()
