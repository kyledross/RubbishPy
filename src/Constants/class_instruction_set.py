from enum import IntFlag


class InstructionSet(IntFlag):
    """
    The InstructionSet class represents the set of instructions that the Rubbish language supports.
    Each instruction is represented by a class variable with a unique integer value.
    """
    DoNotUse = -1
    NOP = 0  # No operation instruction
    LR = 1  # Load register instruction
    LRM = 2  # Load register from memory instruction
    LRR = 3  # Load register from register instruction
    MRM = 4  # Move register to memory instruction
    ADD = 5  # Addition instruction
    SUB = 6  # Subtraction instruction
    MUL = 7  # Multiplication instruction
    DIV = 8  # Division instruction
    HALT = 9  # Halt instruction
    DEBUG = 10  # Debug instruction
    JMP = 11  # Jump instruction
    RST = 12  # Reset instruction
    CMP = 13  # Compare instruction
    JE = 14  # Jump if equal instruction
    JNE = 15  # Jump if not equal instruction
    JL = 16  # Jump if less instruction
    JG = 17  # Jump if greater instruction
    PUSH = 18  # Push to stack instruction
    POP = 19  # Pop from stack instruction
    CALL = 20  # Call subroutine instruction
    RTN = 21  # Return from subroutine instruction
    NOT = 22  # Bitwise NOT instruction
    OR = 23  # Bitwise OR instruction
    AND = 24  # Bitwise AND instruction
    XOR = 25  # Bitwise XOR instruction
    SIV = 26  # Set interrupt vector instruction
    INC = 27  # Increment instruction
    SLEEP = 28  # Sleep instruction
    WAKE = 29  # Wake instruction
    PEEK = 34  # Peek at top of stack instruction
