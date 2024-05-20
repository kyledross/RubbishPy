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

class InstructionSet:
    """
    The InstructionSet class represents the set of instructions that the Rubbish language supports.
    Each instruction is represented by a class variable with a unique integer value.
    """

    NOP = 0  # No operation instruction
    LR = 1  # Load register instruction
    LRM = 2  # Load register from memory instruction
    LRR = 3  # Load register from register instruction
    MRM = 4  # Move register to memory instruction
    ADD = 5  # Addition instruction
    DIV = 8  # Division instruction
    MUL = 7  # Multiplication instruction
    SUB = 6  # Subtraction instruction
    DEBUG = 10  # Debug instruction
    JMP = 11  # Jump instruction
    HALT = 9  # Halt instruction
    RST = 12  # Reset instruction
    CMP = 13  # Compare instruction
    JE = 14  # Jump if equal instruction
    JNE = 15  # Jump if not equal instruction
    JL = 16  # Jump if less instruction
    JG = 17  # Jump if greater instruction
    PUSH = 18  # Push to stack instruction
    POP = 19  # Pop from stack instruction
    PEEK = 34  # Peek at top of stack instruction
    CALL = 20  # Call subroutine instruction
    RTN = 21  # Return from subroutine instruction
    NOT = 22  # Bitwise NOT instruction
    OR = 23  # Bitwise OR instruction
    AND = 24  # Bitwise AND instruction
    XOR = 25  # Bitwise XOR instruction
    SIV = 26  # Set interrupt vector instruction
    SLEEP = 28  # Sleep instruction
    WAKE = 29  # Wake instruction
    # noinspection SpellCheckingInspection
    DEBUGOUT = 35  # Debug output instruction
    # noinspection SpellCheckingInspection
    DEBUGPUSH = 36  # Debug push instruction
