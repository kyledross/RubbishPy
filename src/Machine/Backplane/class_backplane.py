import time

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class BackPlane:
    """
    A class used to represent a BackPlane.

    ...

    Attributes
    ----------
    _devices : list
        a list to store the devices connected to the backplane
    _addressBus : AddressBus
        the address bus of the backplane
    _dataBus : DataBus
        the data bus of the backplane
    _controlBus : ControlBus
        the control bus of the backplane
    _interruptBus : InterruptBus
        the interrupt bus of the backplane

    Methods
    -------
    __init__():
        Constructs all the necessary attributes for the backplane.
    add_device(device):
        Adds a device to the backplane.
    run():
        Runs the backplane.
    """

    _devices = []
    _addressBus: AddressBus = None
    _dataBus: DataBus = None
    _controlBus: ControlBus = None
    _interruptBus: InterruptBus = None

    _cataloged_devices = {}

    def __init__(self):
        """
        Constructs all the necessary attributes for the backplane.
        """
        self._addressBus = AddressBus()
        self._controlBus = ControlBus()
        self._dataBus = DataBus(self._controlBus)
        self._interruptBus = InterruptBus()

    def add_device(self, device: BaseDevice):
        """
        Adds a device to the backplane.

        Parameters:
            device (BaseDevice): The device to be added to the backplane.
        """
        self._devices.append(device)

    def run(self):
        """
        Runs the backplane.
        The backplane runs in an infinite loop, cycling through all the devices
        connected to it.  When a HALT interrupt is detected, cycling stops.

        Raises:
            None
        """
        running: bool = True
        while running:
            for device in self._devices:
                device.cycle(self._addressBus, self._dataBus, self._controlBus, self._interruptBus)
                # if the device has set the response line, save the address it responded to
                if self._controlBus.read_response():
                    self._cataloged_devices[self._addressBus.get_address()] = device
                # if the device is requesting an address, and we've cataloged the responding device for the address,
                # cycle the responding device
                if ((self._controlBus.get_read_request() or self._controlBus.get_write_request())
                        and self._addressBus.get_address() in self._cataloged_devices):
                    cataloged_device = self._cataloged_devices[self._addressBus.get_address()]
                    cataloged_device.cycle(self._addressBus, self._dataBus, self._controlBus, self._interruptBus)
                    # now cycle the current device again to give it a chance to respond to the read/write request
                    device.cycle(self._addressBus, self._dataBus, self._controlBus, self._interruptBus)

                if self._interruptBus.test_interrupt(Interrupts.halt):
                    running = False
                    break
            time.sleep(0)  # allow other threads (such as console 3.1) to run
