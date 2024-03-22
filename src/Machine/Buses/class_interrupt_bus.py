#  Copyright (c) 2024. Kyle D. Ross.  All rights reserved.

class InterruptBus:
    """
    The InterruptBus class represents the interrupt bus of a computer system.
    It provides methods to set, test, and clear interrupts on the bus.
    """

    _interruptBus: int = 0  # The interrupts on the bus

    def __init__(self):
        """
        Constructor for the InterruptBus class.
        Initializes the interrupts on the bus to 0.
        """
        self._interruptBus = 0

    def set_interrupt(self, value: int):
        """
        This method sets an interrupt on the bus.
        It uses bitwise OR to set the interrupt.
        :param value: The interrupt to set on the bus.
        """
        self._interruptBus = self._interruptBus | value

    def test_interrupt(self, interrupt_number: int) -> bool:
        """
        This method tests if a specific interrupt is set on the bus.
        It uses bitwise AND to test the interrupt.
        :param interrupt_number: The interrupt to test on the bus.
        :return: True if the interrupt is set, False otherwise.
        """
        return self._interruptBus & interrupt_number != 0

    def clear_interrupt(self, interrupt_number: int):
        """
        This method clears a specific interrupt on the bus.
        It uses bitwise AND with bitwise NOT to clear the interrupt.
        :param interrupt_number: The interrupt to clear on the bus.
        """
        self._interruptBus = self._interruptBus & ~interrupt_number
