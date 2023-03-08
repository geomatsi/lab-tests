#!/usr/bin/env python

import minimalmodbus
import time


def relay_status(instrument):
    # request all relays status
    state = instrument.read_bits(0, 8, 1)
    print("relays: {}".format(':'.join("ON" if x else "OFF" for x in state)))
    time.sleep(1)


# test3: control multiple relays in one command

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1, minimalmodbus.MODE_RTU)
instrument.serial.baudrate = 9600
instrument.serial.timeout = 0.5

relay_status(instrument)

# turn on all relays
instrument.write_bits(0, [1, 1, 1, 1, 1, 1, 1, 1])
time.sleep(1)

relay_status(instrument)

# turn on relays 0..3
instrument.write_bits(0, [1, 1, 1, 1, 0, 0, 0, 0])
time.sleep(1)

relay_status(instrument)

# turn on relays 4..7
instrument.write_bits(0, [0, 0, 0, 0, 1, 1, 1, 1])
time.sleep(1)

relay_status(instrument)

# turn off all relays
instrument.write_bits(0, [0, 0, 0, 0, 0, 0, 0, 0])
time.sleep(1)

relay_status(instrument)

instrument.serial.close()
