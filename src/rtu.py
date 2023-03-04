#!/usr/bin/env python

""" Modbus RTU management tool """

import argparse
import sys

from serial import Serial, PARITY_NONE
from umodbus.client.serial import rtu
from umodbus.exceptions import IllegalDataValueError


def get_serial_port(name):
    """ Return serial.Serial instance, ready to use for RS485."""
    port = Serial(port=name, baudrate=9600, parity=PARITY_NONE,
                  stopbits=1, bytesize=8, timeout=1)
    return port


def cmd_relay(args):
    """ command: relay control """
    serial_port = get_serial_port('/dev/ttyUSB0')

    if hasattr(args, 'on'):
        req = rtu.write_single_coil(slave_id=args.device, address=args.on, value=0xff00)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rtu.send_message(req, serial_port)
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'off'):
        req = rtu.write_single_coil(slave_id=args.device, address=args.off, value=0)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rtu.send_message(req, serial_port)
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'flip'):
        # For some reason write_single_coil throws IllegalDataValueError exception:
        # req = rtu.write_single_coil(slave_id=args.device, address=args.flip, value=0x5500)
        reqs = [
            b'\x01\x05\x00\x00\x55\x00\xf2\x9a',
            b'\x01\x05\x00\x01\x55\x00\xa3\x5a',
            b'\x01\x05\x00\x02\x55\x00\x53\x5a',
            b'\x01\x05\x00\x03\x55\x00\x02\x9a',
            b'\x01\x05\x00\x04\x55\x00\xb3\x5b',
            b'\x01\x05\x00\x05\x55\x00\xe2\x9b',
            b'\x01\x05\x00\x06\x55\x00\x12\x9b',
            b'\x01\x05\x00\x07\x55\x00\x43\x5b'
        ]

        req = reqs[args.flip]
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        try:
            rtu.send_message(req, serial_port)
        except IllegalDataValueError:
            pass
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'read'):
        req = rtu.read_coils(slave_id=args.device, starting_address=args.read, quantity=1)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rsp = rtu.send_message(req, serial_port)
        if args.text:
            print(format("ON" if rsp[0] else "OFF"))
        else:
            print(rsp[0])
        serial_port.close()
        sys.exit(0)

    sys.exit(0)


def cmd_pins(args):
    """ command: read input pins"""
    serial_port = get_serial_port('/dev/ttyUSB0')

    req = rtu.read_discrete_inputs(slave_id=args.device, starting_address=0, quantity=8)
    print("request: {}".format(':'.join(format(x, '02x') for x in req)))
    rsp = rtu.send_message(req, serial_port)

    if args.pin is not None:
        print(rsp[args.pin])
    else:
        print(rsp)

    serial_port.close()
    sys.exit(0)


def cmd_scan(args):
    """ command: scan modbus rtu device address """
    serial_port = get_serial_port('/dev/ttyUSB0')

    req = rtu.read_holding_registers(slave_id=0, starting_address=0, quantity=1)
    print("request: {}".format(':'.join(format(x, '02x') for x in req)))
    rsp = rtu.send_message(req, serial_port)
    print(rsp[0])

    serial_port.close()
    sys.exit(0)


def create_parser():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    # scan command
    scan_parser = subparsers.add_parser('scan', help='scan modbus rtu device address')
    scan_parser.set_defaults(func=cmd_scan)

    # input pins command
    pins_parser = subparsers.add_parser('pins', help='read input pins')
    pins_parser.add_argument('-d', '--device', action='store', type=int, default=1, required=False,
                              dest='device', help='modbus rtu device address')
    supported_pins = [0, 1, 2, 3, 4, 5, 6, 7]
    pins_parser.add_argument('-p', '--pin', action='store', type=int, choices=supported_pins,
                             required=False, dest='pin', help='select input pin')
    pins_parser.set_defaults(func=cmd_pins)

    # relay commands
    relay_parser = subparsers.add_parser('relay', help='relay commands')
    relay_subparsers = relay_parser.add_subparsers(help='commands')

    relay_parser.add_argument('-d', '--device', action='store', type=int, default=1, required=False,
                              dest='device', help='modbus rtu device address')

    supported_relays = [0, 1, 2, 3, 4, 5, 6, 7]

    enable_parser = relay_subparsers.add_parser('on', help='turn on relay')
    enable_parser.add_argument('on', action='store', type=int, choices=supported_relays,
                             help='relay number')

    disable_parser = relay_subparsers.add_parser('off', help='turn off relay')
    disable_parser.add_argument('off', action='store', type=int, choices=supported_relays,
                             help='relay number')

    flip_parser = relay_subparsers.add_parser('flip', help='flip relay state')
    flip_parser.add_argument('flip', action='store', type=int, choices=supported_relays,
                             help='relay number')

    read_parser = relay_subparsers.add_parser('read', help='read relay state')
    read_parser.add_argument('read', action='store', type=int, choices=supported_relays,
                             help='relay number')
    read_parser.add_argument('--text', action='store_true', required=False, dest='text',
                              help='report relay status in text form')

    relay_parser.set_defaults(func=cmd_relay)

    return parser


if __name__ == '__main__':
    cmdline = create_parser()
    ns = cmdline.parse_args()
    if not hasattr(ns, 'func'):
        cmdline.print_help()
        sys.exit(-1)
    ns.func(ns)
