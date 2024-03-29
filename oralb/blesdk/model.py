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

BASE_UUID = "A0F0XXXX-5047-4D53-8208-4F72616C2D42"

# struct configuration
be = BigEndian
le = LittleEndian
opt.set_struct_flags(opt.S_REPLACE_TYPES)

#: all runtime characteristics will be mapped to their corresponding
#: struct type.
__characteristics__: dict = {}


def make_uuid(cid: str) -> str:
    """Generates a uuid from the given short uuid"""
    return BASE_UUID.replace("XXXX", cid)


def register(cid: str, model) -> None:
    """Registers a new struct type to the given uuid"""
    __characteristics__[cid] = model


def characteristic(cid: str, name: str):
    def wrap(cls):
        register(make_uuid(cid) if len(cid) == 4 else cid, cls)
        setattr(cls, "__cname__", name)
        return cls

    return wrap


S_CAPABILITIES = make_uuid("FF00")
CH_DEVICE_ID = make_uuid("FF01")
CH_DEVICE_INFO = make_uuid("FF02")
CH_USER_ID = make_uuid("FF03")
CH_DEVICE_STATE = make_uuid("FF04")
CH_BATTERY_LEVEL = make_uuid("FF05")
CH_BUTTON = make_uuid("FF06")
CH_BRUSHING_MODE = make_uuid("FF07")
CH_BRUSHING_TIME = make_uuid("FF08")
CH_QUADRANT = make_uuid("FF09")
CH_SMILEY = make_uuid("FF0A")
CH_PRESSURE = make_uuid("FF0B")
# ff0c (Handle: 55): 'Cache' ['read', 'write', 'notify'] (needs AUTH)
CH_SENSOR_DATA = make_uuid("FF0D")

S_CONFIG = make_uuid("FF20")
CH_CONTROL = make_uuid("FF21")
CH_RTC = make_uuid("FF22")
CH_TIMEZONE = make_uuid("FF23")
CH_BRUSH_MODES = make_uuid("FF25")
# ff26 (Handle: 77): 'Quadrant Times' ['read', 'write']
CH_TONGUE_TIME = make_uuid("FF27")
CH_SESSION_DATA = make_uuid("FF29")
# ff2a (Handle: 83): 'Flight Mode' ['read', 'write']
CH_MY_COLOR = make_uuid("FF2B")
CH_DASHBOARD_CONFIG = make_uuid("FF2C")
CH_REFILL_REMAINDER = make_uuid("FF2D")

S_OTA = make_uuid("FF80")
CH_OTA_COMMAND = make_uuid("FF81")
CH_OTA_PAYLOAD = make_uuid("FF82")
# ff83 (Handle: 102): 'OTA Payload 2'
CH_OTA_STATE = make_uuid("FF84")
CH_OTA_TRANSFER_SIZE = make_uuid("FF85")


@characteristic(CH_USER_ID, "user_id")
@struct(kw_only=False)
class UserID:
    """Characteristic representing a user ID."""

    id_: uint8
    """The user ID."""


@characteristic(CH_MY_COLOR, "my_color")
@struct
class Color:
    """Characteristic representing a color."""

    #: The red component of the color.
    red: uint8

    #: The green component of the color.
    green: uint8

    #: The blue component of the color.
    blue: uint8

    #: The identifier of the color.
    identifier: uint8


@characteristic(CH_DEVICE_STATE, "device_state")
@struct(kw_only=False)
class DeviceState:
    """Represents the state of a device."""

    class State(enum.IntEnum):
        """Enumeration representing the main states of the device."""

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
        """Enumeration representing the sub-states of the device."""

        __struct__ = uint8
        UNKNOWN = 0xFF
        TRANSPORT_DISABLED_DEACTIVATE_TIMER_DISABLED = 0
        TRANSPORT_ENABLED_DEACTIVATE_TIMER_DISABLED = 1
        TRANSPORT_ENABLED_DEACTIVATE_TIMER_ENABLED = 2

    #: The main state of the device.
    state: State

    #: The sub-state of the device.
    sub_state: SubState


