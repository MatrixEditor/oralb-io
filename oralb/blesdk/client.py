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
from typing import Optional, List
from asyncio import all_tasks

from bleak import BleakClient
from caterpillar.shortcuts import unpack, pack
from caterpillar.fields import FieldStruct
from caterpillar.abc import hasstruct, getstruct

from .model import __characteristics__
from .advertise import ProtocolVersion


class OralBProperty:
    def __init__(self, client: "OralBClient", name: str, model: type) -> None:
        self._value = None
        self.obclient = client
        self.name = name
        self.model = model

    def _get_struct(self):
        return self.model() if not hasstruct(self.model) else getstruct(self.model)

    async def _get(self):
        if self._value is None:
            data = await self.obclient.read(self.name)
            struct = self._get_struct()
            self._value = unpack(struct, data, protocol=self.obclient.protocol)

        return self._value

    async def set(self, new_value, response=None):
        self._value = new_value
        await self.save(response)

    async def save(self, response=None) -> None:
        data = pack(self._value, self.model, protocol=self.obclient.protocol)
        await self.obclient.write(self.name, data, response=response)

    def __await__(self):
        return self._get().__await__()


def _empty_callback(_, _1):
    pass


class OralBClient:
    def __init__(
        self, address: str, protocol: Optional[ProtocolVersion] = None
    ) -> None:
        self.protocol = protocol or ProtocolVersion.V006
        self.address = address
        self.client = None
        self._fields = set()

        for name, cls_ in __characteristics__.items():
            setattr(self, cls_.__cname__, OralBProperty(self, name, cls_))
            self._fields.add(cls_.__cname__)
            # this is only for documentation purposes
            type(self).__annotations__[cls_.__cname__] = cls_

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.client.disconnect()

    async def connect(self, address=None):
        if self.client:
            await self.disconnect()

        previous_address = self.address
        self.address = address or self.address
        if self.client is None or self.address != previous_address:
            self.client = BleakClient(address)

        return await self.client.connect()

    async def disconnect(self):
        return await self.client.disconnect()

    async def unpair(self):
        await self.client.unpair()

    async def pair(self):
        await self.client.pair()

    @property
    def characteristics(self) -> List[str]:
        return list(self._fields)

    @property
    def is_connected(self) -> bool:
        # the result can't be used on windows
        return self.client.is_connected if self.client else False

    async def subscribe(self, char: str, callback) -> None:
        await self.client.start_notify(char, callback)

    async def stop_notify(self, char: str):
        await self.client.stop_notify(char)

    async def write(self, char: str, obj, response=False):
        if not isinstance(obj, bytes):
            obj = pack(obj, protocol=self.protocol)

        return await self.client.write_gatt_char(char, obj, response)

    async def write_notify_on(self, char: str, obj, callback=None, response=False):
        await self.subscribe(char, callback or _empty_callback)
        await self.write(char, obj, response=response)

    async def read(self, char: str):
        return await self.client.read_gatt_char(char)

    async def write_read_on(self, write: str, obj, read: str):
        # result is ignored for now
        await self.write(write, obj, response=True)
        return self.read(read)
