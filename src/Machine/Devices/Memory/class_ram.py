import threading
from typing import List

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class RAM(BaseDevice):
    """
    A class used to represent a RAM device.

    ...

    Attributes
    ----------
    __memory : list
        a list to store the memory of the RAM device

    Methods
    -------
    __init__(starting_address, size):
        Constructs all the necessary attributes for the RAM device.
    load_data(data):
        Loads data into the RAM device.
    cycle(address_bus, data_bus, control_bus, interrupt_bus):
        Executes a cycle of the RAM device.
    """

    def start(self) -> None:
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()

    def __init__(self, starting_address: int, size: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructs all the necessary attributes for the RAM device.

        Parameters:
            starting_address (int): The starting address of the RAM device.
            size (int): The size of the RAM device.
        """
        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self.__memory: List[int] = [0] * size

    @property
    def memory(self) -> List[int]:
        """
        This method returns the memory of the RAM device.
        :return: The memory of the RAM device.
        """
        return self.__memory

    @memory.setter
    def memory(self, value: List[int]):
        """
        This method sets the memory of the RAM device.
        :param value: The memory to set for the RAM device.
        """
        self.__memory = value

    def load_data(self, data: List[int]):
        """
        Loads data into the RAM device.

        Parameters:
            data (list): The data to be loaded into the RAM device.

        Raises:
            ValueError: If the length of the data is greater than the memory size.
        """
        if len(data) > len(self.memory):
            raise ValueError("Data must be the same length or less as the memory size.")
        memory_size = len(self.memory)
        self.memory.clear()
        self.memory += data
        self.memory += [0] * (memory_size - len(self.memory))

    def process_buses(self) -> None:
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                if self.address_is_valid(self.address_bus):
                    if self.control_bus.read_request:
                        self.data_bus.data = self.__memory[self.address_bus.address - self.starting_address]
                        self.control_bus.read_request = False
                        self.control_bus.response = True
                    if self.control_bus.write_request:
                        self.__memory[self.address_bus.address - self.starting_address] = (
                            self.data_bus.data)
                        self.control_bus.write_request = False
                        self.control_bus.response = True
            self.control_bus.unlock_bus()
        self.finished = True
