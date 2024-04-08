#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.
from enum import IntFlag


class Interrupts(IntFlag):
    """
    The Interrupts class represents the different types of interrupts that can be triggered in the system.
    Each interrupt is represented by a class variable with a unique integer value.
    """

    none: int = 0  # represents no active interrupts
    irq1: int = 1  # Represents the first interrupt request line
    irq2: int = 2  # Represents the second interrupt request line
    irq3: int = 3  # Represents the third interrupt request line
    irq4: int = 4  # Represents the fourth interrupt request line
    irq5: int = 5  # Represents the fifth interrupt request line
    irq6: int = 6  # Represents the sixth interrupt request line
    irq7: int = 7  # Represents the seventh interrupt request line
    irq8: int = 8  # Represents the eighth interrupt request line
    halt: int = 9  # Represents the halt interrupt
