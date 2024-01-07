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
from .advertise import ProtocolVersion, is_brush, COMPANY_ID
from .sonos import Model
from ._model import (
    BASE_UUID,
    characteristic,
    make_uuid,
    OTACommand,
    OTAPayload,
    OTAState,
    OTATransferSize,
    Color,
    DeviceState,
    Pressure,
    TongueTime,
    Timezone,
    UserID,
    RTC,
    Smiley,
)
from .brush import (
    BrushAdvertisement,
    BrushInfo,
    BrushingMode,
    BrushingTime,
    BrushModes,
    BrushType,
    Quadrant,
    State,
    Status,
    Mode,
    ToothbrushQuadrant,
)
from .client import OralBClient, OralBProperty