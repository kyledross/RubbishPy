import Constants.class_interrupts
from Constants.class_interrupts import Interrupts


class InterruptBus:
    """
    The InterruptBus class represents the interrupt bus of a computer system.
    It provides methods to set, test, and clear interrupts on the bus.
    """

    def __init__(self):
        """
        Constructor for the InterruptBus class.
        Initializes the interrupts on the bus to 0.
        """
        self.__interruptBus = Interrupts.none

    def set_interrupt(self, value: Constants.class_interrupts) -> bool:
        """
        This method sets an interrupt on the bus.
        It uses bitwise OR to set the interrupt.
        :param value: The interrupt to set on the bus.
        """
        if self.__interruptBus == Interrupts.none:
            self.__interruptBus = self.__interruptBus | value
            return True
        return False

    def test_interrupt(self, interrupt_number: Constants.class_interrupts) -> bool:
        """
        This method tests if a specific interrupt is set on the bus.
        It uses bitwise AND to test the interrupt.
        :param interrupt_number: The interrupt to test on the bus.
        :return: True if the interrupt is set, False otherwise.
        """
        return self.__interruptBus & interrupt_number != Interrupts.none

    def clear_interrupt(self, interrupt_number: Constants.class_interrupts):
        """
        This method clears a specific interrupt on the bus.
        It uses bitwise AND with bitwise NOT to clear the interrupt.
        :param interrupt_number: The interrupt to clear on the bus.
        """
        self.__interruptBus = self.__interruptBus & ~interrupt_number
