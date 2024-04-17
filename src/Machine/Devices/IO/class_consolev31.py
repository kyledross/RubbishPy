#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.
import sys
import threading
import time
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

REFRESH_RATE_MS = 10  # milliseconds between screen refreshes
DEFAULT_LABEL_CONTENTS = ' '  # set to X if debugging so the labels may be seen
FONT_UBUNTU_MONO_REGULAR = "Ubuntu Mono Regular"


def log_message(message):
    if sys.gettrace():
        print(message)

def show_execution_time(func):
    def wrapper(*args, **kwargs):
        log_message(f"{func.__name__} started")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        log_message(f"{func.__name__} executed in {end_time - start_time} seconds")
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
    input_queue : Queue
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
        self._width = width
        self._height = height
        self.console_buffer = [[' '] * self._width for _ in range(self._height)]
        self.interrupt_number = interrupt_number
        self.input_queue = Queue()
        self.output_queue = Queue()
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

        self.process_cursor()
        self.process_keypress(interrupt_bus)
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                if not self.input_queue.empty():
                    buffer_data = self.input_queue.get()
                    if len(buffer_data) > 0:
                        data_bus.set_data(ord(buffer_data))
                    control_bus.set_read_request(False)
                    control_bus.set_response(True)
            if control_bus.get_write_request():
                self.cursor_off()
                data = data_bus.get_data()
                self.output_queue.put(data)
                control_bus.set_write_request(False)
                control_bus.set_response(True)

    def scroll_up(self):
        for i in range(self._height - 1):
            for j in range(self._width):
                self.console_buffer[i][j] = self.console_buffer[i + 1][j]
        for j in range(self._width):
            self.console_buffer[self._height - 1][j] = ' '

    def console_is_ready(self):
        """
        Checks if the console is ready.

        Returns:
            bool: True if the console is ready, False otherwise.
        """
        return self.console_window is not None and self.form_ready

    def process_keypress(self, interrupt_bus):
        """
        Processes the keypress event.

        Parameters:
            interrupt_bus (Bus): The interrupt bus.
        """
        if self.keypress_event.is_set():
            log_message("Keypress detected")
            self.input_queue.put(self.keypress)
            self.keypress_event.clear()
            log_message(f"Keypress: {self.keypress} cleared.")
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
        self.create_labels()

        def process_data(data):
            # todo: this should be called on the window thread on a timer
            # pop the data off the output queue and call this with it
            """
            This method will take the data, and based off of the cursorX and cursorY position,
            will compute the offset address to be passed to the write method.
            It will then increment the cursorX value by one.
            If cursorX is >= the width, it will set cursorX to 0 and increment the cursorY by one.
            If cursorY is >= the height, it will scroll the labels up by one, setting the new line all blank.
            If the data is 13, it will set cursorX to 0 and increment the cursorY by one.
            If the data is 8, it will decrement cursorX by one. If cursorX is < 0, it will decrement the cursorY by one
            and set cursorX to the width-1.
            Args:
                data:

            Returns:

            """
            if data == 13:
                self._cursorX = 0
            elif data == 10:  # LF
                self._cursorY += 1
                if self._cursorY >= self._height:
                    self.scroll_up()
                    self._cursorY -= 1
            elif data == 8:
                self._cursorX -= 1
                if self._cursorX < 0:
                    self._cursorY -= 1
                    self._cursorX = self._width - 1  # todo: seek to the end of the current line
                self.write(self._cursorY * self._width + self._cursorX, chr(32))
            else:
                self.write(self._cursorY * self._width + self._cursorX, chr(data))
                self._cursorX += 1
                if self._cursorX >= self._width:
                    self._cursorX = 0
                    self._cursorY += 1
                if self._cursorY >= self._height:
                    self.scroll_up()
                    self._cursorY -= 1

        def capture_keypress(event):
            """
            Captures the keypress event.
            Args:
                event: The keypress event.

            Returns: "break"

            """
            if event.char != "":
                self.keypress = event.char
                self.keypress_event.set()
            return "break"

        def on_close():
            """
            Closes the console window.
            Returns:
                None

            """
            # todo: change cursor to wait while form is being closed
            self.console_closed = True

        @show_execution_time
        def process_output_queue():
            """
            Processes the output queue.
            Returns:
                None

            """
            log_message(f"Output queue empty? {self.output_queue.empty()}")
            data_changed = False
            while not self.output_queue.empty():
                data_changed = True
                log_message(f"Queue size: {self.output_queue.qsize()}")
                data = self.output_queue.get(block=True)
                process_data(data)
                # Schedule the function to be called again after 100ms
            if data_changed:
                for i in range(self._height):
                    for j in range(self._width):
                        self.labels[i][j]['text'] = self.console_buffer[i][j]
            self.console_window.after(REFRESH_RATE_MS, process_output_queue)

        self.console_window.bind("<KeyPress>", capture_keypress)
        self.console_window.protocol("WM_DELETE_WINDOW", on_close)
        self.form_ready = True
        process_output_queue()
        self.console_window.mainloop()

    def create_labels(self):
        # todo: labels are growing in height when a character is assigned to them
        # todo: there is a lot of space between each row of labels
        self.labels = []
        for _ in range(self._height):
            self.labels.append([tk.Label(self.console_window, text=DEFAULT_LABEL_CONTENTS,
                                         font=(FONT_UBUNTU_MONO_REGULAR, 10), width=1, padx=0, pady=0) for _
                                in range(self._width)])
        for i in range(self._height):
            for j in range(self._width):
                self.labels[i][j].grid(row=i, column=j, pady=0, padx=0)  # Set pady and padx to 0 in grid method
