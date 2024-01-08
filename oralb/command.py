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
import dataclasses
import errno
import functools
import enum
import asyncio

from rich import print
from rich.table import Table
from rich.live import Live
from rich.console import Console
from rich.tree import Tree

from bleak import BleakScanner, exc
from caterpillar.shortcuts import unpack, F
from caterpillar.fields import Bytes
from caterpillar.exception import StructException

from oralb.blesdk.advertise import is_brush, COMPANY_ID
from oralb.blesdk.model import __characteristics__, make_uuid, CH_CONTROL, Control
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
    return console.input(r"\[  [bold grey]Input[/] ] " + prompt)


class Command:
    name: str

    def get_parser(self) -> argparse.ArgumentParser:
        return argparse.ArgumentParser(self.name)


def requires_connection(func):
    @functools.wraps(func)
    async def ensure_connected(self, shell, argv, *args, **kwargs):
        if not shell.obclient:
            cmd = DeviceManagerCommand()
            await cmd.do_connect(shell, argv)
            if not shell.obclient or not shell.obclient.is_connected:
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
    """..."""

    name = "dm"

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            self.name, description=DeviceManagerCommand.__doc__
        )
        sub_parsers = parser.add_subparsers()

        mod_connect = sub_parsers.add_parser("connect")
        mod_connect.add_argument("address")
        mod_connect.set_defaults(fn=self.do_connect)
        mod_extend = sub_parsers.add_parser("extend-connection")
        mod_extend.set_defaults(fn=self.do_extend_connection)

        get_mod = sub_parsers.add_parser("getchar")
        get_mod.add_argument("name")
        get_mod.add_argument("-R", "--raw", action="store_true")
        get_mod.set_defaults(fn=self.get_char)

        list_mod = sub_parsers.add_parser("list")
        list_parsers = list_mod.add_subparsers()
        list_chars = list_parsers.add_parser("chars")
        list_chars.set_defaults(fn=self.list_characteristics)
        list_srv = list_parsers.add_parser("services")
        list_srv.set_defaults(fn=self.list_services)
        list_desc = list_parsers.add_parser("descriptors")
        list_desc.set_defaults(fn=self.list_descriptors)

        put_mod = sub_parsers.add_parser("putchar")
        put_mod.add_argument("--no-response", action='store_false')
        put_parsers = put_mod.add_subparsers()

        for uuid, model_ty in __characteristics__.items():
            name = model_ty.__cname__
            model_parser = put_parsers.add_parser(
                name, aliases=(uuid[4:8],), description=model_ty.__name__
            )
            self.build_parser(model_parser, model_ty)

        put_mod.set_defaults(fn=self.put_char)
        return parser

    def _callback(self, shell):
        def real_callback(characteristic, data):
            print(data)
            # loop = asyncio.get_event_loop()
            # loop.create_task(self.do_extend_connection(shell))

        return real_callback

    async def do_extend_connection(self, shell, argv):
        obclient: OralBClient = shell.obclient
        try:
            await obclient.write(
                CH_CONTROL,
                Control.extend_connection(255),
                response=True,  # dm extend-connection
            )
        except Exception as err:
            print_err(f"{type(err).__name__}: {err}")


    async def do_connect(self, shell, argv):
        if shell.obclient is None:
            obclient = OralBClient(None)
        else:
            # In this case, the BleakClient is already assigned
            # to the right address.
            obclient: OralBClient = shell.obclient

        try:
            address = argv.address
        except AttributeError:
            address = obclient.address
            if obclient.address is None:
                print_info("Device address is not set, please enter address below!")
                # Here, we have to request the device's address first
                address = get_input("[bold]Device: [/]")
                if not address:
                    return

        msg = "Trying to establish a connection to device..."
        if shell.obclient is not None:
            msg = "Reconnecting to device..."
        try:
            with console.status(msg):
                if obclient.address:
                    await obclient.unpair()

                await obclient.connect(address=address)
            with console.status("Pairing..."):
                await obclient.pair()
                # If this command throws an error, we have to
                # reconnect to the device (cleanup connection)
                # await obclient.write(
                #     CH_CONTROL,
                #     Control.extend_connection(255),
                #     response=True,
                # )
        except TimeoutError:
            print_err("Timout error while connecting to device, please try again!")
        except OSError as osexc:
            print_err(f"OS related error: {str(osexc)}")
        except exc.BleakDeviceNotFoundError:
            print_err(f"Device with address {obclient.address!r} not found!")
        except exc.BleakError as err:
            if str(err).endswith("Unreachable"):
                # reconnect
                shell.obclient = obclient
                return await self.do_connect(shell, argv)
        except Exception as error:
            print_err(f"[bold]{type(error).__name__}: [/] {str(error)}")
        else:
            shell.obclient = obclient
            print_ok(f"Connected to {obclient.address!r}")
            return True

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

            if not argv.raw:
                model = __characteristics__.get(uuid, model)
            obproperty = OralBProperty(obclient, uuid, model)
        try:
            with console.status("Reading value..."):
                value = await obproperty._get()
        except TimeoutError:
            print_err("Timeout error during get_char!")
        except StructException as err:
            print_err(f"Could not parse input: {str(err)}")
        except exc.BleakError as be:
            if str(be).endswith("Unreachable"):
                print_info("Device disconnected (unreachable)!")
                await obclient.unpair()
                if await self.do_connect(shell, argv):
                    return await self.get_char(shell, argv)
            print_err(str(be))
        except OSError as err:
            if err.errno == errno.EINVAL:
                # windows closed connection
                if len(err.args) == 5 and list(err.args)[3] == -0x7FFFFFED:
                    print_info("Device disconnected (object closed)!")
                    await obclient.unpair()
                    if await self.do_connect(shell, argv):
                        return await self.get_char(shell, argv)
            else:
                print({"no": err.errno, "args": err.args, "str": err.strerror})
                print_err(f"[bold]OSError: [/] {err}")
        except Exception as err:
            print_err(f"{type(err).__name__}: {err}")
            traceback.print_exc()
        else:
            print_ok(f"Value of {obproperty.name!r}:\n")
            print(value)

    def build_parser(self, parser, model: type, name=None) -> argparse.ArgumentParser:
        if hasattr(model, "__models__"):
            # Special case, create subparsers
            subs = parser.add_subparsers()
            for name, sub_model in getattr(model, "__models__").items():
                sub_mod = subs.add_parser(name)
                self.build_parser(sub_mod, sub_model, model.__cname__)
            return

        for field in dataclasses.fields(model):
            name = field.name
            field_ty = field.type
            if isinstance(field_ty, type) and issubclass(field_ty, enum.IntEnum):
                field_ty = int
            elif field_ty in (bytes, memoryview):
                field_ty = lambda x: x.encode("utf-8")
            elif field_ty not in (int, str):
                field_ty = str

            parser.add_argument(
                f"--{name}",
                type=field_ty,
                required=bool(field.default),
                default=field.default if bool(field.default) else None,
                help=f"type: {field_ty.__name__}",
            )
        parser.set_defaults(__cname__=name or model.__cname__)

    @requires_connection
    async def put_char(self, shell, argv):
        name = getattr(argv, "__cname__", None)
        if not name:
            # Do nothing if no command was  typed
            return

        model_ty = name2characteristic[name]
        init_data = {}
        with console.status("Verifying data..."):
            for field in dataclasses.fields(model_ty):
                default = field.default
                value = getattr(argv, field.name, dataclasses.MISSING)
                # raise an eror if not all required arguments
                # have been set
                if not bool(default) and value is dataclasses.MISSING:
                    print_err(f"Missing value of {field.name}")
                    return

                if value is dataclasses.MISSING:
                    value = default
                init_data[field.name] = value

        obj = model_ty(**init_data)
        try:
            with console.status("Writing new value..."):
                obproperty = getattr(shell.obclient, name)
                await obproperty.set(obj, response=not argv.no_response)
        except exc.BleakError as err:
            msg = str(err)
            # if err.endswith("Access Denied"):
            #     pass
            print_err(msg)
        except Exception as err:
            print_err(f"{type(err).__name__}: {err}")
            traceback.print_exc()
        else:
            print_ok("New value:")
            print(obj)

    @requires_connection
    async def list_characteristics(self, shell, argv):
        obclient: OralBClient = shell.obclient
        with console.status("Collecting information..."):
            services = obclient.client.services

        print_info("Device characteristics:\n")
        tree = Tree(f"[bold]Device: [/]{obclient.address}")
        with Live(tree):
            self.add_chars(services.characteristics.values(), tree)

    def add_chars(self, chars: list, tree: Tree):
        for char in chars:
            node = (
                f"[bold]{char.uuid}[/] (Handle: [cyan]{char.handle}[/]): "
                f"[green]{char.description!r}[/] {char.properties}"
            )
            tree.add(node)

    @requires_connection
    async def list_services(self, shell, argv):
        obclient: OralBClient = shell.obclient
        with console.status("Collecting information..."):
            services = obclient.client.services

        print_info("Device services:\n")
        tree = Tree(f"[bold]Device: [/]{obclient.address}")
        with Live(tree):
            for service in services.services.values():
                node = (
                    f"[bold]{service.uuid}[/] (Handle: [cyan]{service.handle}[/]): "
                    f"[green]{service.description!r}[/]"
                )
                subtree = tree.add(node)
                self.add_chars(service.characteristics, subtree)

    @requires_connection
    async def list_descriptors(self, shell, argv):
        obclient: OralBClient = shell.obclient
        with console.status("Collecting information..."):
            services = obclient.client.services

        print_info("Device descriptors:\n")
        tree = Tree(f"[bold]Device: [/]{obclient.address}")
        with Live(tree):
            for desc in services.descriptors.values():
                tree.add(str(desc))
