# Copyright (C) MatrixEditor 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import argparse
import traceback
import asyncio
import functools

from typing import Any, Optional

from rich import print
from rich.table import Table
from rich.live import Live
from rich.console import Console

from bleak import BleakScanner, exc, BLEDevice, AdvertisementData
from caterpillar.shortcuts import unpack, F
from caterpillar.fields import Bytes
from caterpillar.exception import StructException

from oralb.blesdk.advertise import is_brush, COMPANY_ID
from oralb.blesdk._model import __characteristics__, make_uuid
from oralb.blesdk.brush import BrushAdvertisement
from oralb.blesdk.client import OralBClient, OralBProperty
from oralb.exceptions import CLIStop

console = Console()

COMMAND_TYPES = set()


def command(cls):
    COMMAND_TYPES.add(cls)
    return cls


def print_ok(msg) -> None:
    print(r"\[   [bold green]Ok[/]   ] " + msg)


def print_err(msg) -> None:
    print(r"\[  [bold red]Error[/] ] " + msg)


def print_info(msg) -> None:
    print(r"\[  [bold cyan]Info[/]  ] " + msg)


def print_warn(msg) -> None:
    print(r"\[  [bold yellow]Warn[/]  ] " + msg)


def get_input(prompt) -> str:
    return console.input(r"<  [bold grey]Input[/] > " + prompt)


class Command:
    name: str

    def get_parser(self) -> argparse.ArgumentParser:
        return argparse.ArgumentParser(self.name)


def requires_connection(func):
    @functools.wraps(func)
    async def ensure_connected(self, shell, argv, *args, **kwargs):
        if not shell.obclient or not shell.obclient.is_connected:
            cmd = DeviceManagerCommand()
            await cmd.do_connect(shell, argv)
            if not shell.obclient or not shell.obclient.is_connected:
                print_err("Could not connect to device, please restart the shell!")
                return

        return await func(self, shell, argv, *args, **kwargs)

    return ensure_connected


@command
class ExitCommand(Command):
    name = "exit"

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(self.name)
        parser.set_defaults(fn=self.do_exit)
        return parser

    async def do_exit(self, shell, argv):
        if shell.obclient and shell.obclient.is_connected:
            with console.status("Disconnecting from device..."):
                await shell.obclient.disconnect()
        raise CLIStop


@command
class BLECommand(Command):
    name = "ble"

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(self.name)
        sub_parsers = parser.add_subparsers()

        discover_mod = sub_parsers.add_parser("discover")
        discover_mod.add_argument("-T", "--timeout", default=10.0)
        discover_mod.add_argument("-B", "--brushes", action="store_true")
        discover_mod.set_defaults(fn=self.discover)
        return parser

    async def discover(self, shell, argv: argparse.Namespace) -> None:
        timeout = argv.timeout
        with console.status("Starting Bluetooth (LE) scan for 5 seconds..."):
            try:
                devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
            except TimeoutError:
                print_err(
                    (
                        "Could not receive any incoming advertisements - it threw a "
                        "[bold]TimeoutError[/]. Please try again!"
                    )
                )
                return
            except exc.BleakError as error:
                print_err(f"[bold]{type(error).__name__}: [/] {str(error)}")
                return

        # We should print out detailed information on brushes
        print_info(f"Scan complete: found {len(devices)} devices.\n")
        table = Table(title="Detailed device info")
        table.add_column("Address")
        table.add_column("Name", justify="center")
        table.add_column("rssi", justify="center")
        table.add_column("isBrush", justify="center")

        brushes = []
        with Live(table, refresh_per_second=4):
            for device, adv in devices.values():
                brush = is_brush(device, adv)
                if argv.brushes and not brush:
                    continue

                table.add_row(
                    str(device.address),
                    str(device.name),
                    f"[cyan]{adv.rssi}[/]",
                    str(brush),
                )
                if brush:
                    brushes.append((device, adv))

        # Now lets inspect all brushes
        if len(brushes) == 0:
            print_warn("Could not locate any brushes!")
            return

        print_info(f"Located {len(brushes)} brushes:")
        for device, adv in brushes:
            print()  # extra new line for style purposes
            print(device)
            print("-" * len(str(device)))
            print(unpack(BrushAdvertisement, adv.manufacturer_data[COMPANY_ID]))


name2characteristic = {y.__cname__: y for x, y in __characteristics__.items()}
cid2characteristic = {x[4:8]: y for x, y in __characteristics__.items()}


@command
class DeviceManagerCommand(Command):
    name = "dm"

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(self.name)
        sub_parsers = parser.add_subparsers()

        mod_connect = sub_parsers.add_parser("connect")
        mod_connect.add_argument("address")
        mod_connect.set_defaults(fn=self.do_connect)

        get_mod = sub_parsers.add_parser("getchar")
        get_mod.add_argument("name")
        get_mod.set_defaults(fn=self.get_char)
        return parser

    async def do_connect(self, shell, argv):
        if shell.obclient is None:
            obclient = OralBClient(None)
        else:
            # In this case, the BleakClient is already assigned
            # to the right address.
            obclient = shell.obclient

        address = obclient.address
        if obclient.address is None:
            try:
                address = argv.address
            except AttributeError:
                print_info("Device's is not set, please enter address below!")
                # Here, we have to request the device's address first
                address = get_input("[bold]Device: [/]")
                if not address:
                    return

        msg = "Trying to establish a connection to device..."
        if shell.obclient is not None:
            msg = "Reconnecting to device..."
        try:
            with console.status(msg):
                await obclient.connect(address=address)
        except TimeoutError:
            print_err("Timout error while connecting to device, please try again!")
        except OSError as osexc:
            print_err(f"OS related error: {str(osexc)}")
        except exc.BleakDeviceNotFoundError:
            print_err(f"Device with address {obclient.address!r} not found!")
        except Exception as error:
            print_err(f"[bold]{type(error).__name__}: [/] {str(error)}")
            traceback.print_exc()
        else:
            shell.obclient = obclient
            print_ok(f"Connected to {obclient.address!r}")

    @requires_connection
    async def get_char(self, shell, argv):
        name = argv.name
        obclient: OralBClient = shell.obclient
        if name in name2characteristic:
            try:
                obproperty = getattr(obclient, name)
            except AttributeError:
                print_err(
                    (
                        "Could not resolve characteristic using attribute name "
                        f"{name!r}. Try 'cm list' to view available characteristics."
                    )
                )
                return
        # The name specifies a uuid or short uuid
        else:
            uuid = name
            model = F(Bytes(...))
            if name in cid2characteristic or len(name) == 4:
                uuid = make_uuid(name)

            model = __characteristics__.get(name, model)
            obproperty = OralBProperty(obclient, uuid, model)
        try:
            with console.status("Reading value..."):
                value = await obproperty._get()
        except TimeoutError:
            print_err("Timeout error during get_char!")
        except StructException as err:
            print_err(f"Could not parse input: {str(err)}")
        except exc.BleakError as be:
            print_err(str(be))
        except Exception as err:
            print_err(f"{type(err).__name__}: {err}")
        else:
            print_ok(f"Value of {obproperty.name!r}:\n")
            print(value)
