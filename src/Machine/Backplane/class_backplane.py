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

    def address_bus(self):
        return self._addressBus

    def data_bus(self):
        return self._dataBus

    def control_bus(self):
        return self._controlBus

    def interrupt_bus(self):
        return self._interruptBus

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
        The backplane runs creates instances of the buses and allows the devices to run on them.
        When a HALT interrupt is detected, cycling stops.

        Raises:
            None
        """
        self.control_bus().power_on()
        while self.control_bus().is_power_on():
            self.control_bus().lock_bus()
            if self._interruptBus.test_interrupt(Interrupts.halt):
                print("HALT interrupt detected.")
                self.control_bus().power_off()
                break
            self.control_bus().unlock_bus()
        self.wait_for_devices_to_finish()

    def wait_for_devices_to_finish(self):
        print("Waiting for devices to finish.")
        devices_busy = True
        while devices_busy:
            devices_busy = False
            for device in self._devices:
                if device.finished() is False:
                    devices_busy = True
                    break
            time.sleep(.1)

