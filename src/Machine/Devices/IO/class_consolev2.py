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

import threading
import time
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice


class ConsoleV2(BaseDevice):
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
    console_output_buffer : str
        a string to store the console output
    keypress_event : threading.Event
        an event to indicate a keypress
    console_window : tk.Tk
        the tkinter window for the console
    textbox : tk.Text
        the tkinter text widget for the console
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

    def __init__(self, starting_address: int, interrupt_number: int):
        """
        Constructs all the necessary attributes for the console device.

        Parameters:
            starting_address (int): The starting address of the console device.
            interrupt_number (int): The interrupt number for the console device.
        """
        super().__init__(starting_address, 1)
        self.interrupt_number = interrupt_number
        self.keystroke_buffer = Queue()
        self.console_output_buffer = ""
        self.keypress = ""
        self.keypress_event = threading.Event()
        self.console_window = None
        self.textbox = None
        self.console_closed = False
        self.start_form()

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
                    if data == 8:  # backspace
                        if len(self.console_output_buffer) > 0:
                            self.set_console_output_buffer(self.console_output_buffer[:-1])
                    elif data == 12:  # form feed
                        self.set_console_output_buffer("")
                    elif data == 7:  # bell
                        # do nothing
                        pass
                    else:
                        if 0 <= data <= 255:
                            self.set_console_output_buffer(self.console_output_buffer + chr(data))
                            self.set_console_output_buffer(
                                self.console_output_buffer.replace("\r\n", "\n").replace("\r", ""))
                    control_bus.set_write_request(False)
                    control_bus.set_response(True)
                    self.update_textbox()

    def console_is_ready(self):
        """
        Checks if the console is ready.

        Returns:
            bool: True if the console is ready, False otherwise.
        """
        return self.console_window is not None and self.textbox is not None

    def set_console_output_buffer(self, output: str):
        """
        Sets the console output buffer.

        Parameters:
            output (str): The output to set in the console output buffer.
        """
        self.console_output_buffer = output
        self.update_textbox()

    def update_textbox(self):
        """
        Updates the text in the textbox.
        """
        self.textbox.config(state="normal")
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, self.console_output_buffer)
        self.textbox.mark_set("insert", tk.END)  # Set the cursor at the end of the text
        self.textbox.see(tk.END)
        self.textbox.config(state="disabled")

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

    def process_cursor(self):
        """
        Processes the cursor.
        Returns:
            None
        """

        flash_interval = 1 / self._cursor_blinks_per_second
        current_time = time.time()
        if current_time - self._cursor_last_display_time > flash_interval:
            if self._cursor_is_displayed:
                self.cursor_off()
            else:
                self.console_output_buffer += "_"
                self._cursor_is_displayed = True
            self.update_textbox()
            self._cursor_last_display_time = current_time

    def cursor_off(self):
        """
        This will remove the cursor character from the console output buffer.
        Returns: None
        """
        if self._cursor_is_displayed:
            self.console_output_buffer = self.console_output_buffer[:-1]
            self._cursor_is_displayed = False

    def run_form(self):
        """
        Runs the form.
        """
        self.console_window = tk.Tk()
        self.console_window.title("Console v2")
        self.textbox = tk.Text(self.console_window, state="disabled")
        self.textbox.pack()
        self.textbox.focus_set()

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
        self.console_window.mainloop()
