import Constants.class_interrupts
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class InterruptTester(BaseDevice):
    def __init__(self, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        super().__init__(0, 0, address_bus, data_bus, control_bus, interrupt_bus)

    def cycle(self, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        force_interrupt = False
        if force_interrupt:
            interrupt_bus.set_interrupt(Constants.class_interrupts.Interrupts.irq1)
