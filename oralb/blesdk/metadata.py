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

from caterpillar.shortcuts import *
from caterpillar.fields import *
from caterpillar.exception import *


from .model import Control

__meta_models__ = {}
__data_models__ = {
    Control.DataRead.DATE_OF_BUILD: F(CString(...)),
    Control.DataRead.TIME_OF_BUILD: F(CString(...)),
    Control.DataRead.SOFTWARE_VERSION_SECONDARY_CONTROLLER: F(CString(...)),
    Control.DataRead.SOFTWARE_VERSION_MAIN_CONTROLLER: CString(...) @ 1,
}


def metadata(value: int):
    def add_meta(cls):
        __meta_models__[value] = cls
        return cls

    return add_meta


def data(value: int):
    def add_data(cls):
        __data_models__[value] = cls
        return cls

    return add_data


def metadata_models():
    return __meta_models__


def data_models():
    return __data_models__


@metadata(Control.METADATA.SONOS_TYPE)
@struct
class SonosMetadata:
    class Model(enum.IntEnum):
        __struct__ = uint8

        UNDEFINED = 0
        M9 = 1
        M8 = 2
        M7 = 3
        M6 = 4
        M5 = 5
        M4 = 6
        M10 = 16
        E11 = 17

    class Color(enum.IntEnum):
        __struct__ = uint8

        UNDEFINED = 0
        WHITE = 1
        ONYX = 2
        VIOLET = 3
        ROSE_GOLD = 4
        STORMY_GREY = 5
        LIGHT_ROSE = 6
        DARK_BLUE = 7
        LIGHT_BLUE = 8
        ICE_BLUE = 9
        LILAC_MIST = 10
        SPECKLED_WHITE = 11
        SPECKLED_BLACK = 12
        PURPLE_RAIN = 13
        DEEP_BLACK = 14
        FOREST_GREEN = 15
        OCEAN_BLUE = 16

    class Language(enum.IntEnum):
        __struct__ = uint8

        UNDEFINED = -1
        ENGLISH_EN = 0
        DUETSCH_DE = 1
        CHINESE_CC = 2
        ITALIAN_IT = 3
        JAPANESE_JP = 4
        ARABIC_AR = 5
        FRENCH_FR = 6
        SPANISH_SP = 7
        POLISH_PL = 8
        RUSSIAN_RU = 9
        KOREAN_SK = 10

    class GumGuard(enum.IntEnum):
        __struct__ = uint8

        OFF = 0
        ON = 1
        HD = 2
        NOT_AVAILABLE = 255

    magic: Const(0xFF, uint8)
    model: Model
    color: Color
    language: Language
    brush_modes: uint8[8]
    gum_guard: GumGuard


# REVISIT: this structure may be invalid
@metadata(Control.METADATA.SW_VER_SYSTEM_CONTROLLER_1)
@struct
class SystemController1:
    magic: Const(0x07, uint8)
    media_content_version: uint8
    hardware_config: uint8
    mmap_version: uint8
    info_sector_version: uint8


@metadata(Control.METADATA.SW_VER_SYSTEM_CONTROLLER_2)
@struct
class SystemController2:
    magic: Const(0x07, uint8)
    version: uint8


# REVISIT: device returns other data
@metadata(Control.METADATA.BLE_PROFILE)
@struct
class BLEProfile:
    magic: Const(0x06, uint8)
    prefix_bootloader: char
    num_bootloader: uint8
    build_bootloader: uint8
    prefix_sec_program: char
    num_sec_program: uint8
    build_sec_program: uint8


@metadata(Control.METADATA.DEVICE_UUID)
@struct
class DeviceUUID:
    id: uuid


# default models
@data(Control.DataRead.SERVICE_DATA_A)
@struct(order=LittleEndian)
class ServiceDataA:
    ideal_full_capacity: uint16
    average_motor_current: uint16
    total_monitor_runtime: uint32
    total_pressure: uint32
    total_charge_time: uint32

@data(Control.DataRead.SERVICE_DATA_B)
@struct(order=LittleEndian)
class ServiceDataB:
    total_charge_events: uint16
    total_full_charge_events: uint16
    total_over_temp_Events: uint16
    total_low_temp_events: uint16
    total_brushing_cycles: uint16
    short_term_motor_current: uint16
    total_recharging_hours: uint16