#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.
import threading
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

FONT_UBUNTU_MONO_REGULAR = "Ubuntu Mono Regular"


class ConsoleV3(BaseDevice):
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
    _interrupt_number: int = 0
    _formReady: bool = False  # Flag to indicate if the form is ready

    # cursor management
    _cursorX: int = 0
    _cursorY: int = 0

    def __init__(self, starting_address, width, height, interrupt_number: int):
        """
        Constructor for the AddressableTextDisplay class.
        Initializes the starting address, width, and height of the display.
        It creates labels on the window that represent each character on the display.
        :param starting_address: The starting address of the display.
        :param width: The width of the display.
        :param height: The height of the display.
        """
        self.interrupt_number = 0
        self.keypress = ""
        self.keystroke_buffer = Queue()
        self.keypress_event = threading.Event()
        self.labels = None
        self.console_window = None
        self._interrupt_number = interrupt_number
        self._width = width
        self._height = height
        super().__init__(starting_address, 1)
        self.display = [[' '] * self._width for _ in range(self._height)]
        self.start_form()

    def process_keypress(self, interrupt_bus):
        """
        Processes the keypress event.

        Parameters:
            interrupt_bus (Bus): The interrupt bus.
        """
        if self.keypress_event.is_set():
            self.keystroke_buffer.put(self.keypress)
            self.keypress_event.clear()
            interrupt_bus.set_interrupt(self.interrupt_number)

    def start_form(self):
        """
        Starts the form in a separate thread.
        """
        form_thread = threading.Thread(target=self.run_form)
        form_thread.start()

    def run_form(self):
        """
        Runs the form.
        """
        self.console_window = tk.Tk()
        self.console_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.labels = \
            [[tk.Label(self.console_window, text=' ', font=(FONT_UBUNTU_MONO_REGULAR, 10), width=1) for _ in
              range(self._width)] for _ in
             range(self._height)]
        for i in range(self._height):
            for j in range(self._width):
                self.labels[i][j].grid(row=i, column=j)
        self.console_window.title("Console v3")
        self._formReady = True

        def on_close():
            """
            Closes the console window.
            Returns:
                None

            """
            self.console_closed = True

        def capture_keypress(event):
            """
            Captures the keypress event.
            Args:
                event: The keypress event.

            Returns: "break"

            """
            # todo: figure out how to handle control keypress
            self.keypress = event.char
            self.keypress_event.set()
            return "break"

        self.console_window.bind("<KeyPress>", capture_keypress)
        self.console_window.protocol("WM_DELETE_WINDOW", on_close)
        self.console_window.mainloop()

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
        return self.display[address // self._width][address % self._width]

    def process_data(self, data):
        """
        This method will take the data, and based off of the cursorX and cursorY position,
        will compute the offset address to be passed to the write method.
        It will then increment the cursorX value by one.
        If cursorX is >= the width, it will set cursorX to 0 and increment the cursorY by one.
        If cursorY is >= the height, it will scroll the labels up by one, setting the new line all blank.
        If the data is 13, it will set cursorX to 0 and increment the cursorY by one.
        If the data is 8, it will decrement cursorX by one. If cursorX is < 0, it will decrement the cursorY by one and
        set cursorX to the width-1.
        Args:
            data:

        Returns:

        """
        if data == 13:
            self._cursorX = 0
            self._cursorY += 1
            if self._cursorY >= self._height:
                self.scroll_labels_up()
                self._cursorY -= 1
        elif data == 8:
            self._cursorX -= 1
            if self._cursorX < 0:
                self._cursorY -= 1
                self._cursorX = self._width - 1
            self.write(self._cursorY * self._width + self._cursorX, chr(32))
        else:
            self.write(self._cursorY * self._width + self._cursorX, chr(data))
            self._cursorX += 1
            if self._cursorX >= self._width:
                self._cursorX = 0
                self._cursorY += 1
            if self._cursorY >= self._height:
                self.scroll_labels_up()
                self._cursorY -= 1

    def write(self, address, value: str):
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
        if not self._formReady:
            return
        if self._formClosing:
            interrupt_bus.set_interrupt(Interrupts.halt)
            return
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                if not self.keystroke_buffer.empty():
                    buffer_data = self.keystroke_buffer.get()
                    if len(buffer_data) > 0:
                        data_bus.set_data(ord(buffer_data))
                    control_bus.set_read_request(False)
                    control_bus.set_response(True)
            if control_bus.get_write_request():
                data = data_bus.get_data()
                self.process_data(data)
                control_bus.set_write_request(False)
                control_bus.set_response(True)

    def scroll_labels_up(self):
        for i in range(self._height - 1):
            for j in range(self._width):
                self.display[i][j] = self.display[i + 1][j]
                self.labels[i][j]['text'] = self.labels[i + 1][j]['text']
        for j in range(self._width):
            self.display[self._height - 1][j] = ' '
            self.labels[self._height - 1][j]['text'] = ' '
