#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--arch', help='Targeted architecture', type=str, default='amd64')
    parser.add_argument('-B', '--binary', help='Binary name', type=str, required=True)
    parser.add_argument('-L', '--libc', help='Libc name', type=str)
    parser.add_argument('-O', '--os', help='Operating System', type=str, default='linux')
    parser.add_argument('-E', '--endian', help='Endianness', type=str, default='little')
    parser.add_argument('-R', '--remote', help='Remote host', type=str)
    parser.add_argument('-P', '--port', help='Remote port', type=int)
    args = parser.parse_args()
    if args.remote is set and args.port is None or args.port is set and args.remote is None:
        parser.error("--remote and --port are required.")

    scheme="""#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from pwn import *
import os


context(arch="{}", os="{}", endian="{}")
context.log_level="DEBUG"


class Pwn:
    def __init__(self):
        self.e = ELF("./{}")
""".format(args.arch, args.os, args.endian, args.binary)
    if args.libc:
        scheme+="""        self.libc = ELF("./{}")
""".format(args.libc)
    scheme+="""        self.p = None

    def start_binary(self):
"""
    if args.libc:
        scheme+="""        self.p = process("./{}", env={{
            "LD_PRELOAD": "{}"
        }})
""".format(args.binary, args.libc)
    else:
        scheme+="""        self.p = process("./{}")
""".format(args.binary)
    if args.remote:
        scheme+="""        #self.p = remote("{}", {})
""".format(args.remote, args.port)
    scheme+="""        self.p.recvuntil("...")

    def pwn_binary(self):
        self.start_binary()

        self.p.interactive()
        self.p.close()


def main():
    pwn = Pwn()
    pwn.pwn_binary()


if __name__ == "__main__":
    main()
"""

    exploit_name="exploit_{}.py".format(args.binary)
    with open(exploit_name, 'w+') as file:
        file.write(scheme)


if __name__ == "__main__":
    main()
