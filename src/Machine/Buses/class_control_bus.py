import time
from threading import Lock


class ControlBus:
    """
    The ControlBus class represents the control bus of a computer system.
    It provides methods to get and set the read request, write request, and response on the bus.
    """

    _ReadRequest: bool = False  # The read request on the bus
    _WriteRequest: bool = False  # The write request on the bus
    _Response: bool = False  # The response on the bus
    _PowerOn: bool = False  # The running state of the machine

    def __init__(self):
        """
        Constructor for the ControlBus class.
        Initializes the read request, write request, and response on the bus to False.
        """
        self._ReadRequest = False
        self._WriteRequest = False
        self._Response = False
        self._busLock = Lock()

    def lock_bus(self):
        """
        This method locks the bus.
        """
        self._busLock.acquire()

    def unlock_bus(self):
        """
        This method unlocks the bus.
        """
        self._busLock.release()

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

    def peek_response(self) -> bool:
        """
        This method returns the response on the bus without setting the response to False.
        :return: The response on the bus.
        """
        return self._Response

    def set_response(self, value: bool):
        """
        This method sets the response on the bus.
        :param value: The response to set on the bus.
        """
        self._Response = value

    def is_power_on(self) -> bool:
        """ This method returns whether the bus is running or not. """
        return self._PowerOn

    def power_on(self):
        """ This method starts the bus running. """
        self._PowerOn = True

    def power_off(self):
        """ This method starts the bus running. """
        self._PowerOn = False
