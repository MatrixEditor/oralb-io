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
import pathlib
import json
import base64
import hashlib

from typing import List
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from oralb.exceptions import InvalidChecksum

SIGNATURE_SEPARATOR = b"\n---------- SIGNATURE ----------\n"


def get_public_key() -> rsa.RSAPublicKey:
    parent = pathlib.Path(__file__).parent
    with open(str(parent / "publickey.pem"), "rb") as key_file:
        return load_pem_public_key(key_file.read())


PUBLIC_KEY = get_public_key()


def _convert_hex(values: List[str]) -> List[int]:
    return list(map(lambda x: int(x, base=16), values))


class OTAImageInfo(dict):
    @property
    def notes(self) -> str:
        return self["notes"]

    @property
    def url(self) -> str:
        return self["url"]

    @property
    def version(self) -> int:
        return int(self["version"], base=16)

    @property
    def min_required(self) -> int:
        return int(self["minRequiredVersion"], base=16)

    @property
    def supported_bootloaders(self) -> List[int]:
        return _convert_hex(self["supportedBootloaderVersions"])

    @property
    def supported_2nd_controllers(self) -> List[int]:
        return _convert_hex(self["supported2ndControllerVersions"])

    @property
    def supported_info_sectors(self) -> List[int]:
        return _convert_hex(self["supportedInfoSectorVersions"])

    @property
    def supported_memory_maps(self) -> List[int]:
        return _convert_hex(self["supportedMemoryMapVersions"])

    @property
    def supported_media_contents(self) -> List[int]:
        return _convert_hex(self["supportedMediaContentVersions"])

    @property
    def checksum(self) -> str:
        return self["fileChecksum"]

    @property
    def checksum_type(self) -> str:
        return self["fileChecksum"]

    @property
    def countries(self) -> List[str]:
        return self["countries"]

    def verify(self, path: str) -> None:
        if self.checksum_type != "MD5":
            raise NotImplementedError(
                f"Checksum type {self.checksum_type!r} not implemented!"
            )

        with open(path, "rb") as fp:
            digest = hashlib.file_digest(fp, hashlib.md5)

        if digest != self.checksum:
            raise InvalidChecksum(self.checksum, digest)


class OTAHardwareInfo(dict):
    @property
    def pcba(self) -> List[int]:
        return _convert_hex(self["PCBA"])

    @property
    def config(self) -> List[int]:
        return _convert_hex(self["hardwareConfiguration"])

    @property
    def images(self) -> List[OTAImageInfo]:
        return list(map(OTAImageInfo, self["images"]))


class OTAFirmwareInfo(dict):
    def __init__(self, manifest: bytes, signature: bytes) -> None:
        super().__init__(json.loads(manifest))
        self.signature = signature
        self.manifest = manifest

    @property
    def sig_algorithm(self) -> str:
        return self["signatureAlgorithm"]

    @property
    def sig_encoding(self) -> str:
        return self["signatureEncoding"]

    @property
    def hardware(self) -> List[OTAHardwareInfo]:
        return list(map(OTAHardwareInfo, self["hardwareMapping"]))

    @classmethod
    def from_bytes(cls, data: bytes) -> "OTAFirmwareInfo":
        index = data.rfind(SIGNATURE_SEPARATOR)
        if index == -1:
            raise ValueError("Invalid input data - could not find 'SIGNATURE'!")

        json_data = data[:index]
        # We have to skip the separator string and a trailing newline
        signature = data[index + len(SIGNATURE_SEPARATOR) :].strip()
        return OTAFirmwareInfo(json_data, signature)

    @classmethod
    def from_file(cls, path: str) -> "OTAFirmwareInfo":
        with open(path, "rb") as fp:
            return OTAFirmwareInfo.from_bytes(fp.read())

    def verify(self) -> None:
        if self.sig_algorithm != "SHA256WithRSA":
            raise ValueError(f"Unknown signature algorithm: {self.sig_algorithm!r}")

        key = PUBLIC_KEY
        # The signature may be encoded using base64
        signature = self.signature
        if self.sig_encoding == "base64":
            signature = base64.b64decode(self.signature)

        # SHA256withRSA uses PKCS#1 v1.5 padding, so we can simply verify the
        # encoded data
        key.verify(signature, self.manifest, padding.PKCS1v15(), SHA256())
