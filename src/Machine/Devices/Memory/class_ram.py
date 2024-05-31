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

    def start(self):
        threading.Thread(target=self.process_buses, name=self.get_device_id() + "::process_buses").start()

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

    def load_data(self, data: List[int]):
        """
        Loads data into the RAM device.

        Parameters:
            data (list): The data to be loaded into the RAM device.

        Raises:
            ValueError: If the length of the data is greater than the memory size.
        """
        if len(data) > len(self.__memory):
            raise ValueError("Data must be the same length or less as the memory size.")
        memory_size = len(self.__memory)
        self.__memory.clear()
        self.__memory += data
        self.__memory += [0] * (memory_size - len(self.__memory))

    def process_buses(self):
        while self.is_running():
            self.control_bus().lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus().is_power_on():
                if self.address_is_valid(self.address_bus()):
                    if self.control_bus().get_read_request():
                        self.data_bus().set_data(
                            self.__memory[self.address_bus().get_address() - self.starting_address])
                        self.control_bus().set_read_request(False)
                        self.control_bus().set_response(True)
                    if self.control_bus().get_write_request():
                        self.__memory[self.address_bus().get_address() - self.starting_address] = (
                            self.data_bus().get_data())
                        self.control_bus().set_write_request(False)
                        self.control_bus().set_response(True)
            self.control_bus().unlock_bus()
        self.set_finished()
