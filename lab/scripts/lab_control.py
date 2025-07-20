#!/usr/bin/env python

import argparse
import pathlib
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from labgrid import Environment
from lg.modbus import ModbusTCPPowerDriver


def cmd_power(args):
    """ command: control lab slots power supplies"""

    env = Environment(args.conf)
    tgt = env.get_target(args.slot)
    pwr = tgt.get_driver("PowerProtocol")

    if hasattr(args, 'action'):
        if args.action == 'on':
            print(f"{args.slot}: pwr on")
            pwr.on()
        elif args.action == 'off':
            print(f"{args.slot}: pwr off")
            pwr.off()
        elif args.action == 'cycle':
            print(f"{args.slot}: pwr cycle")
            pwr.cycle()
        elif args.action == 'get':
            print(f"{args.slot}: pwr {"on" if pwr.get() else "off"}")
        else:
            print("unsupported action: {}", args.action)

    sys.exit(0)


def create_parser():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    # global options
    parser.add_argument('-c', '--configuration', action='store', type=str,
                        default="workspace/test.yaml", required=False,
                        dest='conf', help='Lab configuration file')
    parser.add_argument('-s', '--slot', action='store', type=str, default="slot2",
                        required=False, dest='slot', help='Lab test slot')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                              dest='verbose', help='verbose mode')

    # slot power commands
    power_parser = subparsers.add_parser('power', help='slot power commands')
    supported_actions = ['on', 'off', 'cycle', 'get']
    power_parser.add_argument('action', action='store', type=str,
                              choices=supported_actions, help='slot power command command')
    power_parser.set_defaults(func=cmd_power)

    return parser


if __name__ == "__main__":

    cmdline = create_parser()
    ns = cmdline.parse_args()

    if not pathlib.Path(ns.conf).is_file():
        print(f"Data file does not exists: {ns.conf}")
        sys.exit(-1)

    if not hasattr(ns, 'func'):
        cmdline.print_help()
        sys.exit(-1)

    ns.func(ns)
