#  Copyright (c) 2024. Kyle D. Ross.  All rights reserved.

import tkinter as tk

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

FONT_UBUNTU_MONO_REGULAR = "Ubuntu Mono Regular"


class AddressableTextDisplay(BaseDevice):
    """
    The AddressableTextDisplay class represents a text display that can be
    addressed by a computer system. It inherits from the BaseDevice class
    and provides methods to read and write to the display, as well as to
    cycle the display. The display contains its own buffer and its
    geometry is defined by the width and height at creation.
    """

    _width: int = 0  # The width of the display
    _height: int = 0  # The height of the display
    _formClosing: bool = False  # Flag to indicate if the form is closing

    def __init__(self, starting_address, width, height):
        """
        Constructor for the AddressableTextDisplay class.
        Initializes the starting address, width, and height of the display.
        It creates labels on the window that represent each character on the display.
        :param starting_address: The starting address of the display.
        :param width: The width of the display.
        :param height: The height of the display.
        """
        self._width = width
        self._height = height
        super().__init__(starting_address, self._width * self._height)
        self.display = [[' '] * self._width for _ in range(self._height)]
        self.window = tk.Tk()
        self.labels = \
            [[tk.Label(self.window, text=' ', font=(FONT_UBUNTU_MONO_REGULAR, 10), width=1) for _ in
              range(self._width)] for _ in
             range(self._height)]
        for i in range(self._height):
            for j in range(self._width):
                self.labels[i][j].grid(row=i, column=j)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        This method is called when the form is closing.
        It sets the _formClosing flag to True.
        This is used to halt the system when the form is closed by raising the halt interrupt.
        """
        self._formClosing = True

    def read(self, address):
        """
        This method reads a character from the display at a given address.
        :param address: The address to read from.
        :return: The character at the given address.
        """
        row = address // self._width
        col = address % self._width
        return self.display[row][col]

    def write(self, address, value):
        """
        This method writes a character to the display at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        row = address // self._width
        col = address % self._width
        self.display[row][col] = value
        self.labels[row][col]['text'] = value

    def cycle(self, address_bus, data_bus, control_bus, interrupt_bus):
        """
        This method represents a cycle of the display, which involves interaction with the buses.
        :param address_bus: The address bus to interact with.
        :param data_bus: The data bus to interact with.
        :param control_bus: The control bus to interact with.
        :param interrupt_bus: The interrupt bus to interact with.
        """
        if self._formClosing:
            interrupt_bus.set_interrupt(Interrupts.halt)
            return
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                data_bus.set_data(ord(self.read(address_bus.get_address() - self.starting_address)))
                control_bus.set_read_request(False)
                control_bus.set_response(True)
            if control_bus.get_write_request():
                data = data_bus.get_data()
                self.write(address_bus.get_address() - self.starting_address, chr(data))
                control_bus.set_write_request(False)
                control_bus.set_response(True)
        self.update_window()

    def update_window(self):
        """
        This method updates the window of the display.
        """
        self.window.update_idletasks()
        self.window.update()

    def run(self):
        """
        This method starts the main loop of the window.
        """
        self.window.mainloop()
