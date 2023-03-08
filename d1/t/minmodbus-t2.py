#!/usr/bin/env python

import minimalmodbus
import time


def relay_status(instrument):
    # request all relays status
    state = instrument.read_bits(0, 8, 1)
    print("relays: {}".format(':'.join("ON" if x else "OFF" for x in state)))
    time.sleep(1)


# test2: turn relays on/off

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1, minimalmodbus.MODE_RTU)
instrument.serial.baudrate = 9600
instrument.serial.timeout = 0.5

relay_status(instrument)

# turn on relay 5
instrument.write_bit(5, 1, 5)
time.sleep(1)

relay_status(instrument)

# turn on relay 7
instrument.write_bit(7, 1, 5)
time.sleep(1)

relay_status(instrument)

# turn off relay 7
instrument.write_bit(7, 0, 5)
time.sleep(1)

relay_status(instrument)

# turn off relay 5
instrument.write_bit(5, 0, 5)
time.sleep(1)

instrument.serial.close()
