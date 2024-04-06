#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.txt for license information.

class AddressBus:
    """
    The AddressBus class represents the address bus of a computer system.
    It provides methods to get and set the address on the bus.
    """

    _AddressBus: int = 0  # The address on the bus

    def __init__(self):
        """
        Constructor for the AddressBus class.
        Initializes the address on the bus to 0.
        """
        self._AddressBus = 0

    def get_address(self) -> int:
        """
        This method returns the address on the bus.
        :return: The address on the bus.
        """
        return self._AddressBus

    def set_address(self, value: int):
        """
        This method sets the address on the bus.
        :param value: The address to set on the bus.
        """
        self._AddressBus = value
