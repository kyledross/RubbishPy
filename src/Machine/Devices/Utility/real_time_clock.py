import threading

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice

class RealTimeClock(BaseDevice):

    _interrupt: int = -1
    def __init__(self, starting_address: int, interrupt: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructs all the necessary attributes for the RAM device.

        Parameters:
            starting_address (int): The address of the RTC value
            interrupt (int): The interrupt to raise every half-second
        """
        super().__init__(starting_address= starting_address, size = 1, address_bus=address_bus, data_bus=data_bus, control_bus=control_bus, interrupt_bus=interrupt_bus)
        if interrupt < 0:
            raise ValueError("Invalid interrupt number. Interrupt number must be non-negative.")
        self._interrupt = interrupt

    def start(self):
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()
        
    def process_buses(self) -> None:
        self.main_loop()
        self.finished = True

    def main_loop(self) -> None:
        """
        The main loop of the RTC device.  This runs continuously to monitor for read and write requests.
        Returns:
    
        """
        import time
        last_interrupt_time = time.time()  # Initialize the last interrupt time
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                if self.address_is_valid(self.address_bus):
                    if self.control_bus.read_request:
                        self.data_bus.data = int(time.time())  # Number of seconds since Unix epoch
                        self.control_bus.read_request = False
                        self.control_bus.response = True
                        self.interrupt_bus.clear_interrupt(self._interrupt)

                # Interrupt generation logic... a non-precision timer
                current_time = time.time()
                if current_time - last_interrupt_time >= 0.5:  # Check if half a second has elapsed
                    if self._interrupt != -1:
                        self.interrupt_bus.set_interrupt(self._interrupt)
                    last_interrupt_time = current_time  # Update the last interrupt time
            self.control_bus.unlock_bus()
