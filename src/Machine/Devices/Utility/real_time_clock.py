import threading
from datetime import timezone
from typing import List

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


class RTC(BaseDevice):
    """
    A class used to represent a real-time clock device.
    """

    # address map
    # address = UTC offset whole
    # address + 1 = UTC offset fraction
    # address + 2 = year
    # address + 3 = month
    # address + 4 = day
    # address + 5 = hour (0-23)
    # address + 6 = minute
    # address + 7 = second

    def start(self) -> None:
        """
        This method starts the RTC device.
        Returns:

        """
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()

    def __init__(self, starting_address: int, interrupt: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructs all the necessary attributes for the RTC device.

        Parameters:
            starting_address (int): The starting address of the RTC device.
            interrupt (int): The interrupt that will be raised on every interval

        """
        import time
        self._last_checked_time = time.time() * 1000  # Initialize with the current time in milliseconds
        size = 8
        self.interval_interrupt = interrupt
        self.interval_milliseconds = 1000
        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self.__memory: List[int] = [0] * size

    @property
    def memory(self) -> List[int]:
        """
        This method returns the memory of the RTC device.
        :return: The memory of the RTC device.
        """
        return self.__memory

    @memory.setter
    def memory(self, value: List[int]):
        """
        This method sets the memory of the RTC device.
        :param value: The memory to set for the RTC device.
        """
        self.__memory = value

    def process_buses(self) -> None:
        self.main_loop()
        self.finished = True

    def main_loop(self) -> None:
        """
        The main loop of the RTC device.  This runs continuously to monitor for read and write requests.
        Returns:

        """
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

            # Add call to check_interval
            self.check_interval()
            self.control_bus.unlock_bus()

    @staticmethod
    def compute_current_datetime(utc_offset: float) -> dict:
        """
        Compute the current date and time as a dictionary using the UTC offset stored in memory.
    
        Parameters:
            utc_offset (float): The UTC offset to apply (e.g., -5.5 for UTC-5:30).
    
        Returns:
            dict: A dictionary with separated time components (year, month, day, hour, minute, second).
        """
        from datetime import datetime, timedelta
        current_utc_time = datetime.now(tz=timezone.utc)
        adjusted_time = current_utc_time + timedelta(hours=utc_offset)
        return {
            "year": adjusted_time.year,
            "month": adjusted_time.month,
            "day": adjusted_time.day,
            "hour": adjusted_time.hour,
            "minute": adjusted_time.minute,
            "second": adjusted_time.second
        }

    def check_interval(self) -> None:
        """
        This method checks if the specified interval in milliseconds has elapsed
        and performs actions if required. 
        """
        import time
        current_time = time.time() * 1000  # Convert current time to milliseconds
        if not hasattr(self, "_last_checked_time"):
            self._last_checked_time = current_time  # Initialize last checked time
        if current_time - self._last_checked_time >= self.interval_milliseconds:
            # Perform the work here
            if self.interval_interrupt >= 0:
                utc_offset = self.memory[0] + self.memory[1] / 100
                current_datetime = self.compute_current_datetime(utc_offset)
                # Set memory values for the current Date & Time
                self.memory[2] = current_datetime["year"]
                self.memory[3] = current_datetime["month"]
                self.memory[4] = current_datetime["day"]
                self.memory[5] = current_datetime["hour"]
                self.memory[6] = current_datetime["minute"]
                self.memory[7] = current_datetime["second"]

                # Trigger the interrupt
                self.interrupt_bus.set_interrupt(self.interval_interrupt)

            self._last_checked_time = current_time  # Update last checked time
