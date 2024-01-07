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

# from urllib3.util.url import parse_url, Url
from typing import Any, Optional, List

FW_DEFAULT_HOST = "fw.iot-dev.alchemy.codes"
FW_CHINA_HOST = "email-assets-271825783008-cn-north-1.s3.cn-north-1.amazonaws.com.cn"


class CountryCode(enum.StrEnum):
    CHINA = "cn"
    GERMANY = "de"
    ITALY = "it"
    SPAIN = "es"
    USA = "us"


def info_url(
    model: int, host: Optional[str] = None, locale: Optional[str] = None
) -> str:
    # asia needs another host?
    if host is None:
        host = FW_DEFAULT_HOST
        if locale in ("cn", "hk", "mo"):
            host = FW_CHINA_HOST

    # The info url consists of three parts:
    #     1: host
    #     2: path to info document ("oralb" / <hex(model)>)
    #     3: document path
    path = f"oralb/0x{model:04X}/0x{model:04X}.json"
    return "/".join([host, path])


