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

class AddressBus:
    """
    The AddressBus class represents the address bus of a computer system.
    It provides methods to get and set the address on the bus.
    """

    _AddressBus: int = 0  # The address on the bus

    def __init__(self):
        """
        Constructor for the AddressBus class.
        Initializes the address on the bus to 0.
        """
        self._AddressBus = 0

    def get_address(self) -> int:
        """
        This method returns the address on the bus.
        :return: The address on the bus.
        """
        return self._AddressBus

    def set_address(self, value: int):
        """
        This method sets the address on the bus.
        :param value: The address to set on the bus.
        """
        self._AddressBus = value
