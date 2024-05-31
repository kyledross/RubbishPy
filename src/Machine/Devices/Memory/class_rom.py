import threading

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
    _memory : list
        a list to store the memory of the ROM device

    Methods
    -------
    __init__(starting_address):
        Constructs all the necessary attributes for the ROM device.
    cycle(address_bus, data_bus, control_bus, interrupt_bus):
        Executes a cycle of the ROM device.
    """

    def start(self):
        threading.Thread(target=self.process_buses, name=self.get_device_id() + "::process_buses").start()

    _memory = []

    def __init__(self, starting_address, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructs all the necessary attributes for the ROM device.

        Parameters:
            starting_address (int): The starting address of the ROM device.
        """
        self._memory.append(InstructionSet.LR)
        self._memory.append(1)
        self._memory.append(1)
        self._memory.append(InstructionSet.LR)
        self._memory.append(2)
        self._memory.append(2)
        self._memory.append(InstructionSet.ADD)
        self._memory.append(InstructionSet.DEBUG)
        self._memory.append(InstructionSet.JMP)
        self._memory.append(0)
        super().__init__(starting_address, len(self._memory), address_bus, data_bus, control_bus, interrupt_bus)

    def process_buses(self):
        while self.is_running():
            self.control_bus().lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus().is_power_on():
                if self.address_is_valid(self.address_bus()):
                    if self.control_bus().get_read_request():
                        self.data_bus().set_data(
                            self._memory[self.address_bus().get_address() - super().starting_address])
                        self.control_bus().set_read_request(False)
                        self.control_bus().set_response(True)
            self.control_bus().unlock_bus()
        self.set_finished()
