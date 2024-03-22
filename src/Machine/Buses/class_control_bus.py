#  Copyright (c) 2024. Kyle D. Ross.
#  Refer to LICENSE.txt for license information.

class ControlBus:
    """
    The ControlBus class represents the control bus of a computer system.
    It provides methods to get and set the read request, write request, and response on the bus.
    """

    _ReadRequest: bool = False  # The read request on the bus
    _WriteRequest: bool = False  # The write request on the bus
    _Response: bool = False  # The response on the bus

    def __init__(self):
        """
        Constructor for the ControlBus class.
        Initializes the read request, write request, and response on the bus to False.
        """
        self._ReadRequest = False
        self._WriteRequest = False
        self._Response = False

    def get_read_request(self) -> bool:
        """
        This method returns the read request on the bus.
        :return: The read request on the bus.
        """
        return self._ReadRequest

    def set_read_request(self, value: bool):
        """
        This method sets the read request on the bus.
        :param value: The read request to set on the bus.
        """
        self._ReadRequest = value

    def get_write_request(self) -> bool:
        """
        This method returns the write request on the bus.
        :return: The write request on the bus.
        """
        return self._WriteRequest

    def set_write_request(self, value: bool):
        """
        This method sets the write request on the bus.
        :param value: The write request to set on the bus.
        """
        self._WriteRequest = value

    def get_response(self) -> bool:
        """
        This method returns the response on the bus and then sets the response to False.
        :return: The response on the bus.
        """
        if self._Response:
            self._Response = False
            return True
        else:
            return False

    def set_response(self, value: bool):
        """
        This method sets the response on the bus.
        :param value: The response to set on the bus.
        """
        self._Response = value