@characteristic(CH_RTC, "rtc")
@struct(order=LittleEndian, kw_only=False)
class RTC:
    epochMillis: uint32 = 946684800000


@characteristic(CH_SMILEY, "smiley")
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


@characteristic(CH_TIMEZONE, "timezone")
@struct(kw_only=False)
class Timezone:
    # This struct has to be validated!
    zone: uint8


@characteristic(CH_TONGUE_TIME, "tongue_time")
@struct(kw_only=False)
class TongueTime:
    # This struct has to be validated!
    duration: uint8


@characteristic(CH_OTA_COMMAND, "ota_command")
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


@characteristic(CH_OTA_PAYLOAD, "ota_payload")
@struct(kw_only=False)
class OTAPayload:
    payload: Memory(...)


@characteristic(CH_OTA_STATE, "ota_state")
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


@characteristic(CH_OTA_TRANSFER_SIZE, "ota_transfer_size")
@struct(kw_only=False)
class OTATransferSize:
    # This struct has to be validated!
    value: uint32


@characteristic(CH_PRESSURE, "pressure")
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


@characteristic(CH_REFILL_REMAINDER, "refill_remainder")
@struct(order=LittleEndian, kw_only=False)
class RefillRemainder:
    class State(enum.IntEnum):
        __struct__ = uint8

        SNOOZE = 2
        RESET = 1
        ON = 0
        OFF = 0xFF
        INTERVAL = 0xFE

    state: State
    days_left: uint16
    brushing_seconds_left: uint16


@characteristic(CH_DASHBOARD_CONFIG, "dashboard")
@struct(order=LittleEndian, kw_only=False)
class DashboardConfig:
    class Divider(enum.IntEnum):
        __struct__ = uint8
        FULL_RESOLUTION = 0
        HALF_RESOLUTION = 2
        QUARTER_RESOLUTION = 4

    session_id: uint16
    divider: Divider


@characteristic(CH_BUTTON, "button")
@struct(kw_only=False)
class Button:
    class State(enum.IntEnum):
        __struct__ = uint8
        UNKNOWN = 0xFF
        NOTHING_PRESSED = 0
        POWER_PRESSED = 1
        MODE_PRESSED = 2

    state: State  #


@characteristic(CH_BATTERY_LEVEL, "battery_level")
@struct(order=LittleEndian, kw_only=False)
class BatteryLevel:
    level: uint8
    with ctx._root.protocol >= 6:
        seconds_left: uint16

    with ctx._root.protocol >= 8:
        milli_volts: uint16
        milli_amperes: uint16
        temperature: int8
        avail_soc: uint8
        # dischargeCapacityMilliAmpereSeconds
        dcmas: uint32
        # currentConditionRemainingCapacityMilliAmpereSeconds
        rcmas: uint32
        soc_state: uint8


# default GATT characteristics
@characteristic("00002a00-0000-1000-8000-00805f9b34fb", "name")
@struct(kw_only=False)
class DeviceName:
    text: String(...)


@struct(kw_only=False, order=LittleEndian)
class GyroMotionData:
    timestamp: uint16
    gyro_x: int8
    gyro_y: int8
    gyro_z: int8
    motion_x: int8
    motion_y: int8
    motion_z: int8


@struct(kw_only=False, order=LittleEndian)
class HighResolutionMotionData:
    motion_x: int16
    motion_y: int16
    motion_z: int16


@struct(kw_only=False, order=LittleEndian)
class MotionData:
    timestamp: uint16
    motion_x: int8
    motion_y: int8
    motion_z: int8


@struct(kw_only=False, order=LittleEndian)
class CalibrationData:
    calibration_x: int16
    calibration_y: int16
    calibration_z: int16


@struct(kw_only=False, order=LittleEndian)
class DashboardData:
    class Status(enum.IntEnum):
        SESSION_ID_INVALID = 0xFF - 16
        FIRST_PACKAGE = 1
        PACKAGES_PENDING = 2
        LAST_PACKAGE = 8

    status: Enum(Status, uint8) @ 16
    # To keep CLI parser building simple, we do NOT include
    # a nested struct here
    timestamp: uint16
    gyro_x: int8
    gyro_y: int8
    gyro_z: int8
    motion_x: int8
    motion_y: int8
    motion_z: int8


