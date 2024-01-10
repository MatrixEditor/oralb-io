# OralB IO

[![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FMatrixEditor%2Foralb-io%2Fmaster%2Fpyproject.toml&logo=python)](https://www.python.org/downloads/)
![GitHub issues](https://img.shields.io/github/issues/MatrixEditor/oralb-io?logo=github)
![GitHub License](https://img.shields.io/github/license/MatrixEditor/oralb-io?logo=github)

> [!WARNING]
> This library uses [red functions](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)! Be aware of that before using the API of this project.

A small project to be able to configure an Oral-B toothbrush using
the command line. Current features are:

* Discover all brushes in the local area
* Get specific characteristics from a brush

The following features are proposed but not implemented yet:

* Modify specific characteristics of a brush (partial support)
* Request metadata information
* Update the brush using the CLI
* Protocol documentation

## Installation

```bash
pip install git+https://github.com/MatrixEditor/oralb-io.git
```

## Protocol

A final documentation is not published yet, but WIP. Use [/oralb/blesdk/model](https://github.com/MatrixEditor/oralb-io/blob/master/oralb/blesdk/model.py) as a reference.

## Usage

To start the CLI just type `oralbcli`.

### Discover nearby Bluetooth devices

The `ble` command can be used to view all Bluetooth devices in the area. Additionally,
advertisements from brushes will be displayed in detail:

![ble-discover](/Docs/source/_static/ble-discover.gif)

### Connect to a toothbrush

Before we can read data from the device, we have to connect to it.

> [!WARNING]
> The device **must** be actived the whole time. Otherwise you have to
> restart the shell and connect again. The *re-connect* mechanism is not
> fully applicable by now.
> You can try to extend the using `dm extend-connection`. If that fails,
> you have to connect again.

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

### Write characterisitcs

You can try to write new characteristics using `dm putchar`. The following example illustrates a sample write-process using the characteristic `00002a00` (device name):

```bash
(oralb)> dm putchar --no-response name --text "Hello, World!"
```

> [!TIP]
> Retrieve a list of all available structs using `dm putchar -h` and
> view specific options for a characteristic with `dm putchar $NAME -h`.

### List Bluetooth cpabilities

The device manager (`dm`) command supports displaying all bluetooth services
of a device:

```bash
(oralb)> dm list services
[  Info  ] Device services:

Device: FF:FF:FF:FF:FF:FF
├── 00001800-0000-1000-8000-00805f9b34fb (Handle: 1): 'Generic Access Profile'
│   ├── 00002a00-0000-1000-8000-00805f9b34fb (Handle: 2): 'Device Name' ['read', 'write-without-response', 'write']
...
├── 00001801-0000-1000-8000-00805f9b34fb (Handle: 12): 'Generic Attribute Profile'
├── a0f0ff00-5047-4d53-8208-4f72616c2d42 (Handle: 13): 'Unknown'
│   ├── a0f0ff01-5047-4d53-8208-4f72616c2d42 (Handle: 14): 'Handle ID' ['read']
│   ├── a0f0ff02-5047-4d53-8208-4f72616c2d42 (Handle: 17): 'Handle Type' ['read']
...
│   ├── a0f0ff0c-5047-4d53-8208-4f72616c2d42 (Handle: 55): 'Cache' ['read', 'write', 'notify']
│   └── a0f0ff0d-5047-4d53-8208-4f72616c2d42 (Handle: 59): 'Sensor Data' ['read', 'notify']
├── a0f0ff20-5047-4d53-8208-4f72616c2d42 (Handle: 63): 'Unknown'
│   ├── a0f0ff21-5047-4d53-8208-4f72616c2d42 (Handle: 64): 'Command Status' ['read', 'write', 'notify']
│   ├── a0f0ff22-5047-4d53-8208-4f72616c2d42 (Handle: 68): 'RTC' ['read', 'write']
...
└── a0f0ff80-5047-4d53-8208-4f72616c2d42 (Handle: 95): 'Unknown'
    ├── a0f0ff81-5047-4d53-8208-4f72616c2d42 (Handle: 96): 'OTA Command' ['read', 'write']
    ...
```


## Firmware

Nothing interesting, seems to be encrypted and compressed.


## License

Distributed under the GNU General Public License (V3). See [License](LICENSE) for more information.