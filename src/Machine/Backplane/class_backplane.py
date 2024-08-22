import time
from typing import List

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class BackPlane:
    """
    A class used to represent the machine's backplane.
    One or more devices are attached to the backplane.
    The backplane provides the buses for the devices.
    When the backplane is run, it starts each of the attached devices.
    """

    @property
    def address_bus(self) -> AddressBus:
        """
        The address bus of the backplane.

        """
        return self.__addressBus

    @property
    def data_bus(self) -> DataBus:
        """
        The data bus of the backplane.

        """
        return self.__dataBus

    @property
    def control_bus(self) -> ControlBus:
        """
        The control bus of the backplane.

        """
        return self.__controlBus

    @property
    def interrupt_bus(self) -> InterruptBus:
        """
        The interrupt bus of the backplane.

        """
        return self.__interruptBus

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes for the backplane.
        """
        self.__addressBus = AddressBus()
        self.__controlBus = ControlBus()
        self.__dataBus = DataBus(self.__controlBus)
        self.__interruptBus = InterruptBus()
        self.__devices: List[BaseDevice] = []

    def add_device(self, device: BaseDevice):
        """
        Adds a device to the backplane.

        Parameters:
            device (BaseDevice): The device to be added to the backplane.
        """
        self.__devices.append(device)

    def run(self) -> None:
        """
        Runs the backplane.
        The backplane calls the start method of each device attached to it to start the machine.

        """
        self.control_bus.power_on = True
        for device in self.__devices:
            device.start()
        while self.control_bus.power_on:
            self.control_bus.lock_bus()
            if self.interrupt_bus.test_interrupt(Interrupts.halt):
                print("HALT interrupt detected.")
                self.control_bus.power_on = False
            self.control_bus.unlock_bus()
            time.sleep(0)
        self.wait_for_devices_to_finish()

    def wait_for_devices_to_finish(self) -> None:
        """
        Waits for all devices to finish when the machine is halted.

        """
        print("Waiting for devices to finish.")
        devices_busy = True
        while devices_busy:
            devices_busy = False
            for device in self.__devices:
                if device.finished is False:
                    devices_busy = True
                    break
            time.sleep(.1)
