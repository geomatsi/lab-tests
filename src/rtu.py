#!/usr/bin/env python

""" Modbus RTU management tool """

import argparse
import sys

from serial import Serial, PARITY_NONE
from umodbus.client.serial import rtu
from umodbus.exceptions import IllegalDataValueError
import umodbus.client.serial.redundancy_check as crc


def get_serial_port(name):
    """ Return serial.Serial instance, ready to use for RS485."""
    port = Serial(port=name, baudrate=9600, parity=PARITY_NONE,
                  stopbits=1, bytesize=8, timeout=1)
    return port


def cmd_relay(args):
    """ command: relay control """
    serial_port = get_serial_port(args.device)

    if hasattr(args, 'on'):
        req = rtu.write_single_coil(slave_id=args.server, address=args.on, value=0xff00)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rtu.send_message(req, serial_port)
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'off'):
        req = rtu.write_single_coil(slave_id=args.server, address=args.off, value=0)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rtu.send_message(req, serial_port)
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'flip'):
        # flip command value b'\x55\x00' is not compliant with modbus spec
        # so create request manually to avoid umodbus exception 
        req = crc.add_crc(bytes([args.server]) + b'\x05\x00' + bytes([args.flip]) + b'\x55\x00')
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        try:
            rtu.send_message(req, serial_port)
        except IllegalDataValueError:
            pass
        serial_port.close()
        sys.exit(0)

    if hasattr(args, 'read'):
        req = rtu.read_coils(slave_id=args.server, starting_address=args.read, quantity=1)
        print("request: {}".format(':'.join(format(x, '02x') for x in req)))
        rsp = rtu.send_message(req, serial_port)
        if args.text:
            print(format("ON" if rsp[0] else "OFF"))
        else:
            print(rsp[0])
        serial_port.close()
        sys.exit(0)

    sys.exit(0)


def cmd_relays(args):
    """ command: control all relays at once """
    serial_port = get_serial_port(args.device)

    if hasattr(args, 'action'):
        if args.action == 'read':
            req = rtu.read_coils(slave_id=args.server, starting_address=0, quantity=8)
            print("request: {}".format(':'.join(format(x, '02x') for x in req)))
            rsp = rtu.send_message(req, serial_port)
            if args.text:
                print(format(':'.join("ON" if x else "OFF" for x in rsp)))
            else:
                print(rsp)
        elif args.action == 'flip':
            # flip-all command value b'\x5a\x00' is not compliant with modbus spec
            # so create request manually to avoid umodbus exception 
            req = crc.add_crc(bytes([args.server]) + b'\x05\x00\x00\x5a\x00')
            print("request: {}".format(':'.join(format(x, '02x') for x in req)))
            try:
                rtu.send_message(req, serial_port)
            except IllegalDataValueError:
                pass
        else:
            print("unsupported action: {}", args.action)

    serial_port.close()
    sys.exit(0)


def cmd_pins(args):
    """ command: read input pins"""
    serial_port = get_serial_port(args.device)

    req = rtu.read_discrete_inputs(slave_id=args.server, starting_address=0, quantity=8)
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
    serial_port = get_serial_port(args.device)

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

    # global options
    parser.add_argument('-d', '--device', action='store', type=str, default='/dev/ttyUSB0',
                        required=False, dest='device', help='serial device for modbus connection')
    parser.add_argument('-s', '--server', action='store', type=int, default=1, required=False,
                              dest='server', help='modbus rtu server address')

    # scan command
    scan_parser = subparsers.add_parser('scan', help='scan modbus rtu device address')
    scan_parser.set_defaults(func=cmd_scan)

    # input pins command
    pins_parser = subparsers.add_parser('pins', help='read input pins')
    supported_pins = [0, 1, 2, 3, 4, 5, 6, 7]
    pins_parser.add_argument('-p', '--pin', action='store', type=int, choices=supported_pins,
                             required=False, dest='pin', help='select input pin')
    pins_parser.set_defaults(func=cmd_pins)

    # relay commands
    relay_parser = subparsers.add_parser('relay', help='relay commands')
    relay_subparsers = relay_parser.add_subparsers(help='commands')

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

    # relays command
    relays_parser = subparsers.add_parser('relays', help='multi-relays commands')
    relays_parser.add_argument('--text', action='store_true', required=False,
                               dest='text', help='report relays status in text form')
    supported_actions = ['read', 'flip']
    relays_parser.add_argument('action', action='store', type=str,
                               choices=supported_actions, help='multi-relays command')

    relays_parser.set_defaults(func=cmd_relays)

    return parser


if __name__ == '__main__':
    cmdline = create_parser()
    ns = cmdline.parse_args()
    if not hasattr(ns, 'func'):
        cmdline.print_help()
        sys.exit(-1)
    ns.func(ns)
