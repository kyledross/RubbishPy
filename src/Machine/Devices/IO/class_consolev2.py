#  Copyright (c) 2024 Kyle D. Ross.
#  Refer to LICENSE.txt for license information.

import threading
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice


# todo When Hello World program is running, if the user presses the CTRL key, the program displays some garbage.
#  That shouldn't happen.
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
                    data = data_bus.get_data()
                    if data == 8:  # backspace
                        if len(self.console_output_buffer) > 0:
                            self.console_output_buffer = self.console_output_buffer[:-1]
                    elif data == 12:  # form feed
                        self.console_output_buffer = ""
                    elif data == 7:  # bell
                        # do nothing
                        pass
                    else:
                        if 0 <= data <= 255:
                            self.console_output_buffer += chr(data)
                            self.console_output_buffer = self.console_output_buffer.replace("\r\n", "\n").replace("\r",
                                                                                                                  "")
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

    def update_textbox(self):
        """
        Updates the text in the textbox.
        """
        self.textbox.config(state="normal")
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, self.console_output_buffer)
        self.textbox.mark_set("insert", tk.END)  # Set the cursor at the end of the text
        self.textbox.see(tk.END)

        # todo: although it scrolls to end, it still briefly scrolls to top,
        # creating a flicker

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
        self.console_window.title("Console v2")
        self.textbox = tk.Text(self.console_window, state="disabled")
        self.textbox.pack()
        self.textbox.focus_set()

        def capture_keypress(event):
            # todo: figure out how to handle control keypress
            self.keypress = event.char
            self.keypress_event.set()
            return "break"

        def on_close():
            self.console_closed = True

        self.console_window.bind("<KeyPress>", capture_keypress)
        self.console_window.protocol("WM_DELETE_WINDOW", on_close)
        self.console_window.mainloop()
