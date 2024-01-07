# OralB IO

[![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FMatrixEditor%oralb-io%2Fmaster%2Fpyproject.toml&logo=python)](https://www.python.org/downloads/)
![GitHub issues](https://img.shields.io/github/issues/MatrixEditor/oralb-io?logo=github)
![GitHub License](https://img.shields.io/github/license/MatrixEditor/oralb-io?logo=github)

> [!WARNING]
> This library uses [red functions](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)! Be aware of that before using the API of this project.

A small project to be able to configure an Oral-B toothbrush using
the command line. Current features are:

* Discover all brushes in the local area
* Get specific characteristics from a brush

The following features are proposed but not implemented yet:

* Modify specific characteristics of a brush
* Update the brush using the CLI


## Installation

```bash
pip install git+https://github.com/MatrixEditor/oralb-io.git
```

## Usage

To start the CLI just type `oralbcli`.

### Discover nearby Bluetooth devices

The `ble` command can be used to view all Bluetooth devices in the area. Additionally,
advertisements from brushes will be displayed in detail:

```bash
(oralb)> ble discover
[  Info  ] Scan complete: found 17 devices.

                   Detailed device info
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━┓
┃ Address           ┃       Name        ┃ rssi ┃ isBrush ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━┩
│ 01:02:03:04:05:06 │       ....        │ -57  │  False  │
│ FF:FF:FF:FF:FF:FF │ Oral-B Toothbrush │ -46  │  True   │  # we need only the address
│ ...               │       None        │ -55  │  False  │
└───────────────────┴───────────────────┴──────┴─────────┘
[  Info  ] Located 1 brushes:

FF:FF:FF:FF:FF:FF: Oral-B Toothbrush
------------------------------------
BrushAdvertisement(
    protocol=<ProtocolVersion.V006: 6>,
    type=<Type.SONOS_BIG_TI: 50>,
    version=107,
    state=<State.POWER_PRESSED: 8>,
    status=<Status.PCB_TEST: 114>,
    brush_time_min=0,
    brush_time_sec=0,
    brush_mode=<V006Mode.V006_CLEAN: 0>,
    brush_progress=1,
    quadrant_completion=<Quadrant.FIRST_QUADRANT: 0>,
    total_quadrants=4
)
```

### Connect to a toothbrush

Before we can read data from the device, we have to connect to it.

> [!WARNING]
> The device **must** be actived the whole time. Otherwise you have to
> restart the shell and connect again. The *re-connect* mechanism is not
> fully applicable by now.

```bash
(oralb)> dm connect "FF:FF:FF:FF:FF:FF"
[   Ok   ] Connected to 'FF:FF:FF:FF:FF:FF'
```

Note that you may need to retry to connect to the device as sometimes
paring fails.

### Read characteristics

In order to read attributes, the device must be active:

```bash
(oralb)> dm getchar my_color
[   Ok   ] Value of 'A0F0FF2B-5047-4D53-8208-4F72616C2D42':

Color(red=0, green=255, blue=61, identifier=0)
```

is equivalent to

```bash
(oralb)> dm getchar FF2B
[   Ok   ] Value of 'A0F0FF2B-5047-4D53-8208-4F72616C2D42':

Color(red=0, green=255, blue=61, identifier=0)
```

and

```bash
(oralb)> dm getchar "A0F0FF2B-5047-4D53-8208-4F72616C2D42"
[   Ok   ] Value of 'A0F0FF2B-5047-4D53-8208-4F72616C2D42':

Color(red=0, green=255, blue=61, identifier=0)
```

## Firmware

Nothing interesting, seems to be encrypted and compressed.


## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.