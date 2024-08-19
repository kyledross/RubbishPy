from enum import IntFlag


class CompareResults(IntFlag):
    """
    The CompareResults class is a class that represents the possible results of a compare operation.
    It contains three class variables: Equal, GreaterThan, and LessThan.
    These variables are used to represent the three possible outcomes of a comparison operation.
    """
    Inconclusive: int = -1
    Equal: int = 0  # Represents the case where the two operands are equal
    GreaterThan: int = 1  # Represents the case where the first operand is greater than the second
    LessThan: int = 2  # Represents the case where the first operand is less than the second
