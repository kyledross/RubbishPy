#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.


import threading
import time
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

FONT_UBUNTU_MONO_REGULAR = "Ubuntu Mono Regular"


def show_execution_time(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} started")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time} seconds")
        return result

    return wrapper


class ConsoleV31(BaseDevice):
    """
    A class used to represent a Console device version 2.
    This console is compatible with the original console.

    ...

    Attributes
    ----------
    interrupt_number : int
        the interrupt number for the console
    keystroke_buffer : Queue
        a queue to store the keystrokes
    console_buffer : str
        a string to store the console output
    keypress_event : threading.Event
        an event to indicate a keypress
    console_window : tk.Tk
        the tkinter window for the console
    console_closed : bool
        a flag to indicate if the console is closed
    ...

    Methods
    -------
    cycle(address_bus, data_bus, control_bus, interrupt_bus):
        Executes a cycle of the console device.
    console_is_ready():
        Checks if the console is ready.
    update_textbox():
        Updates the text in the textbox.
    process_keypress(interrupt_bus):
        Processes the keypress event.
    start_form():
        Starts the form in a separate thread.
    run_form():
        Runs the form.
    """

    # synthetic cursor control
    _cursor_is_displayed: bool = False
    _cursor_last_display_time: float = 0
    _cursor_blinks_per_second: int = 2
    # cursor management
    _cursorX: int = 0
    _cursorY: int = 0

    def __init__(self, starting_address, width, height, interrupt_number: int):
        """
        Constructs all the necessary attributes for the console device.

        Parameters:
            starting_address (int): The starting address of the console device.
            interrupt_number (int): The interrupt number for the console device.
        """
        super().__init__(starting_address, 1)
        self.labels = None
        self.form_ready = False
        self.console_is_busy = False
        self._width = width
        self._height = height
        self.console_buffer = [[' '] * self._width for _ in range(self._height)]
        self.interrupt_number = interrupt_number
        self.keystroke_buffer = Queue()
        self.keypress = ""
        self.keypress_event = threading.Event()
        self.console_window = None
        self.console_closed = False
        self.start_form()

    def write(self, address, value: str):
        """
        This method writes a character to the display at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        row = address // self._width
        col = address % self._width
        self.console_buffer[row][col] = value
        self.labels[row][col]['text'] = value

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

    def cycle(self, address_bus, data_bus, control_bus, interrupt_bus):
        """
        Executes a cycle of the console device.

        Parameters:
            address_bus (Bus): The address bus.
            data_bus (Bus): The data bus.
            control_bus (Bus): The control bus.
            interrupt_bus (Bus): The interrupt bus.
        """
        if self.console_closed:
            self.console_window.quit()
            interrupt_bus.set_interrupt(Interrupts.halt)
            return

        if self.console_is_ready():
            self.console_is_busy = True
            self.process_cursor()
            self.process_keypress(interrupt_bus)
            if self.address_is_valid(address_bus):
                if control_bus.get_read_request():
                    if not self.keystroke_buffer.empty():
                        buffer_data = self.keystroke_buffer.get()
                        if len(buffer_data) > 0:
                            data_bus.set_data(ord(buffer_data))
                        control_bus.set_read_request(False)
                        control_bus.set_response(True)
                if control_bus.get_write_request():
                    self.cursor_off()
                    data = data_bus.get_data()
                    self.process_data(data)
                    control_bus.set_write_request(False)
                    control_bus.set_response(True)
            self.console_is_busy = False

    def scroll_labels_up(self):
        for i in range(self._height - 1):
            for j in range(self._width):
                self.console_buffer[i][j] = self.console_buffer[i + 1][j]
                self.labels[i][j]['text'] = self.labels[i + 1][j]['text']
        for j in range(self._width):
            self.console_buffer[self._height - 1][j] = ' '
            self.labels[self._height - 1][j]['text'] = ' '

    def console_is_ready(self):
        """
        Checks if the console is ready.

        Returns:
            bool: True if the console is ready, False otherwise.
        """
        return not self.console_is_busy and self.console_window is not None and self.form_ready

    def process_keypress(self, interrupt_bus):
        """
        Processes the keypress event.

        Parameters:
            interrupt_bus (Bus): The interrupt bus.
        """
        if self.keypress_event.is_set():
            print("Keypress detected")
            self.keystroke_buffer.put(self.keypress)
            self.keypress_event.clear()
            print(f"Keypress: {self.keypress} cleared.")
            interrupt_bus.set_interrupt(self.interrupt_number)

    @show_execution_time
    def start_form(self):
        """
        Starts the form in a separate thread.
        """

        form_thread = threading.Thread(target=self.run_form)
        form_thread.start()

    def process_cursor(self):
        """
        Processes the cursor.
        Returns:
            None
        """
        # todo: replace with more elegant solution
        return

        flash_interval = 1 / self._cursor_blinks_per_second
        current_time = time.time()
        if current_time - self._cursor_last_display_time > flash_interval:
            if self._cursor_is_displayed:
                self.cursor_off()
            else:
                self.console_buffer += "_"
                self._cursor_is_displayed = True
            self._cursor_last_display_time = current_time

    def cursor_off(self):
        """
        This will remove the cursor character from the console output buffer.
        Returns: None
        """
        # todo: replace with more elegant solution
        return

        if self._cursor_is_displayed:
            self.console_buffer = self.console_buffer[:-1]
            self._cursor_is_displayed = False

    @show_execution_time
    def run_form(self):
        """
        Runs the form.
        """
        self.console_window = tk.Tk()
        self.console_window.title("Console v3.1")
        self.labels = \
            [[tk.Label(self.console_window, text=' ', font=(FONT_UBUNTU_MONO_REGULAR, 10), width=1) for _ in
              range(self._width)] for _ in
             range(self._height)]
        for i in range(self._height):
            for j in range(self._width):
                self.labels[i][j].grid(row=i, column=j)

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

        def on_close():
            """
            Closes the console window.
            Returns:
                None

            """
            self.console_closed = True

        self.console_window.bind("<KeyPress>", capture_keypress)
        self.console_window.protocol("WM_DELETE_WINDOW", on_close)
        self.form_ready = True
        self.console_window.mainloop()
