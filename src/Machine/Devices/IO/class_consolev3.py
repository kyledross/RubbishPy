#  Copyright (c) 2024 Kyle D. Ross.
#  Refer to LICENSE.txt for license information.

from Machine.Devices.Bases.class_base_device import BaseDevice
from Machine.Devices.IO.class_addressable_text_display import FONT_UBUNTU_MONO_REGULAR
import tkinter as tk


class ConsoleV3(BaseDevice):
    """
    ConsoleV3 is a class that represents a console device.
    It consists of a window with multiple labels that represent the console output in an 80x25 grid.
    It contains an array of integers that represent the ASCII values of the characters on the console (an 80x25 grid).
    It inherits from the BaseDevice class and provides methods to read and write to the console, as well as to cycle the console.
    Functionally, it is similar to the ConsoleV2 class, but it uses a different approach to create the console window.
    """

    _formClosing: bool = False  # Flag to indicate if the form is closing
    _cursor_location: tuple = (0, 0)  # The current cursor location
    _interrupt_number: int = 0  # The interrupt number for the console

    def __init__(self, starting_address: int, interrupt_number: int):
        """
        Constructor for the ConsoleV3 class.
        Initializes the starting address of the console.
        It creates labels on the window that represent each character on the console.
        :param starting_address: The starting address of the console.
        """
        super().__init__(starting_address, 1)
        self._interrupt_number = interrupt_number
        self.display_buffer = [[32] * 80 for _ in range(25)]  # Initialize the display with spaces
        self.window = tk.Tk()
        self.labels = \
            [[tk.Label(self.window, text=' ', font=(FONT_UBUNTU_MONO_REGULAR, 10), width=1) for _ in range(80)] for _ in
             range(25)]
        for i in range(25):
            for j in range(80):
                self.labels[i][j].grid(row=i, column=j)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        This method is called when the form is closing.
        It sets the _formClosing flag to True.
        This is used to halt the system when the form is closed by raising the halt interrupt.
        """
        self._formClosing = True

    def cycle(self, address_bus, data_bus, control_bus, interrupt_bus) -> None:
        """
        This method cycles the console device.
        """
        if self.address_is_valid(address_bus):
            if control_bus.get_write_request():
                self.process_write(data_bus.get_data())
                control_bus.set_write_request(False)
                control_bus.set_response(True)

    def refresh_display(self) -> None:
        """
        This method refreshes the display by updating the text in the labels.
        """
        for i in range(25):
            for j in range(80):
                self.labels[i][j].config(text=chr(self.display_buffer[i][j]))

    def process_write(self, value: int) -> None:
        """
        This method will write the byte to the display buffer at the current cursor location.
        It will also increment the cursor location.
        If the cursor reaches the end of the line, it will wrap to the next line.
        If the cursor reaches the end of the display, it will scroll the display up by one line.
        Returns:

        """
        row, col = self._cursor_location
        self.display_buffer[row][col] = value
        self._cursor_location = (row, (col + 1) % 80)
        if col == 79:
            if row == 24:
                # Scroll the buffer up, losing the top row and creating a blank bottom row
                self.display_buffer = self.display_buffer[1:] + [[32] * 80]
                self._cursor_location = (24, 0)
            else:
                self._cursor_location = (row + 1, 0)

        self.refresh_display()
