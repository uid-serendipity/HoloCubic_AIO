#!/usr/bin/env python
# This file includes the operations with eFuses for ESP32-C3 chip
#
# Copyright (C) 2020 Espressif Systems (Shanghai) PTE LTD
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301 USA.
from __future__ import division, print_function

import argparse

import espsecure

import esptool

from . import fields
from .. import util
from ..base_operations import (add_common_commands, add_force_write_always, burn_bit, burn_block_data, burn_efuse, dump,  # noqa: F401
                               read_protect_efuse, summary, write_protect_efuse)  # noqa: F401


def protect_options(p):
    p.add_argument('--no-write-protect', help='Disable write-protecting of the key. The key remains writable. '
                   '(The keys use the RS coding scheme that does not support post-write data changes. Forced write can damage RS encoding bits.)'
                   ' The write-protecting of keypurposes does not depend on the option, it will be set anyway.', action='store_true')
    p.add_argument('--no-read-protect', help='Disable read-protecting of the key. The key remains readable software.'
                   'The key with keypurpose[USER, RESERVED and *_DIGEST] will remain readable anyway. '
                   'For the rest keypurposes the read-protection will be defined the option (Read-protect by default).', action='store_true')


def add_commands(subparsers, efuses):
    add_common_commands(subparsers, efuses)
    burn_key = subparsers.add_parser('burn_key', help='Burn the key block with the specified name')
    protect_options(burn_key)
    add_force_write_always(burn_key)
    burn_key.add_argument('block', help='Key block to burn', action='append', choices=efuses.BLOCKS_FOR_KEYS)
    burn_key.add_argument('keyfile', help='File containing 256 bits of binary key data', action='append', type=argparse.FileType('rb'))
    burn_key.add_argument('keypurpose', help='Purpose to set.', action='append', choices=fields.EfuseKeyPurposeField.KEY_PURPOSES_NAME)
    for _ in efuses.BLOCKS_FOR_KEYS:
        burn_key.add_argument('block', help='Key block to burn', nargs="?", action='append', metavar="BLOCK", choices=efuses.BLOCKS_FOR_KEYS)
        burn_key.add_argument('keyfile', help='File containing 256 bits of binary key data', nargs="?", action='append', metavar="KEYFILE",
                              type=argparse.FileType('rb'))
        burn_key.add_argument('keypurpose', help='Purpose to set.', nargs="?", action='append', metavar="KEYPURPOSE",
                              choices=fields.EfuseKeyPurposeField.KEY_PURPOSES_NAME)

    burn_key_digest = subparsers.add_parser('burn_key_digest', help='Parse a RSA public key and burn the digest to key efuse block')
    protect_options(burn_key_digest)
    add_force_write_always(burn_key_digest)
    burn_key_digest.add_argument('block', help='Key block to burn', action='append', choices=efuses.BLOCKS_FOR_KEYS)
    burn_key_digest.add_argument('keyfile', help='Key file to digest (PEM format)', action='append', type=argparse.FileType('rb'))
    burn_key_digest.add_argument('keypurpose', help='Purpose to set.', action='append', choices=fields.EfuseKeyPurposeField.DIGEST_KEY_PURPOSES)
    for _ in efuses.BLOCKS_FOR_KEYS:
        burn_key_digest.add_argument('block', help='Key block to burn', nargs="?", action='append', metavar="BLOCK", choices=efuses.BLOCKS_FOR_KEYS)
        burn_key_digest.add_argument('keyfile', help='Key file to digest (PEM format)', nargs="?", action='append', metavar="KEYFILE",
                                     type=argparse.FileType('rb'))
        burn_key_digest.add_argument('keypurpose', help='Purpose to set.', nargs="?", action='append', metavar="KEYPURPOSE",
                                     choices=fields.EfuseKeyPurposeField.DIGEST_KEY_PURPOSES)

    p = subparsers.add_parser('set_flash_voltage',
                              help='Permanently set the internal flash voltage regulator to either 1.8V, 3.3V or OFF. '
                              'This means GPIO45 can be high or low at reset without changing the flash voltage.')
    p.add_argument('voltage', help='Voltage selection', choices=['1.8V', '3.3V', 'OFF'])

    p = subparsers.add_parser('burn_custom_mac', help='Not supported! Burn a 48-bit Custom MAC Address to EFUSE is.')
    p.add_argument('mac', help='Custom MAC Address to burn given in hexadecimal format with bytes separated by colons'
                   ' (e.g. AA:CD:EF:01:02:03).', nargs="?")
    add_force_write_always(p)

    p = subparsers.add_parser('get_custom_mac', help='Not supported! Prints the Custom MAC Address.')


