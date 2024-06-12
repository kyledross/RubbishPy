class AddressBus:
    """
    The AddressBus class represents the address bus of a computer system.
    It provides methods to get and set the address on the bus.
    """

    def __init__(self) -> None:
        """
        Constructor for the AddressBus class.
        Initializes the address on the bus to 0.
        """
        self.__AddressBus = 0

    @property
    def address(self) -> int:
        """
        This method returns the address on the bus.
        :return: The address on the bus.
        """
        return self.__AddressBus

    @address.setter
    def address(self, value: int):
        """
        This method sets the address on the bus.
        :param value: The address to set on the bus.
        """
        self.__AddressBus = value
