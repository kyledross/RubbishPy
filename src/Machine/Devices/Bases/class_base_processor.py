#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class BaseProcessor(BaseDevice):
    """
    The BaseProcessor class is an abstract base class for all processors in the system.
    It inherits from the BaseDevice class and provides a common interface
    for all processors, including a method to cycle the processor.
    """

    def cycle(self, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        This method is an abstract method that must be implemented by all subclasses.
        It represents a cycle of the processor, which involves interaction with the buses.
        :param address_bus: The address bus to interact with.
        :param data_bus: The data bus to interact with.
        :param control_bus: The control bus to interact with.
        :param interrupt_bus: The interrupt bus to interact with.
        :raise NotImplementedError: If this method is called directly from the base class.
        """
        raise NotImplementedError
