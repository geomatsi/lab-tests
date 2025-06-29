#!/usr/bin/env python

""" Modbus RTU management tool v2 """

import minimalmodbus
import argparse
import time
import sys


def get_instrument(name, id, verbose):
    """ Return Instrument instance, ready to use for RS485"""
    instrument = minimalmodbus.Instrument(name, id, minimalmodbus.MODE_RTU)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 0.5
    instrument.debug = verbose
    return instrument


def cmd_relay(args):
    """ command: relay control """
    instrument = get_instrument(args.device, args.server, args.verbose)

    if hasattr(args, 'on'):
        instrument.write_bit(args.on, 1, 5)
        instrument.serial.close()
        sys.exit(0)

    if hasattr(args, 'off'):
        instrument.write_bit(args.off, 0, 5)
        instrument.serial.close()
        sys.exit(0)

    if hasattr(args, 'flip'):
        state = instrument.read_bit(args.flip, 1)
        time.sleep(0.5)
        instrument.write_bit(args.flip, 0 if state else 1, 5)
        instrument.serial.close()
        sys.exit(0)

    if hasattr(args, 'read'):
        state = instrument.read_bit(args.read, 1)
        if args.text:
            print(format("ON" if state else "OFF"))
        else:
            print(state)
        instrument.serial.close()
        sys.exit(0)

    sys.exit(0)


def cmd_relays(args):
    """ command: control all relays at once """
    instrument = get_instrument(args.device, args.server, args.verbose)

    if hasattr(args, 'action'):
        if args.action == 'read':
            state = instrument.read_bits(0, 8, 1)
            if args.text:
                print(format(':'.join("ON" if x else "OFF" for x in state)))
            else:
                print(state)
        elif args.action == 'on':
            instrument.write_bits(0, [1, 1, 1, 1, 1, 1, 1, 1])
        elif args.action == 'off':
            instrument.write_bits(0, [0, 0, 0, 0, 0, 0, 0, 0])
        elif args.action == 'flip':
            state = instrument.read_bits(0, 8, 1)
            time.sleep(0.5)
            instrument.write_bits(0,  [0 if x else 1 for x in state])
        else:
            print("unsupported action: {}", args.action)

    instrument.serial.close()
    sys.exit(0)


def cmd_pins(args):
    """ command: read input pins"""
    instrument = get_instrument(args.device, args.server, args.verbose)
    state = instrument.read_bits(0, 8, 2)
    if args.pin is not None:
        print(state[args.pin])
    else:
        print(state)

    instrument.serial.close()
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
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                              dest='verbose', help='verbose mode')

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
    supported_actions = ['read', 'on', 'off', 'flip']
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
