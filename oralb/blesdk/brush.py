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
from typing import List

from caterpillar.model import struct
from caterpillar.shortcuts import ctx, F, this, LittleEndian
from caterpillar.fields import uint8, Enum, uint32

from .model import characteristic, DeviceState, Pressure
from .advertise import ProtocolVersion


class BrushType(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 153
    EXPERIMENTAL = 255
    D36_EXPERIMENTAL = 63
    D36_X_MODE = 0
    D36_6_MODE = 1
    D36_5_MODE = 2
    D21_EXPERIMENTAL = 127
    D21_X_MODE = 64
    D21_4_MODE = 65
    D21_3_MODE = 66
    D21_3_MODE_WHITENING = 69
    D21_2A_MODE = 67
    D21_2B_MODE = 68
    D21_1_MODE = 70
    D706_X_MODE = 112
    D706_6_MODE = 113
    D706_5_MODE = 114
    D706_X_MODE_CHINA = 117
    D706_6_MODE_CHINA = 118
    D706_5_MODE_CHINA = 119
    D701_X_MODE = 32
    D701_6_MODE = 33
    D701_5_MODE = 34
    D700_5_MODE = 39
    D700_4_MODE = 40
    D700_6_MODE = 41
    D601_X_MODE = 80
    D601_5_MODE = 81
    D601_4_MODE = 82
    D601_3A_MODE = 83
    D601_2A_MODE = 84
    D601_2B_MODE = 85
    D601_3B_MODE = 86
    D601_1_MODE = 87
    SONOS_X_MODE = 48
    SONOS = 49  # SONOS IO
    SONOS_BIG_TI = 50  # SONOS IO (BIG TI)
    SONOS_G4 = 52  # SONOS GALAXY (IO 4)
    SONOS_G5 = 53  # SONOS GALAXY (IO 5)
    SONOS_EPLATFORM = 54


class BrushStatus(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 0xFF
    NOT_CONNECTED = 0
    PRE_RUN = 1
    IDLE = 2
    CHARGING = 3
    RUN = 4

    # the following codes were taken from
    # https://github.com/wise86-android/OralBlue_python/blob/master/OralBlue/BrushState.py
    SETUP = 0x05
    FLIGHT_MENU = 0x06
    FINAL_TEST = 0x71
    PCB_TEST = 0x72
    SLEEP = 0x73
    TRANSPORT = 0x74


class Mode(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 0xFF
    OFF = 0
    DAILY_CLEAN = 1
    SENSITIVE = 2
    MASSAGE = 3
    WHITENING = 4
    DEEP_CLEAN = 5
    TONGUE_CLEAN = 6
    PRO_CLEAN = 7


class V006Mode(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 0xFF
    V006_CLEAN = 0
    V006_SOFT = 1
    V006_MASSAGE = 2
    V006_POLISH = 3
    V006_TURBO = 4
    V006_SOFT_PLUS = 5
    V006_TONGUE = 6
    V006_OFF = 7
    V006_SETTINGS = 8


class Quadrant(enum.IntEnum):
    __struct__ = uint8

    UNKNOWN = 0xFE
    FIRST_QUADRANT = 0
    SECOND_QUADRANT = 1
    THIRD_QUADRANT = 2
    FOURTH_QUADRANT = 3
    FIFTH_QUADRANT = 4
    SIXTH_QUADRANT = 5
    SEVENTH_QUADRANT = 6
    EIGHTH_QUADRANT = 7
    LAST_QUADRANT = 0xFF
    NO_QUADRANTS_DEFINED = 0xF0


@characteristic("FF08", "brushing_time")
@struct(kw_only=False)
class BrushingTime:
    minutes: uint8
    seconds: uint8


def _brush_mode_fn(value, context):
    if value >= 6 or value == 0:
        return F(Enum(V006Mode, uint8))

    return F(Enum(Mode, uint8))


@characteristic("FF07", "brushing_mode")
@struct(kw_only=False)
class BrushingMode:
    mode: F(ctx._root.protocol) >> _brush_mode_fn


@characteristic("FF09", "toothbrush_quadrant")
@struct(kw_only=False)
class ToothbrushQuadrant:
    quadrant: Quadrant
    num_quadrants: uint8


@characteristic("FF25", "brush_modes")
@struct(kw_only=False)
class BrushModes:
    modes: uint8[8]

    def get_modes(self) -> List[Mode]:
        return list(map(Mode, self.modes))


@characteristic("FF02", "brush_info")
@struct(kw_only=False)
class BrushInfo:
    type: BrushType
    protocol: ProtocolVersion
    version: uint8


@characteristic("FF01", "brush_id")
@struct(kw_only=False, order=LittleEndian)
class BrushID:
    id: uint32


def _brush_status_fn(value: ProtocolVersion, context):
    if value <= 5:
        # An advertisement before V006 contains
        # the current pressure state.
        return Enum(Pressure.State, uint8)
    return Enum(BrushStatus, uint8)


@struct
class BrushAdvertisement:
    protocol: ProtocolVersion
    type: BrushType
    version: uint8
    state: DeviceState.State
    status: F(this.protocol) >> _brush_status_fn
    brush_time_min: uint8
    brush_time_sec: uint8
    brush_mode: F(this.protocol) >> _brush_mode_fn
    brush_progress: uint8
    quadrant_completion: Quadrant
    total_quadrants: uint8
