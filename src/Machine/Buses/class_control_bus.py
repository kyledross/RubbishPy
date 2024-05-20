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

    def read_response(self) -> bool:
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
