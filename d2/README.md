# [Dingtian 2-channel Relay Board](https://www.dingtian-tech.com/en_us/relay2.html)

![alt text](docs/ps0.jpg)

## Using modbus-cli tool

Project: https://github.com/favalex/modbus-cli

Command line `modbus-cli` is a tool to access both Modbus-RTU and Modbus-TCP
devices from the command line.

<details>
<summary>Examples of board control over Modbus-TCP using modbus-cli tool</summary>

### Read number of relay channels

```bash
$ modbus -v 192.168.1.100 h@0
Parsed 0 registers definitions from 1 files
→ < f0 f9 00 00 00 06 ff 03 00 00 00 01 >
← < f0 f9 00 00 00 05 ff 03 02 00 02 > 11 bytes
← [2]
0: 2 0x2
```

### Read relays status

```bash
$ modbus -v 192.168.1.100 h@1
Parsed 0 registers definitions from 1 files
→ < 12 ff 00 00 00 06 ff 03 00 01 00 01 >
← < 12 ff 00 00 00 05 ff 03 02 00 01 > 11 bytes
← [1]
1: 1 0x1
```

### Control relays

Command format is 2 bytes:
* the first byte is the relays mask
* the second byte is the requested state

Turn off both relays and check status:

```bash
$ modbus -v 192.168.1.100 h@2=0x0300
Parsed 0 registers definitions from 1 files
→ < 34 d4 00 00 00 06 ff 06 00 02 03 00 >
← < 34 d4 00 00 00 06 ff 06 00 02 03 00 > 12 bytes

$ modbus -v 192.168.1.100 h@1
Parsed 0 registers definitions from 1 files
→ < f6 a0 00 00 00 06 ff 03 00 01 00 01 >
← < f6 a0 00 00 00 05 ff 03 02 00 00 > 11 bytes
← [0]
1: 0 0x0
```

Turn on both relays and check status:

```bash
$ modbus -v 192.168.1.100 h@2=0x0303
Parsed 0 registers definitions from 1 files
→ < dc 55 00 00 00 06 ff 06 00 02 03 03 >
← < dc 55 00 00 00 06 ff 06 00 02 03 03 > 12 bytes

$ modbus -v 192.168.1.100 h@1
Parsed 0 registers definitions from 1 files
→ < e3 ad 00 00 00 06 ff 03 00 01 00 01 >
← < e3 ad 00 00 00 05 ff 03 02 00 03 > 11 bytes
← [3]
1: 3 0x3
```

Turn off 1st relay and check status:

```bash
$ modbus -v 192.168.1.100 h@2=0x0100
Parsed 0 registers definitions from 1 files
→ < 25 a1 00 00 00 06 ff 06 00 02 01 00 >
← < 25 a1 00 00 00 06 ff 06 00 02 01 00 > 12 byte

$ modbus -v 192.168.1.100 h@1
Parsed 0 registers definitions from 1 files
→ < b7 8e 00 00 00 06 ff 03 00 01 00 01 >
← < b7 8e 00 00 00 05 ff 03 02 00 02 > 11 bytes
← [2]
1: 2 0x2
```

Turn on 1st relay and turn off 2nd relay and check status:

```bash
$ modbus -v 192.168.1.100 h@2=0x301
Parsed 0 registers definitions from 1 files
→ < e0 dc 00 00 00 06 ff 06 00 02 03 01 >
← < e0 dc 00 00 00 06 ff 06 00 02 03 01 > 12 bytes

$ modbus -v 192.168.1.100 h@1
Parsed 0 registers definitions from 1 files
→ < 8c ff 00 00 00 06 ff 03 00 01 00 01 >
← < 8c ff 00 00 00 05 ff 03 02 00 01 > 11 bytes
← [1]
1: 1 0x1
```
</details>

## Using Custom CLI tool

This repository provides a simple example command line tool [rtu.py](src/rtu.py) for this specific device.
The tool is based on [umodbus](https://umodbus.readthedocs.io/) library.
  
<details>
<summary>Examples of board control over Modbus-TCP using custom tool</summary>

```bash
$ ./src/rtu.py
usage: rtu.py [-h] [-s SERVER] [-p PORT] [-v] {relay,relays} ...

positional arguments:
  {relay,relays}        commands
    relay               relay commands
    relays              multi-relays commands

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Modbus TCP server IP address
  -p PORT, --port PORT  Modbus TCP server port
  -v, --verbose         verbose mode
```

Basic relay functions:

```bash
$ ./src/rtu.py relay -h                                                                                                                                                                                                                                                           255 ↵
usage: rtu.py relay [-h] {on,off,flip,read} ...

positional arguments:
  {on,off,flip,read}  commands
    on                turn on relay
    off               turn off relay
    flip              flip relay state
    read              read relay state

options:
  -h, --help          show this help message and exit

$ ./src/rtu.py -s 192.168.1.100 relay on 1

$ ./src/rtu.py -s 192.168.1.100 relay read 1
1

$ ./src/rtu.py -s 192.168.1.100 relay flip 2

$ ./src/rtu.py -s 192.168.1.100 relay read 2 --text
ON
```

Basic all-relays functions:

```bash
$ ./src/rtu.py relays -h
usage: rtu.py relays [-h] [--text] {read,on,off,flip}

positional arguments:
  {read,on,off,flip}  multi-relays command

options:
  -h, --help          show this help message and exit
  --text              report relays status in text form

$ ./src/rtu.py -s 192.168.1.100 relays read --text
ON:OFF

$ ./src/rtu.py -s 192.168.1.100 relays flip

$ ./src/rtu.py -s 192.168.1.100 relays read
[0, 1]

$ ./src/rtu.py -s 192.168.1.100 relays off

$ ./src/rtu.py -s 192.168.1.100 relays read
[0, 0]
```
</details>
