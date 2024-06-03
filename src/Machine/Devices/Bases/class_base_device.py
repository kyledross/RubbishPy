import abc
import random
import sys

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_control_bus import ControlBus


def base36encode(number) -> str:
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
        device_id = cls.__name__ + "_" + base36encode(random.randint(0, 36 ** 2))
        return device_id

    def get_device_id(self) -> str:
        """
        This method returns the device ID.
        :return: The device ID.
        """
        return self.__deviceId

    def set_finished(self):
        self.__finished = True

    def is_finished(self) -> bool:
        return self.__finished

    @abc.abstractmethod
    def start(self):
        """
        This method starts the device.
        """
        pass

    def is_running(self) -> bool:
        """
        This method returns whether the device is running or not.
        :return: True if the device is running, False otherwise.
        """
        return self.__running

    def address_bus(self) -> AddressBus:
        return self.__addressBus

    def data_bus(self) -> DataBus:
        return self.__dataBus

    def control_bus(self) -> ControlBus:
        return self.__controlBus

    def interrupt_bus(self) -> InterruptBus:
        return self.__interruptBus

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
        This property returns the size of the device.
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

    def stop_running_if_halt_detected(self):
        # if halt interrupt has been raised, stop the thread
        if self.interrupt_bus().test_interrupt(Interrupts.halt):
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