@characteristic(CH_SENSOR_DATA, "sensor_data")
class SensorData(Transformer):
    # This field is only used when preparing the parser
    # for the CLI.
    __models__ = {
        "gyro": GyroMotionData,
        "motion": MotionData,
        "high-resolution": HighResolutionMotionData,
        "calibration": CalibrationData,
        "dashboard": DashboardData,
    }

    class Data(enum.IntEnum):
        SPECIAL = 0xFF - 127
        HIGH_RESOLUTION = 8
        CALIBRATION = 7
        DASHBOARD = 32
        COMINO = 16

    def __init__(self) -> None:
        super().__init__(Bytes(...))

    def decode(self, parsed: bytes, context) -> None:
        if len(parsed) != 20:
            # The parsed data must be 20 bytes
            raise ValidationError(
                f"Expected motion data of length 20 - got {len(parsed)}", context
            )

        if parsed[-1] != SensorData.Data.SPECIAL:
            # Default motion data (takes up all the space)
            return unpack(MotionData[4], parsed)

        match parsed[-2]:
            case SensorData.Data.COMINO:
                return unpack(GyroMotionData[2], parsed)
            case SensorData.Data.HIGH_RESOLUTION:
                return unpack(F(HighResolutionMotionData), parsed)
            case SensorData.Data.CALIBRATION:
                return unpack(CalibrationData[3], parsed)
            case SensorData.Data.DASHBOARD:
                return unpack(DashboardData[2], parsed)
            case _:
                raise ValidationError(f"Unexpected data: {parsed[-2]:x}", context)

    def encode(self, obj, context) -> bytes:
        data: bytes = pack(obj)
        if len(data) < 20:
            if len(data) < 18:
                data += bytes(18 - len(data))

            data_ty = None
            match obj:
                case HighResolutionMotionData():
                    data_ty = SensorData.Data.HIGH_RESOLUTION
                case GyroMotionData():
                    data_ty = SensorData.Data.COMINO
                case CalibrationData():
                    data_ty = SensorData.Data.CALIBRATION
                case DashboardData():
                    data_ty = SensorData.Data.DASHBOARD
                case _:
                    raise ValidationError(f"Invalid data type: {type(obj)}", context)
            data += bytes([data_ty, SensorData.Data.SPECIAL])
        return data


def _cmd_condition(context) -> bool:
    protocol = context._root.protocol
    command = context._obj.command
    if command in list(range(40, 45)):  # 40-44
        return protocol <= 6

    if command in (38, 47):
        return protocol <= 6

    return True


