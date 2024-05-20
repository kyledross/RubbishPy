#  MIT License
#
#  Copyright (c) 2024 Kyle D. Ross
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
    _memory : list
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

    _memory = []

    def __init__(self, starting_address, size):
        """
        Constructs all the necessary attributes for the RAM device.

        Parameters:
            starting_address (int): The starting address of the RAM device.
            size (int): The size of the RAM device.
        """
        super().__init__(starting_address, size)
        self._memory = [0] * size

    def load_data(self, data):
        """
        Loads data into the RAM device.

        Parameters:
            data (list): The data to be loaded into the RAM device.

        Raises:
            ValueError: If the length of the data is greater than the memory size.
        """
        if len(data) > len(self._memory):
            raise ValueError("Data must be the same length or less as the memory size.")
        memory_size = len(self._memory)
        self._memory = []
        self._memory += data
        self._memory += [0] * (memory_size - len(self._memory))

    def cycle(self, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Executes a cycle of the RAM device.

        Parameters:
            address_bus (AddressBus): The address bus.
            data_bus (DataBus): The data bus.
            control_bus (ControlBus): The control bus.
            interrupt_bus (InterruptBus): The interrupt bus.
        """
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                data_bus.set_data(self._memory[address_bus.get_address() - super().starting_address])
                control_bus.set_read_request(False)
                control_bus.set_response(True)
            if control_bus.get_write_request():
                self._memory[address_bus.get_address() - super().starting_address] = data_bus.get_data()
                control_bus.set_write_request(False)
                control_bus.set_response(True)
