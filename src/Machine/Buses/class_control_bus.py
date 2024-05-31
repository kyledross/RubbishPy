import time
from threading import Lock


class ControlBus:
    """
    The ControlBus class represents the control bus of a computer system.
    It provides methods to get and set the read request, write request, and response on the bus.
    """

    def __init__(self):
        """
        Constructor for the ControlBus class.
        Initializes the read request, write request, and response on the bus to False.
        """
        self.__PowerOn = None
        self.__ReadRequest = False
        self.__WriteRequest = False
        self.__Response = False
        self.__busLock = Lock()

    def lock_bus(self):
        """
        This method locks the bus.
        """
        self.__busLock.acquire()

    def unlock_bus(self):
        """
        This method unlocks the bus.
        """
        self.__busLock.release()
        time.sleep(0)

    def get_read_request(self) -> bool:
        """
        This method returns the read request on the bus.
        :return: The read request on the bus.
        """
        return self.__ReadRequest

    def set_read_request(self, value: bool):
        """
        This method sets the read request on the bus.
        :param value: The read request to set on the bus.
        """
        self.__ReadRequest = value

    def get_write_request(self) -> bool:
        """
        This method returns the write request on the bus.
        :return: The write request on the bus.
        """
        return self.__WriteRequest

    def set_write_request(self, value: bool):
        """
        This method sets the write request on the bus.
        :param value: The write request to set on the bus.
        """
        self.__WriteRequest = value

    def get_response(self) -> bool:
        """
        This method returns the response on the bus and then sets the response to False.
        :return: The response on the bus.
        """
        if self.__Response:
            self.__Response = False
            return True
        else:
            return False

    def peek_response(self) -> bool:
        """
        This method returns the response on the bus without setting the response to False.
        :return: The response on the bus.
        """
        return self.__Response

    def set_response(self, value: bool):
        """
        This method sets the response on the bus.
        :param value: The response to set on the bus.
        """
        self.__Response = value

    def is_power_on(self) -> bool:
        """ This method returns whether the bus is running or not. """
        return self.__PowerOn

    def power_on(self):
        """ This method starts the bus running. """
        self.__PowerOn = True

    def power_off(self):
        """ This method starts the bus running. """
        self.__PowerOn = False
