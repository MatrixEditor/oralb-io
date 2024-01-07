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

BASE_UUID = "A0F0XXXX-5047-4D53-8208-4F72616C2D42"

# Missing structs are:
#   FF01 - ? Timestamp/time
#   FF05 - BatteryLevel
#   FF06 - Button
#   FF08 - BrushingTime
#   FF0E - DashboardDataStreamChunk
#   FF21 - Control
#   FF26 - QuadrantTimer
#   FF28 - PressureConfiguration
#   FF29 - SessionData
#   FF2C - ConfigureDashboard
#   FF2D - RefillRemainder
#   FF83 - LegacyOTAPayLoad2
# + all charger commands that start with 3C..


def make_uuid(cid: str) -> str:
    return BASE_UUID.replace("XXXX", cid)


__characteristics__ = {}


def register(cid: str, model) -> None:
    __characteristics__[cid] = model


def characteristic(cid: str, name: str):
    def wrap(cls):
        register(make_uuid(cid), cls)
        setattr(cls, "__cname__", name)
        return cls

    return wrap


@characteristic("FF03", "user_id")
@struct(kw_only=False)
class UserID:
    id: uint8


@characteristic("FF2B", "my_color")
@struct(kw_only=False)
class Color:
    red: uint8
    green: uint8
    blue: uint8
    identifier: uint8


@characteristic("FF04", "device_state")
@struct(kw_only=False)
class DeviceState:
    class State(enum.IntEnum):
        __struct__ = uint8

        UNKNOWN = 0
        INIT = 1
        IDLE = 2
        RUN = 3
        CHARGE = 4
        SETUP = 5
        FLIGHT_MENU = 6
        CHARGE_FORBIDDEN = 7
        PRE_RUN = 8
        POST_RUN = 9
        FINAL_TEST = 113
        PCB_TEST = 114
        SLEEP = 115
        TRANSPORT = 116
        CALIBRATION_TEST = 117

    class SubState(enum.IntEnum):
        __struct__ = uint8

        UNKNOWN = 0xFF
        TRANSPORT_DISABLED_DEACTIVATE_TIMER_DISABLED = 0
        TRANSPORT_ENABLED_DEACTIVATE_TIMER_DISABLED = 1
        TRANSPORT_ENABLED_DEACTIVATE_TIMER_ENABLED = 2

    state: State
    sub_state: SubState


@characteristic("FF22", "rtc")
@struct(order=LittleEndian, kw_only=False)
class RTC:
    epochMillis: uint32 = 946684800000


@characteristic("FF0A", "smiley")
@struct(kw_only=False)
class Smiley:
    class Face(enum.IntEnum):
        __struct__ = uint8

        OFF = 0
        STANDARD = 1
        SPECIAL2 = 2
        SPECIAL3 = 3
        SPECIAL4 = 4
        SPECIAL5 = 5
        SPECIAL6 = 6
        SPECIAL7 = 7

    face: Face


@characteristic("FF23", "timezone")
@struct(kw_only=False)
class Timezone:
    # This struct has to be validated!
    zone: uint8


@characteristic("FF27", "tongue_time")
@struct(kw_only=False)
class TongueTime:
    # This struct has to be validated!
    duration: uint8


@characteristic("FF81", "ota_command")
@struct(kw_only=False)
class OTACommand:
    class Command(enum.IntEnum):
        __struct__ = uint8

        STANDBY = 0
        INITIALIZE = 17
        FINISH_UPLOAD = 19
        FLASH_FIRMWARE = 26
        RESET = 27
        ERROR = 30

    command: Command


@characteristic("FF82", "ota_payload")
@struct(kw_only=False)
class OTAPayload:
    payload: Memory(...)


@characteristic("FF84", "ota_state")
@struct(kw_only=False)
class OTAState:
    class State(enum.IntEnum):
        __struct__ = uint8

        STANDBY = 0
        APP_INITIALIZED = 17
        APP_VERIFY_SIZE = 18
        APP_READY_FOR_PAYLOAD = 19
        APP_UNKNOWN_PAUSE = 20
        APP_COMPLETED = 21
        APP_COMPLETED_NOT_CHARGED = 22
        APP_ERROR = 30
        ERROR = 0xEE
        FLASH_STARTED = 0xAA
        FLASH_CONFIRMED = 0xFF

    state: State


@characteristic("FF85", "ota_transfer_size")
@struct(kw_only=False)
class OTATransferSize:
    # This struct has to be validated!
    value: uint32


@characteristic("FF0B", "pressure")
@struct(order=LittleEndian)
class Pressure:
    # NOTE: only for versions >= 6
    class State(enum.IntEnum):
        __struct__ = uint8

        LOW_PRESSURE = 0
        NORMAL_PRESSURE = 1
        HIGH_PRESSURE = 2

    state: State
    timestamp_a: uint16
    record_a: uint16
    timestamp_b: uint16
    record_b: uint16
    identifier: uint8


