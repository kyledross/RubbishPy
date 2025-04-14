from Constants.class_interrupts import Interrupts

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
        self.__activeInterrupts = {}

    def interrupt_awaiting(self) -> int:
        """
        This method checks if any interrupts are set on the bus and, if so, returns the interrupt number to handle.
        Interrupts with lower numbers have priority.
        :return: The highest-priority interrupt number to handle, or none if no interrupts are set.
        """
        if len(self.__activeInterrupts) == 0:
            return Interrupts.none
        
        highest_priority_interrupt = min(self.__activeInterrupts.keys())
        return highest_priority_interrupt

    def set_interrupt(self, value: int):
        """
        This method sets an interrupt on the bus.
        It uses bitwise OR to set the interrupt.
        :param value: The interrupt to set on the bus.
        """
        self.__activeInterrupts[value] = True


    def test_interrupt(self, interrupt_number: int) -> bool:
        """
        This method tests if a specific interrupt is set on the bus.
        It checks the presence of the interrupt in the set.
        :param interrupt_number: The interrupt to test on the bus.
        :return: True if the interrupt is present in the set, False otherwise.
        """
        return interrupt_number in self.__activeInterrupts


    def clear_interrupt(self, interrupt_number: int):
        """
        This method clears a specific interrupt on the bus.
        It uses bitwise AND with bitwise NOT to clear the interrupt.
        :param interrupt_number: The interrupt to clear on the bus.
        In general, this should only be used by the processor when it has handled the interrupt.
        Devices should refrain from clearing interrupts.
        """
        if interrupt_number in self.__activeInterrupts:
            del self.__activeInterrupts[interrupt_number]
