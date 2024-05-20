#  MIT License
#
#  Copyright (c) 2024 Kyle D. Ross
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
