#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

from abc import abstractmethod
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_control_bus import ControlBus


class BaseDevice:
    """
    The BaseDevice class is an abstract base class for all devices in the system.
    It provides a common interface for all devices, including a method to
    cycle the device and check if an address is valid.
    """

    _startingAddress: int = 0  # The starting address of the device
    _size: int = 0  # The size of the device

    def __init__(self, starting_address: int, size: int):
        """
        Constructor for the BaseDevice class.
        Initializes the starting address and size of the device.
        :param starting_address: The starting address of the device.
        :param size: The size of the device.
        """
        self._startingAddress = starting_address
        self._size = size

    @property
    def starting_address(self) -> int:
        """
        This property returns the starting address of the device.
        :return: The starting address of the device.
        """
        return self._startingAddress

    @property
    def size(self) -> int:
        """
        This property returns the size of the device.
        :return: The size of the device.
        """
        return self._size

    @abstractmethod
    def cycle(self, address_bus: AddressBus, data_bus: DataBus,
              control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        This method is an abstract method that must be implemented by all subclasses.
        It represents a cycle of the device, which involves interaction with the buses.
        :param address_bus: The address bus to interact with.
        :param data_bus: The data bus to interact with.
        :param control_bus: The control bus to interact with.
        :param interrupt_bus: The interrupt bus to interact with.
        :raise NotImplementedError: If this method is called directly from the base class.
        """
        raise NotImplementedError("BaseDevice.Cycle: You may not call this method directly. It must be implemented by "
                                  "a subclass.")

    def address_is_valid(self, address_bus: AddressBus) -> bool:
        """
        This method checks if an address on the address bus is valid for this device.
        An address is valid if it is within the range of the starting address and the size of the device.
        :param address_bus: The address bus to check the address from.
        :return: True if the address is valid, False otherwise.
        """
        if ((address_bus.get_address() >= self._startingAddress)
                and (address_bus.get_address() < self._startingAddress + self._size)):
            return True
        else:
            return False
