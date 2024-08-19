import abc
import random
import sys

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_control_bus import ControlBus


def _base36encode(number) -> str:
    """
    Converts an integer to a base36 string.
    """
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    # noinspection SpellCheckingInspection
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]


class BaseDevice(abc.ABC):
    """
    The BaseDevice class is an abstract base class for all devices in the system.
    It provides a common interface for all devices, including a method to
    cycle the device and check if an address is valid.
    """

    def __init__(self, starting_address: int, size: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):
        """
        Constructor for the BaseDevice class.
        Initializes the starting address and size of the device.
        :param starting_address: The starting address of the device.
        :param size: The size of the device.
        """
        self.__startingAddress: int = starting_address
        self.__size: int = size
        self.__addressBus: AddressBus = address_bus
        self.__dataBus: DataBus = data_bus
        self.__controlBus: ControlBus = control_bus
        self.__interruptBus: InterruptBus = interrupt_bus
        self.__running: bool = True
        self.__finished: bool = False
        self.__deviceId: str = self.generate_device_id()

    @classmethod
    def generate_device_id(cls) -> str:
        """
        This method generates a unique device ID.
        :return: A unique device ID.
        """
        device_id = cls.__name__ + "_" + _base36encode(random.randint(0, 36 ** 2))
        return device_id

    @property
    def device_id(self) -> str:
        """
        This property returns the device ID.
        :return: The device ID.
        """
        return self.__deviceId

    @property
    def finished(self) -> bool:
        """
        This property returns whether the device has finished or not.
        :return: True if the device has finished, False otherwise.
        """
        return self.__finished

    @finished.setter
    def finished(self, value: bool):
        """
        This property sets whether the device has finished or not.
        :param value: True if the device has finished, False otherwise.
        """
        self.__finished = value

    @abc.abstractmethod
    def start(self) -> None:
        """
        This method starts the device.
        """
        pass

    @property
    def running(self) -> bool:
        """
        This property returns whether the device is running or not.
        :return: True if the device is running, False otherwise.
        """
        return self.__running

    @running.setter
    def running(self, value: bool):
        """
        This property sets whether the device is running or not.
        :param value: True if the device is running, False otherwise.
        """
        self.__running = value

    @property
    def address_bus(self) -> AddressBus:
        """
        This property returns the address bus that the device is connected to.
        Returns:
        The address bus that the device is connected to.
        """
        return self.__addressBus

    @address_bus.setter
    def address_bus(self, value: AddressBus):
        """
        This property sets the address bus that the device is connected to.
        Args:
            value: The address bus that the device is connected to.

        """
        self.__addressBus = value

    @property
    def data_bus(self) -> DataBus:
        """
        This property returns the data bus that the device is connected to.
        Returns:
        The data bus that the device is connected to.

        """
        return self.__dataBus

    @data_bus.setter
    def data_bus(self, value: DataBus):
        """
        This property sets the data bus that the device is connected to.
        Args:
            value: The data bus that the device is connected to.

        Returns:

        """
        self.__dataBus = value

    @property
    def control_bus(self) -> ControlBus:
        """
        This property returns the control bus that the device is connected to.
        Returns:
        The control bus that the device is connected to.

        """
        return self.__controlBus

    @control_bus.setter
    def control_bus(self, value: ControlBus):
        """
        This property sets the control bus that the device is connected to.
        Args:
            value: The control bus that the device is connected to.

        Returns:

        """
        self.__controlBus = value

    @property
    def interrupt_bus(self) -> InterruptBus:
        """
        This property returns the interrupt bus that the device is connected to.
        Returns:
        The interrupt bus that the device is connected to.

        """
        return self.__interruptBus

    @interrupt_bus.setter
    def interrupt_bus(self, value: InterruptBus):
        """
        This property sets the interrupt bus that the device is connected to.
        Args:
            value: The interrupt bus that the device is connected to.

        """
        self.__interruptBus = value

    @property
    def starting_address(self) -> int:
        """
        This property returns the starting address of the device.
        :return: The starting address of the device.
        """
        return self.__startingAddress

    @property
    def size(self) -> int:
        """
        This property returns the size of the device in the memory space.
        :return: The size of the device.
        """
        return self.__size

    def address_is_valid(self, address_bus: AddressBus) -> bool:
        """
        This method checks if an address on the address bus is valid for this device.
        An address is valid if it is within the range of the starting address and the size of the device.
        :param address_bus: The address bus to check the address from.
        :return: True if the address is valid, False otherwise.
        """
        if ((address_bus.address >= self.__startingAddress)
                and (address_bus.address < self.__startingAddress + self.__size)):
            return True
        else:
            return False

    def stop_running_if_halt_detected(self) -> None:
        """
        This method checks if a HALT interrupt has been raised on the interrupt bus.
        If so, it stops the device from running.
        """
        if self.interrupt_bus.test_interrupt(Interrupts.halt):
            self.__running = False

def log_message(message: str):
    """
    A function to log a message if a debugger is attached.
    Args:
        message:

    Returns:

    """
    if sys.gettrace() or 'pydevd' in sys.modules:
        print(message)
