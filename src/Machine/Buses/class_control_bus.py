import time
from threading import Lock


class ControlBus:
    """
    The ControlBus class represents the control bus of a computer system.
    It provides methods to get and set the read request, write request, and response on the bus.
    """

    def __init__(self) -> None:
        """
        Constructor for the ControlBus class.
        Initializes the read request, write request, and response on the bus to False.
        """
        self.__PowerOn = None
        self.__ReadRequest = False
        self.__WriteRequest = False
        self.__Response = False
        self.__busLock = Lock()

    def lock_bus(self) -> None:
        """
        This method locks the bus. This is used to prevent multiple devices from accessing the bus at the same time.
        """
        self.__busLock.acquire()

    def unlock_bus(self) -> None:
        """
        This method unlocks the bus.
        """
        self.__busLock.release()
        time.sleep(0)

    @property
    def read_request(self) -> bool:
        """
        This method returns the read request on the bus.
        :return: The read request on the bus.
        """
        return self.__ReadRequest

    @read_request.setter
    def read_request(self, value: bool):
        """
        This method sets the read request on the bus.
        :param value: The read request to set on the bus.
        """
        self.__ReadRequest = value

    @property
    def write_request(self) -> bool:
        """
        This method returns the write request on the bus.
        :return: The write request on the bus.
        """
        return self.__WriteRequest

    @write_request.setter
    def write_request(self, value: bool):
        """
        This method sets the write request on the bus.
        :param value: The write request to set on the bus.
        """
        self.__WriteRequest = value

    @property
    def response(self) -> bool:
        """
        This method returns the response on the bus.
        :return: The response on the bus.
        """
        return self.__Response

    @response.setter
    def response(self, value: bool):
        """
        This method sets the response on the bus.
        :param value: The response to set on the bus.
        """
        self.__Response = value

    @property
    def power_on(self) -> bool:
        """
        This method returns the power on status of the bus.
        :return: The power on status of the bus.
        """
        return self.__PowerOn

    @power_on.setter
    def power_on(self, value: bool):
        """
        This method sets the power on status of the bus.
        :param value: The power on status to set on the bus.
        """
        self.__PowerOn = value
