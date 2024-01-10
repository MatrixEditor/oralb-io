.. _usage:

*********
CLI Usage
*********

After installation completes, there will be an additional command that can be executed: :code:`oralbcli`. It will
start an interactive command shell:

.. code-block:: console
    :caption: Running the client

    (venv-3.12.1) Python> oralbcli
    (oralb)> # ...


Discovering devices
-------------------

Before we can connect to the device, we need its address. To list all local devices, use :code:`ble discover`:

.. figure:: _static/ble-discover.gif

    Sample device discovery


Connecting to devices
---------------------

To establish a connection, the client will first *connect* to the device, then it tries to
*pair* with the device and lastly it writes a special command to extend the connection for
:code:`255` seconds.

.. warning::
    Connecting can be painful sometimes, as you may need to call `connect` multiple times.

.. code-block:: console
    :caption: Successfull connection to device (address from brefore)

    (oralb)> dm connect "74:B8:39:16:06:1B"
    [   Ok   ] Connected to '74:B8:39:16:06:1B'


Extending a connection
^^^^^^^^^^^^^^^^^^^^^^

If you wish to extend the current connection by another :code:`255` seconds manually, there
is another command that can be utilized:

.. code-block:: console
    :caption: There will be no terminal respose if everything worked.

    (oralb)> dm extend-connection
    (oralb)>


Reading characteristics
-----------------------

Characteristics can be selected on several ways:

.. image:: _static/dm-getchar.gif

Okay, lets break down the different options:

* by-name: each characteristic stores an internal name, which can be used here to retrieve its value
* by-cid: another way is to use the short UUID for device characteristics
* by-uuid: or just past the whole UUID

.. note::
    The response of unknown characteristics will be displayed as plain bytes.

Reading special data
^^^^^^^^^^^^^^^^^^^^

There are special commands that lets you read special device data such as a detailed SONOS type
description, or service data information.

.. code-block:: console
    :caption: Reading metadata and special device data

    (oralb)> dm control read-meta sonos_type
    SonosMetadata(
        magic=255,
        model=<Model.M6: 4>,
        color=<Color.STORMY_GREY: 5>,
        language=<Language.ENGLISH_EN: 0>,
        brush_modes=[0, 1, 3, 2, 4, 7, 7, 7],
        gum_guard=6
    )
    (oralb)> dm control read-data service_data_a
    ServiceDataA(
        ideal_full_capacity=0,
        average_motor_current=0,
        total_monitor_runtime=978,
        total_pressure=34,
        total_charge_time=28921
    )

.. tip::
    The names for metadata or normal data values can be taken from
    :class:`~oralb.blesdk.model.Control.DataRead` and
    :class:`~oralb.blesdk.model.Control.METADATA`.

Writing characteristics (Experimental)
--------------------------------------

It is also possible to apply new values to certain characteristics. Make sure to check whether
the characteristic supports the *write* operation before calling :code:`putchar`.

.. code-block:: console

    (oralb)> dm putchar [$NAME | $CID] args

Here you have the option to use the characteristic's name or its short UUID as described before.
You can view the list of required arguments using :code:`-h`.

.. code-block:: console
    :caption: Required arguments for changing the current smiley configuration

    (oralb)> dm putchar smiley -h
    usage: dm putchar smiley [-h] --face FACE

    Smiley

    options:
        -h, --help   show this help message and exit
        --face FACE  type: int