def burn_custom_mac(esp, efuses, args):
    raise esptool.FatalError("burn_custom_mac is not supported!")


def get_custom_mac(esp, efuses, args):
    raise esptool.FatalError("get_custom_mac is not supported!")


def set_flash_voltage(esp, efuses, args):
    raise esptool.FatalError("set_flash_voltage is not supported!")


def adc_info(esp, efuses, args):
    print("")
    if efuses["BLOCK2_VERSION"].get() == 1:
        print("Temperature Sensor Calibration = {}C".format(efuses["TEMP_SENSOR_CAL"].get()))

        print("")
        print("ADC1 readings stored in efuse BLOCK2:")
        print("    MODE0 D1 reading  (250mV):  {}".format(efuses["ADC1_MODE0_D1"].get()))
        print("    MODE0 D2 reading  (600mV):  {}".format(efuses["ADC1_MODE0_D2"].get()))

        print("    MODE1 D1 reading  (250mV):  {}".format(efuses["ADC1_MODE1_D1"].get()))
        print("    MODE1 D2 reading  (800mV):  {}".format(efuses["ADC1_MODE1_D2"].get()))

        print("    MODE2 D1 reading  (250mV):  {}".format(efuses["ADC1_MODE2_D1"].get()))
        print("    MODE2 D2 reading  (1000mV): {}".format(efuses["ADC1_MODE2_D2"].get()))

        print("    MODE3 D1 reading  (250mV):  {}".format(efuses["ADC1_MODE3_D1"].get()))
        print("    MODE3 D2 reading  (2000mV): {}".format(efuses["ADC1_MODE3_D2"].get()))

        print("")
        print("ADC2 readings stored in efuse BLOCK2:")
        print("    MODE0 D1 reading  (250mV):  {}".format(efuses["ADC2_MODE0_D1"].get()))
        print("    MODE0 D2 reading  (600mV):  {}".format(efuses["ADC2_MODE0_D2"].get()))

        print("    MODE1 D1 reading  (250mV):  {}".format(efuses["ADC2_MODE1_D1"].get()))
        print("    MODE1 D2 reading  (800mV):  {}".format(efuses["ADC2_MODE1_D2"].get()))

        print("    MODE2 D1 reading  (250mV):  {}".format(efuses["ADC2_MODE2_D1"].get()))
        print("    MODE2 D2 reading  (1000mV): {}".format(efuses["ADC2_MODE2_D2"].get()))

        print("    MODE3 D1 reading  (250mV):  {}".format(efuses["ADC2_MODE3_D1"].get()))
        print("    MODE3 D2 reading  (2000mV): {}".format(efuses["ADC2_MODE3_D2"].get()))
    else:
        print("BLOCK2_VERSION = {}".format(efuses["BLOCK2_VERSION"].get_meaning()))


