from enum import IntFlag


class Interrupts(IntFlag):
    """
    The Interrupts class represents the different types of interrupts that can be set on the interrupt bus.
    Interrupts with lower numbers have higher priority.
    """
    none: int = 0
    """
    Represents no active interrupts.
    """
    # represents no active interrupts
    irq1: int = 1  # Represents the first interrupt request line
    irq2: int = 2  # Represents the second interrupt request line
    irq3: int = 3  # Represents the third interrupt request line
    irq4: int = 4  # Represents the fourth interrupt request line
    irq5: int = 5  # Represents the fifth interrupt request line
    irq6: int = 6  # Represents the sixth interrupt request line
    irq7: int = 7  # Represents the seventh interrupt request line
    irq8: int = 8  # Represents the eighth interrupt request line
    halt: int = 9
    """
    Represents the halt interrupt. This should be raised when a device in the system is requesting the system to halt.
    Devices in the system should monitor this interrupt and perform the necessary actions to halt the system.
    """
