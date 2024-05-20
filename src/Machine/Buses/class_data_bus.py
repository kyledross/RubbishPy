#  MIT License
#
#  Copyright (c) 2024 Kyle D. Ross
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from Machine.Buses.class_control_bus import ControlBus


class DataBus:
    """
    The DataBus class represents the data bus of a computer system.
    It provides methods to get and set the data on the bus.
    It also maintains a reference to a ControlBus instance.
    """

    _DataBus: int = 0  # The data on the bus
    _ControlBus: ControlBus = None  # The control bus associated with this data bus

    def __init__(self, control_bus: ControlBus):
        """
        Constructor for the DataBus class.
        Initializes the data on the bus to 0 and sets the control bus.
        :param control_bus: The control bus to associate with this data bus.
        """
        self._DataBus = 0
        self._ControlBus = control_bus

    def get_data(self) -> int:
        """
        This method returns the data on the bus.
        :return: The data on the bus.
        """
        return self._DataBus

    def set_data(self, value: int):
        """
        This method sets the data on the bus.
        :param value: The data to set on the bus.
        """
        self._DataBus = value
