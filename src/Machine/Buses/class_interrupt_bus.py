import Constants.class_interrupts
from Constants.class_interrupts import Interrupts

# todo: the structure of interrupts really needs to change
# this implementation tries to replicate bitwise interrupts, and that ends up being just wonky
# in the real world, an interrupt is an interrupt.  interrupt 3 isn't interrupts 1 and 2... it's 3
# so rather than be a bitmap, the interrupt bus needs to be a dictionary of bits with the key being the interrupt
# number and the value being the state

class InterruptBus:
    """
    The InterruptBus class represents the interrupt bus of a computer system.
    It provides methods to set, test, and clear interrupts on the bus.
    """

    def __init__(self) -> None:
        """
        Constructor for the InterruptBus class.
        Initializes the interrupts on the bus to 0.
        """
        self.__interruptBus = Interrupts.none

    def interrupt_awaiting(self) -> Interrupts:
        """
        This method checks if any interrupts are set on the bus and, if so, returns the interrupt number to handle.
        Interrupts with lower numbers have priority.
        :return: The highest-priority interrupt number to handle, or none if no interrupts are set.
        """
        if self.__interruptBus == Interrupts.none:
            return Interrupts.none
        for interruptBit in range(0, 32):
            interrupt_number: Interrupts = 2 ** interruptBit
            if self.test_interrupt(interrupt_number):
                return interrupt_number

    def set_interrupt(self, value: Constants.class_interrupts):
        """
        This method sets an interrupt on the bus.
        It uses bitwise OR to set the interrupt.
        :param value: The interrupt to set on the bus.
        """
        self.__interruptBus = self.__interruptBus | value

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
