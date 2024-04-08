#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.
import Constants.class_interrupts
from Constants.class_interrupts import Interrupts


class InterruptBus:
    """
    The InterruptBus class represents the interrupt bus of a computer system.
    It provides methods to set, test, and clear interrupts on the bus.
    """

    _interruptBus: Constants.class_interrupts.IntFlag = Interrupts.none

    def __init__(self):
        """
        Constructor for the InterruptBus class.
        Initializes the interrupts on the bus to 0.
        """
        self._interruptBus = Interrupts.none

    def set_interrupt(self, value: Constants.class_interrupts):
        """
        This method sets an interrupt on the bus.
        It uses bitwise OR to set the interrupt.
        :param value: The interrupt to set on the bus.
        """
        self._interruptBus = self._interruptBus | value

    def test_interrupt(self, interrupt_number: Constants.class_interrupts) -> bool:
        """
        This method tests if a specific interrupt is set on the bus.
        It uses bitwise AND to test the interrupt.
        :param interrupt_number: The interrupt to test on the bus.
        :return: True if the interrupt is set, False otherwise.
        """
        return self._interruptBus & interrupt_number != Interrupts.none

    def clear_interrupt(self, interrupt_number: Constants.class_interrupts):
        """
        This method clears a specific interrupt on the bus.
        It uses bitwise AND with bitwise NOT to clear the interrupt.
        :param interrupt_number: The interrupt to clear on the bus.
        """
        self._interruptBus = self._interruptBus & ~interrupt_number
