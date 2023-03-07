#!/usr/bin/env python

""" Modbus RTU management tool """

import argparse
import socket
import sys

from umodbus import conf
from umodbus.client import tcp

# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True

REG_STATUS = 1
REG_ACTION = 2


def get_server_sock(server, port):
    """ Return sock, ready to use for Modbus-TCP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))
    return sock


def state_as_list(value):
    res = [1 if digit == '1' else 0 for digit in bin((value & 0x3) + 4)[3:]]
    res.reverse()
    return res


def cmd_relay(args):
    """ command: relay control """
    sock = get_server_sock(args.server, args.port)

    if hasattr(args, 'on'):
        value = (args.on << 8 | args.on)
        req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=value)
        if args.verbose:
            print("req: {}".format(':'.join(format(x, '02x') for x in req)))
        tcp.send_message(req, sock)
        sock.close()
        sys.exit(0)

    if hasattr(args, 'off'):
        value = (args.off << 8)
        req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=value)
        if args.verbose:
            print("req: {}".format(':'.join(format(x, '02x') for x in req)))
        tcp.send_message(req, sock)
        sock.close()
        sys.exit(0)

    if hasattr(args, 'flip'):
        req = tcp.read_holding_registers(slave_id=1, starting_address=REG_STATUS, quantity=1)
        if args.verbose:
            print("req: {}".format(':'.join(format(x, '02x') for x in req)))
        rsp = tcp.send_message(req, sock)
        value = (args.flip << 8) | (~(int(rsp[0]) & args.flip) & 0xff)
        req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=value)
        if args.verbose:
            print("req: {}".format(':'.join(format(x, '02x') for x in req)))
        tcp.send_message(req, sock)
        sock.close()
        sys.exit(0)

    if hasattr(args, 'read'):
        req = tcp.read_holding_registers(slave_id=1, starting_address=REG_STATUS, quantity=1)
        if args.verbose:
            print("req: {}".format(':'.join(format(x, '02x') for x in req)))
        rsp = tcp.send_message(req, sock)
        res = int(rsp[0]) & args.read
        if args.text:
            print(format("ON" if res else "OFF"))
        else:
            print("1" if res else "0")
        sock.close()
        sys.exit(0)

    sys.exit(0)


def cmd_relays(args):
    """ command: control all relays at once """
    sock = get_server_sock(args.server, args.port)

    if hasattr(args, 'action'):
        if args.action == 'read':
            req = tcp.read_holding_registers(slave_id=1, starting_address=REG_STATUS, quantity=1)
            if args.verbose:
                print("req: {}".format(':'.join(format(x, '02x') for x in req)))
            rsp = tcp.send_message(req, sock)
            res = state_as_list(rsp[0])
            if args.text:
                print(format(':'.join("ON" if x else "OFF" for x in res)))
            else:
                print(res)
        elif args.action == 'on':
            req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=0x0303)
            if args.verbose:
                print("req: {}".format(':'.join(format(x, '02x') for x in req)))
            tcp.send_message(req, sock)
        elif args.action == 'off':
            req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=0x0300)
            if args.verbose:
                print("req: {}".format(':'.join(format(x, '02x') for x in req)))
            tcp.send_message(req, sock)
        elif args.action == 'flip':
            req = tcp.read_holding_registers(slave_id=1, starting_address=REG_STATUS, quantity=1)
            if args.verbose:
                print("req: {}".format(':'.join(format(x, '02x') for x in req)))
            rsp = tcp.send_message(req, sock)
            value = 0x0300 | (~rsp[0] & 0x3)
            req = tcp.write_single_register(slave_id=1, address=REG_ACTION, value=value)
            if args.verbose:
                print("req: {}".format(':'.join(format(x, '02x') for x in req)))
            tcp.send_message(req, sock)
        else:
            print("unsupported action: {}", args.action)

    sock.close()
    sys.exit(0)


def create_parser():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    # global options
    parser.add_argument('-s', '--server', action='store', type=str, default='localhost',
                        required=False, dest='server', help='Modbus TCP server IP address')
    parser.add_argument('-p', '--port', action='store', type=int, default=502,
                        required=False, dest='port', help='Modbus TCP server port')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                              dest='verbose', help='verbose mode')

    # relay commands
    relay_parser = subparsers.add_parser('relay', help='relay commands')
    relay_subparsers = relay_parser.add_subparsers(help='commands')

    supported_relays = [1, 2]

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
