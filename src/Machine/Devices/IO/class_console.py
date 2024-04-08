#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

import threading
import tkinter as tk
# import pygame
from queue import Queue

from Constants.class_interrupts import Interrupts as Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice


class Console(BaseDevice):
    """
    A class used to represent a Console device.

    ...

    Attributes
    ----------
    keystroke_buffer : Queue
        a queue to store the keystrokes
    console_output_buffer : str
        a string to store the console output
    keypress_flag : bool
        a flag to indicate if a key has been pressed
    console_closed : bool
        a flag to indicate if the console is closed
    interrupt_number : int
        the interrupt number for the console
    console_window : tk.Tk
        the tkinter window for the console
    ...

    Methods
    -------
    cycle(address_bus, data_bus, control_bus, interrupt_bus):
        Executes a cycle of the console device.
    console_is_ready():
        Checks if the console is ready.
    update_textbox(text):
        Updates the text in the textbox.
    process_keypress():
        Processes the keypress event.
    start_form():
        Starts the form in a separate thread.
    run_form():
        Runs the form.
    """
    keystroke_buffer = Queue()
    console_output_buffer = ""
    keypress_flag: bool = False
    console_closed: bool = False
    interrupt_number: int = Interrupts.irq2
    console_window: tk.Tk = None

    def __init__(self, starting_address: int, interrupt: int):
        super().__init__(starting_address, 1)
        self.interrupt_number = interrupt
        self.keypress_event = threading.Event()
        self.keypress = None  # Shared variable to store the pressed key
        self.textbox = None  # Reference to the form's textbox
        # pygame.mixer.init()
        # pygame.mixer.music.load("src/Resources/stop-13692.mp3")
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
            interrupt_bus.set_interrupt(Interrupts.halt)

        if not self.console_is_ready():
            print("Console is not ready.")
            return

        self.process_keypress()
        if self.keypress_flag:
            self.keypress_flag = False
            interrupt_bus.set_interrupt(self.interrupt_number)
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                data_bus.set_data(ord(self.keystroke_buffer.get()))
                control_bus.set_read_request(False)
                control_bus.set_response(True)
            if control_bus.get_write_request():
                keypress = data_bus.get_data()
                if keypress == 12:
                    self.console_output_buffer = ""
                elif keypress == 8:
                    if len(self.console_output_buffer) > 0:
                        self.console_output_buffer = self.console_output_buffer[:-1]
                elif keypress == 7:
                    # do nothing
                    pass
                    # play Resources/stop-13692.mp3 using pygame
                    # pygame.mixer.music.play()
                else:
                    self.console_output_buffer += chr(keypress)
                control_bus.set_write_request(False)
                control_bus.set_response(True)
                self.update_textbox(self.console_output_buffer)

    @staticmethod
    def formatted_textbox_test(text):
        """
        Function to replace all carriage return and newline characters with newline characters.

        Parameters:
        text (str): The text to be formatted.

        Returns:
        str: The formatted text.
        """
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def console_is_ready(self):
        if self.console_window is None:
            return False
        if not self.console_window.winfo_exists():
            return False
        if self.textbox is None:
            return False
        if not self.textbox.winfo_exists():
            return False
        return True

    def update_textbox(self, text):
        # Set the text of the textbox
        self.textbox.config(state="normal")
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, self.formatted_textbox_test(text))
        self.textbox.config(state="disabled")
        self.textbox.see(tk.END)

    def process_keypress(self):
        # Check if the keypress event is set
        if self.keypress_event.is_set():
            # Process the keypress event
            self.keystroke_buffer.put(self.keypress)

            # Reset the keypress event and clear the shared variable
            self.keypress_event.clear()
            self.keypress = None
            self.keypress_flag = True

    def start_form(self):
        # Start the form in a separate thread
        form_thread = threading.Thread(target=self.run_form)
        form_thread.start()

    def run_form(self):
        # Create the form window
        form_window = tk.Tk()
        form_window.title(f"Rubbish Console [At {self.starting_address}, interrupt {self.interrupt_number}]")
        self.console_window = form_window
        self.textbox = tk.Text(form_window, state="disabled")
        self.textbox.pack()

        # Function to capture keypress events
        def capture_keypress(event):
            # Set the shared variable to the pressed key
            if len(event.char) == 1:
                self.keypress = event.char
                # Signal the main thread
                self.keypress_event.set()

        def on_close():
            self.console_closed = True

        # Bind the keypress event to the capture_keypress function
        form_window.bind("<KeyPress>", capture_keypress)
        form_window.protocol("WM_DELETE_WINDOW", on_close)

        # Start the form main loop
        form_window.mainloop()