def burn_key(esp, efuses, args, digest=None):
    if digest is None:
        datafile_list = args.keyfile[0:len([name for name in args.keyfile if name is not None]):]
    else:
        datafile_list = digest[0:len([name for name in digest if name is not None]):]
    efuses.force_write_always = args.force_write_always
    block_name_list = args.block[0:len([name for name in args.block if name is not None]):]
    keypurpose_list = args.keypurpose[0:len([name for name in args.keypurpose if name is not None]):]

    util.check_duplicate_name_in_list(block_name_list)
    if len(block_name_list) != len(datafile_list) or len(block_name_list) != len(keypurpose_list):
        raise esptool.FatalError("The number of blocks (%d), datafile (%d) and keypurpose (%d) should be the same." %
                                 (len(block_name_list), len(datafile_list), len(keypurpose_list)))

    print("Burn keys to blocks:")
    for block_name, datafile, keypurpose in zip(block_name_list, datafile_list, keypurpose_list):
        efuse = None
        for block in efuses.blocks:
            if block_name == block.name or block_name in block.alias:
                efuse = efuses[block.name]
        if efuse is None:
            raise esptool.FatalError("Unknown block name - %s" % (block_name))
        num_bytes = efuse.bit_len // 8

        block_num = efuses.get_index_block_by_name(block_name)
        block = efuses.blocks[block_num]

        if digest is None:
            data = datafile.read()
        else:
            data = datafile

        print(" - %s" % (efuse.name), end=" ")
        revers_msg = None
        if efuses[block.key_purpose_name].need_reverse(keypurpose):
            revers_msg = "\tReversing byte order for AES-XTS hardware peripheral"
            data = data[::-1]
        print("-> [%s]" % (util.hexify(data, " ")))
        if revers_msg:
            print(revers_msg)
        if len(data) != num_bytes:
            raise esptool.FatalError("Incorrect key file size %d. Key file must be %d bytes (%d bits) of raw binary key data." %
                                     (len(data), num_bytes, num_bytes * 8))

        if efuses[block.key_purpose_name].need_rd_protect(keypurpose):
            read_protect = False if args.no_read_protect else True
        else:
            read_protect = False
        write_protect = not args.no_write_protect

        # using efuse instead of a block gives the advantage of checking it as the whole field.
        efuse.save(data)

        disable_wr_protect_key_purpose = False
        if efuses[block.key_purpose_name].get() != keypurpose:
            if efuses[block.key_purpose_name].is_writeable():
                print("\t'%s': '%s' -> '%s'." % (block.key_purpose_name, efuses[block.key_purpose_name].get(), keypurpose))
                efuses[block.key_purpose_name].save(keypurpose)
                disable_wr_protect_key_purpose = True
            else:
                raise esptool.FatalError("It is not possible to change '%s' to '%s' because write protection bit is set." %
                                         (block.key_purpose_name, keypurpose))
        else:
            print("\t'%s' is already '%s'." % (block.key_purpose_name, keypurpose))
            if efuses[block.key_purpose_name].is_writeable():
                disable_wr_protect_key_purpose = True

        if disable_wr_protect_key_purpose:
            print("\tDisabling write to '%s'." % block.key_purpose_name)
            efuses[block.key_purpose_name].disable_write()

        if read_protect:
            print("\tDisabling read to key block")
            efuse.disable_read()

        if write_protect:
            print("\tDisabling write to key block")
            efuse.disable_write()
        print("")

    if not write_protect:
        print("Keys will remain writeable (due to --no-write-protect)")
    if args.no_read_protect:
        print("Keys will remain readable (due to --no-read-protect)")

    efuses.burn_all()
    print("Successful")


def burn_key_digest(esp, efuses, args):
    digest_list = []
    datafile_list = args.keyfile[0:len([name for name in args.keyfile if name is not None]):]
    block_list = args.block[0:len([block for block in args.block if block is not None]):]
    for block_name, datafile in zip(block_list, datafile_list):
        efuse = None
        for block in efuses.blocks:
            if block_name == block.name or block_name in block.alias:
                efuse = efuses[block.name]
        if efuse is None:
            raise esptool.FatalError("Unknown block name - %s" % (block_name))
        num_bytes = efuse.bit_len // 8
        digest = espsecure._digest_rsa_public_key(datafile)
        if len(digest) != num_bytes:
            raise esptool.FatalError("Incorrect digest size %d. Digest must be %d bytes (%d bits) of raw binary key data." %
                                     (len(digest), num_bytes, num_bytes * 8))
        digest_list.append(digest)
    burn_key(esp, efuses, args, digest=digest_list)
