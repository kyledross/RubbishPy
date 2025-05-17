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
        self.__transactionInProgress = False
        self.__busLock = Lock()

    # What's the difference between locking the bus and starting a transaction?
    #
    # Locking the bus is more of a low-level emulator control. It ensures that only one device is accessing
    # a control-bus variable at a time. It's a race condition protection mechanism.
    #
    # A transaction is a higher-level control meant to indicate that a logical operation is in-progress and
    # that other logical operations must wait until this one is finished.  Where a bus lock prevents changing
    # bus values at a granular level, a transaction wraps a series of requests and responses into a transaction.
    # Any device wanting to make a request and have the request fulfilled without interference by other device
    # requests should wrap the entire operation in a transaction.
    #
    # Bus locks are still required within the transaction because it is still necessary to control variable access
    # between devices.  Only more higher-order devices (like a processor) would begin and end a transaction.  Other
    # devices (like memory or a console) wouldn't do such a thing.  Lower-order devices would typically just signal
    # an interrupt if they need to "make a request", and let a higher-order device (like a processor) respond to
    # the interrupt and make a request (in a transaction) to retrieve the data the device has to offer.
    #
    # Should transactions, then, be a function of the control bus?  Shouldn't it be part of the processors?  Yes,
    # probably.  As of the time of this writing, the processors are completely independent devices in the machine
    # and have no knowledge of each other.  The control bus is common between the two, so for the time being,
    # the control bus is where this transaction is tracked.  Perhaps a future enhancement would isolate
    # processors behind a common interface to the buses.  That interface would become the "processor" and the
    # current-day processors would be "cores" behind that processor.  The transaction control would then be moved
    # away from the control bus and into the new "processor".

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

    def begin_transaction(self) -> None:
        """
        This method begins a transaction on the bus.
        """
        while self.__transactionInProgress:
            time.sleep(0)
        self.__transactionInProgress = True

    def end_transaction(self) -> None:
        """
        This method ends a transaction on the bus.
        """
        self.__transactionInProgress = False

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
