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

from ._model import __characteristics__
from .advertise import ProtocolVersion


class OralBProperty:
    def __init__(self, client: "OralBClient", name: str, model: type) -> None:
        self._value = None
        self.obclient = client
        self.name = name
        self.model = model

    async def _get(self):
        if self._value is None:
            data = await self.obclient.client.read_gatt_char(self.name)
            self._value = unpack(self.model, data, protocol=self.obclient.protocol)

        return self._value

    async def set(self, new_value):
        self._value = new_value
        await self.save()

    async def save(self) -> None:
        data = pack(self._value, self.model, protocol=self.obclient.protocol)
        await self.obclient.client.write_gatt_char(self.name, data)

    def __await__(self):
        return self._get().__await__()


class OralBClient:
    def __init__(
        self, address: str, protocol: Optional[ProtocolVersion] = None
    ) -> None:
        self.protocol = protocol or ProtocolVersion.V006
        self.address = address
        self.client = None
        self._fields = set()

        for name, cls in __characteristics__.items():
            setattr(self, cls.__cname__, OralBProperty(self, name, cls))
            self._fields.add(cls.__cname__)
            # this is only for documentation purposes
            type(self).__annotations__[cls.__cname__] = cls

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.client.disconnect()

    async def connect(self, address=None):
        self.address = address or self.address
        self.client = BleakClient(address, disconnected_callback=self.on_disconnect)

        await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    def on_disconnect(self, _: BleakClient):
        # also, remove the current client instance
        self.client = None

    @property
    def characteristics(self) -> List[str]:
        return list(self._fields)

    @property
    def is_connected(self) -> bool:
        # the result can't be used on windows
        return self.client.is_connected if self.client else False