# @characteristic("FF21", "control")
@struct(kw_only=False)
class Control:
    class Command:
        # The following commands need a 0x10 (16) prefix and use their
        # command value as parameter (see .change_mode)
        RESET_MEMORY_TIMER = 41
        MY_COLOR_DISABLE = 48
        MY_COLOR_ENABLE = 49
        STOP_TIMER_SIGNAL = 32
        MOTION_DISABLE = 64
        MOTION_ENABLE = 65
        HIGH_RESOLUTION_MEASUREMENT = 66
        PRESSURE_DISABLE = 80
        RAINBOW_ILLUMINATION_DISABLE = 96
        RAINBOW_ILLUMINATION_ENABLE = 97
        TRIGGER_RAINBOW_ILLUMINATION = 98
        CHARGE_ILLUMINATION_DISABLE = 112
        CHARGE_ILLUMINATION_ENABLE = 113
        TRIGGER_CONNECTION_ILLUMINATION = -125
        TRIGGER_SHORT_STUTTER = 33
        TRIGGER_LONG_STUTTER = 34
        TRIGGER_SHORT_VISUAL_SIGNAL = 35
        TRIGGER_LONG_VISUAL_SIGNAL = 36
        SET_TO_DAILY_CLEAN_MODE = 1
        SET_TO_PRO_CLEAN_MODE = 7
        SET_TO_SENSITIVE_MODE = 2
        SET_TO_WHITENING_MODE = 4
        SET_TO_MASSAGE_MODE = 3
        SET_TO_TONGUE_CLEAN_MODE = 6
        SET_TO_DEEP_CLEAN_MODE = 5
        MOTOR_OFF = 0
        MODE_SWITCHING_ON = 14
        MODE_SWITCHING_OFF = 15
        # This is a special command that takes a parameter instead of
        # using its command value
        # SET_MODE = 1

        # The following four commands need a 0x2E (46) as prefix and use
        # their command value as parameter
        DISABLE_ALL_MOTOR_RAMPING = 0
        ENABLE_SOFT_START_ONLY_MOTOR_RAMPING = 1
        ENABLE_LOW_CHARGE_ONLY_MOTOR_RAMPING = 2
        ENABLE_ALL_MOTOR_RAMPING = 3

        # The last two commands place their command value as prefix
        # and need a custom parameter value
        READ_PARAM = 1
        READ_DATA = 2  # see .DataRead

        # The following commands need a 0x37 (55) prefix value on protocol
        # version 6 with its value; otherwise the command is the associated
        # value.
        RTC = 38
        BRUSH_TIMER = 40
        BRUSH_MODES = 41
        QUADRANT_TIMERS = 42
        TONGUE_TIME = 43
        PRESSURE_CONFIGURATION = 44
        MY_COLOR = 47

        # parameter is always 82
        FACTORY_RESET = 50

        # prefix = 51
        SMART_GUIDE_DISABLE = 80
        SMART_GUIDE_ENABLE = 81

        #: This command is used to extend the BLE connection for the amount of
        #: seconds given as the parameter. (from 0-255)
        EXTEND_CONNECTION = 49

        # prefix = value and parameter = custom
        CALIBRATION_READ = 4
        READ_METADATA = 5

        # prefix = value and parameter = 0
        DASHBOARD = 48

        # prefix = value, parameter = custom
        DEVICE_COLOR_READ = 18
        NOTIFICATION_CLEAR = 3

    class DataRead(enum.IntEnum):
        SERVICE_DATA_A = 250
        SERVICE_DATA_B = 251
        SOFTWARE_VERSION_SECONDARY_CONTROLLER = 252
        SOFTWARE_VERSION_MAIN_CONTROLLER = 253
        TIME_OF_BUILD = 254
        DATE_OF_BUILD = 255

    class METADATA(enum.IntEnum):
        DEVICE_UUID = 1
        BUSINESS_UNIT = 2
        BLE_PROFILE = 3
        DEVICE_TYPE = 4
        DEVICE_PCBA = 5
        SW_VER_BLUETOOTH_CONTROLLER = 6
        SW_VER_SYSTEM_CONTROLLER_1 = 7
        SW_VER_SYSTEM_CONTROLLER_2 = 8
        GIT_COMMIT_HASH = 9
        SONOS_TYPE = 255

    command: uint8
    parameter: uint8 // _cmd_condition = 0

    @classmethod
    def factory_reset(cls) -> "Control":
        return cls(Control.Command.FACTORY_RESET, 82)

    @classmethod
    def extend_connection(cls, seconds=0xFF) -> "Control":
        return cls(Control.Command.EXTEND_CONNECTION, seconds)

    @classmethod
    def read_metadata(cls, meta: "Control.METADATA") -> "Control":
        return cls(Control.Command.READ_METADATA, meta)

    @classmethod
    def dashboard(cls) -> "Control":
        return cls(Control.Command.DASHBOARD)

    @classmethod
    def change_mode(cls, value: int) -> "Control":
        return cls(16, value)

    @classmethod
    def motor_ramping(cls, value: int) -> "Control":
        return cls(46, value)

    @classmethod
    def read_data(cls, value: "Control.DataRead") -> "Control":
        return cls(Control.Command.READ_DATA, value)
