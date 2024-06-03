from Machine.Buses.class_control_bus import ControlBus


class DataBus:
    """
    The DataBus class represents the data bus of a computer system.
    It provides methods to get and set the data on the bus.
    It also maintains a reference to a ControlBus instance.
    """

    def __init__(self, control_bus: ControlBus):
        """
        Constructor for the DataBus class.
        Initializes the data on the bus to 0 and sets the control bus.
        :param control_bus: The control bus to associate with this data bus.
        """
        self.__DataBus = 0
        self.__ControlBus = control_bus

    @property
    def data(self) -> int:
        """
        This method returns the data on the bus.
        :return: The data on the bus.
        """
        return self.__DataBus

    @data.setter
    def data(self, value: int):
        """
        This method sets the data on the bus.
        :param value: The data to set on the bus.
        """
        self.__DataBus = value

