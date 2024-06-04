import threading
from typing import List

from Constants.class_instruction_set import InstructionSet
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class ROM(BaseDevice):
    """
    A class used to represent a ROM device.

    ...

    Attributes
    ----------
    __memory : list
        a list to store the memory of the ROM device

    Methods
    -------
    __init__(starting_address):
        Constructs all the necessary attributes for the ROM device.
    cycle(address_bus, data_bus, control_bus, interrupt_bus):
        Executes a cycle of the ROM device.
    """

    def start(self):
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()

    def __init__(self, starting_address: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructs all the necessary attributes for the ROM device.

        Parameters:
            starting_address (int): The starting address of the ROM device.
        """
        self.__memory: List[int] = []
        self.__memory.append(InstructionSet.LR)
        self.__memory.append(1)
        self.__memory.append(1)
        self.__memory.append(InstructionSet.LR)
        self.__memory.append(2)
        self.__memory.append(2)
        self.__memory.append(InstructionSet.ADD)
        self.__memory.append(InstructionSet.DEBUG)
        self.__memory.append(InstructionSet.JMP)
        self.__memory.append(0)
        super().__init__(starting_address, len(self.__memory), address_bus, data_bus, control_bus, interrupt_bus)

    @property
    def memory(self) -> List[int]:
        """
        This method returns the memory of the ROM device.
        :return: The memory of the ROM device.
        """
        return self.__memory

    @memory.setter
    def memory(self, value: List[int]):
        """
        This method sets the memory of the ROM device.
        :param value: The memory to set for the ROM device.
        """
        self.__memory = value

    def process_buses(self):
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                if self.address_is_valid(self.address_bus):
                    if self.control_bus.read_request:
                        self.data_bus.data = self.memory[self.address_bus.address - super().starting_address]
                        self.control_bus.read_request = False
                        self.control_bus.response = True
            self.control_bus.unlock_bus()
        self.finished = True
