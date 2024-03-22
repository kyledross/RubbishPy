#  Copyright (c) 2024. Kyle D. Ross.  All rights reserved.

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class Debugger(BaseDevice):

    def __init__(self):
        super().__init__(0, 0)

    def cycle(self, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        print("Debugger")
        print(f"AddressBus: {address_bus.get_address()}")
        print(f"DataBus: {data_bus.get_data()}")
        print()
        input("Press enter to continue...")

        pass
