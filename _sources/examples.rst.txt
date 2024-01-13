.. _examples:

********
Examples
********

This document tries to provide an overview of possible scenarios this library can be used
in. IT doesn't aim to be complete, considering this document as a starting point.

Establish a connection
----------------------

We can either use a context manager or manually connect the :class:`~oralb.blesdk.client.OralBClient`:

.. code-block:: python
    :linenos:

    from oralb.bledsk import OralBClient

    async def main():
        # use a contect manager that will automatically disconnect
        mac = "FF:FF:FF:FF:FF:FF"
        async with OralBClient(mac) as client:
            # by now, the client is connected and we can read or write
            # charactersistics.
            ...


Extending a connection
----------------------

The current implementation does not extend the established connection automatically. Therefore,
a custom command has to be sent to the device:

.. code-block:: python
    :linenos:

    # same procedure from above
    from oralb.blesdk import OralBClient, Control
    from oralb.blesdk.model import CH_CONTROL

    async def main():
        mac = "FF:FF:FF:FF:FF:FF"
        async with OralBClient(mac) as client:
            # 1. create control object. we can choose, how many seconds
            # we would like to extend the connection (1-255)
            command = Control.extend_connection(255)
            # 2. just write to the charactersistic
            await client.write(CH_CONTROL, command)


Reading and writing charactersistics
------------------------------------

We just saw an example of how to write to a certain charactersistic. To *read*
a value, there are two options:

.. code-block:: python
    :linenos:

    from caterpillar.shortcuts import pack
    from oralb.blesdk import OralBClient, Color
    from oralb.blesdk.model import CH_MY_COLOR

    async def main():
        mac = ...
        async with OralBClient(mac) as client:
            # Either you reference the characteristic by its name
            value: Color = await client.my_color
            # or you read the raw data
            data: bytes = await client.read(CH_MY_COLOR)

            # -- Writing --
            # Same as above, either you use the attribute access,
            await client.my_color.set(new_value=value)
            # or just write the data by yourself
            data = pack(value)
            await client.write(CH_MY_COLOR, data, response=True)


Generating an update URL
------------------------

The OTA firmware is delivered using special URLs which are defined in an update
manifest that has to be downloaded first.

.. code-block:: python
    :linenos:

    from oralb.ota import info_url, OTAFirmwareInfo
    from oralb.blesdk import BrushType

    # select your brush type
    model = BrushType.SONOS_BIG_TI

    # generate the corresponding URL (use your current locale
    # if you are from china)
    url = info_url(model)

    # download the raw manifest using the URL (the host returns 403
    # if no update is available)
    data: bytes = ...

    # load the firmware info from the received data
    info = OTAFirmwareInfo.from_bytes(data)

    # The 'info' object is a dictionary with special attributes
    # and a .verify() function.
    info.verify()


