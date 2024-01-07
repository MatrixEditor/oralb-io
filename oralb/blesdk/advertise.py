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
import enum

from caterpillar.fields import uint8
from bleak import BLEDevice, AdvertisementData

# Company ID for: Procter & Gamble
# Taken from https://www.bluetooth.com/specifications/assigned-numbers/
COMPANY_ID = 0xDC


def is_brush(device: BLEDevice, adv: AdvertisementData) -> bool:
    if not adv.manufacturer_data:
        return False

    return COMPANY_ID in adv.manufacturer_data


class ProtocolVersion(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 0
    V001 = 1
    V002 = 2
    V003 = 3
    V004 = 4
    V005 = 5
    V006 = 6
    V007 = 7
    V008 = 8

