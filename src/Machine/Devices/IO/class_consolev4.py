#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

"""
The Console v4 device class.
"""
import os
import sys
import threading
import time
import tkinter as tk
from queue import Queue

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

OUTPUT_QUEUE_PROCESSING_RATE = 10  # milliseconds between processing the output queue
DEFAULT_LABEL_CONTENTS = ' '  # set to X if debugging so the labels may be seen
CONSOLE_FONT = "Ubuntu Sans Mono"
CHARACTER_WIDTH = 8  # todo: get this programmatically from the font
CHARACTER_HEIGHT = 8  # todo: get this programmatically from the font
VERTICAL_PIXEL_SEPARATION = 20
HORIZONTAL_PIXEL_SEPARATION = 4
CURSOR_CHANGES_PER_SECOND: int = 3  # the number of times the cursor changes per second
BACK_COLOR = Black = "#000000"
TEXT_COLOR = White = "#FFFFFF"


def log_message(message):
    """
    A function to log a message if a debugger is attached.
    Args:
        message:

    Returns:

    """
    if os.getenv('IS_DEBUGGING') == '1':
        print(message)


def show_execution_time(func):
    """
    A decorator to show the execution time of a function.
    Args:
        func:

    Returns:

    """

    def wrapper(*args, **kwargs):
        log_message(f"{func.__name__} started")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        log_message(f"{func.__name__} executed in {end_time - start_time} seconds")
        return result

    return wrapper


class ScreenElement:
    """
    A class that represents a character on the screen.
    It contains the character and any attributes associated with it, such as color.
    """

    __character: str = None
    __color: str = None

    def __init__(self, character: str, color: str):
        """
        Constructs the screen element.

        Parameters:
            character (str): The character to display.
            color (str): The color of the character.
        """
        self.set_character_and_color(character, color)

    def set_character_and_color(self, character: str, color: str):
        """
        Sets the character of the screen element.

        Parameters:
            color: (str): The color of the character.
            character (str): The character to set.
        """
        self.__character = character
        self.__color = color

    def set_character(self, character: str):
        """
        Sets the character of the screen element.

        Parameters:
            character (str): The character to set.
        """
        self.__character = character

    def get_character(self):
        """
        Gets the character of the screen element.

        Returns:
            str: The character of the screen element.
        """
        return self.__character

    def get_color(self):
        """
        Gets the color of the screen element.

        Returns:
            str: The color of the screen element.
        """
        return self.__color

    def set_color(self, color: str):
        """
        Sets the color of the screen element.

        Parameters:
            color (str): The color to set.
        """
        self.__color = color


class ConsoleV4(BaseDevice):
    """
    The Console device class.
    """

    # synthetic cursor control
    _cursor_is_displayed: bool = False
    _cursor_last_display_time: float = 0

    # cursor management
    _cursorX: int = 0
    _cursorY: int = 0

    current_text_color = TEXT_COLOR  # the current color of the console.  New characters will use this color.
    current_back_color = BACK_COLOR  # the current background color of the console.  New characters will use this color.

    ansi_sequence = None  # a variable to hold the current ANSI escape sequence being processed

    def __init__(self, starting_address, width, height, interrupt_number: int):
        """
        Constructs all the necessary attributes for the console device.

        Parameters:
            starting_address (int): The starting address of the console device.
            interrupt_number (int): The interrupt number for the console device.
            width (int): The width of the console.
            height (int): The height of the console.
        """
        super().__init__(starting_address, 1)
        self.canvas = None
        self.form_ready = False
        self._width = width
        self._height = height
        self.display_buffer = [[ScreenElement(' ', self.current_text_color) for _ in range(self._width)] for _ in
                               range(self._height)]
        self.interrupt_number = interrupt_number
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.keypress = ""
        self.keypress_event = threading.Event()
        self.console_window = None
        self.console_closed = False
        self.start_form()

    def find_last_non_space_character_on_current_row(self):
        """
        Finds the last non-space character on the current row.
        Returns:
            int: The last non-space character on the current row.
        """
        for x in range(self._width - 1, -1, -1):
            if self.display_buffer[self._cursorY][x].get_character() != ' ':
                return x + 1
        return 0

    def handle_meta_data(self, data: int):
        """
        Handles metadata, such as control characters and ANSI escape sequences.
        This will get called for each character being received.

        Args:
            data: The data to process.

        Returns: True if data is handled, False otherwise.

        """

        if self.ansi_sequence is None:
            # This is outside an ANSI sequence
            # Check if a sequence is starting
            if data == 27:
                self.ansi_sequence = chr(data)
                return True
            # a sequence has not started, so check for control characters
            if self.handle_control_character(data):
                return True
            return False
        else:
            self.ansi_sequence += chr(data)
            # if sequence is for color, set the current_color accordingly then set ansi_sequence to None
            # return True to indicate that no character is to be displayed, yet

            if self.handle_ansi_escaped_escape():
                return False  # it was handled, but we want the escape to be displayed
            if self.handle_ansi_color():
                return True  # short-circuit the rest of the processing because this has been handled

            # other ansi handling goes here

            return True

    def handle_control_character(self, data):
        """
        Handles control characters.
        Args:
            data: int: The data to process.

        Returns:
            True if the data was handled, False otherwise.
        """
        if data == 13:  # CR
            self._cursorX = 0
            return True
        elif data == 10:  # LF
            self._cursorY += 1
            if self._cursorY >= self._height:
                self.scroll_up()
                self._cursorY -= 1
            return True
        elif data == 9:  # TAB
            self._cursorX += 4
            if self._cursorX >= self._width:
                self._cursorX = self._width - 1
            return True
        elif data == 12:  # FF
            self.display_buffer = [[ScreenElement(' ', self.current_text_color) for _ in range(self._width)] for _ in
                                   range(self._height)]
            return True
        elif data == 8:  # BS
            self._cursorX -= 1
            if self._cursorX < 0:
                self._cursorY -= 1
                if self._cursorY < 0:
                    self._cursorY = 0
                    self._cursorX = 0
                self._cursorX = self.find_last_non_space_character_on_current_row()
            self.write_to_display_buffer(self._cursorY * self._width + self._cursorX, chr(32))
            return True
        else:
            return False

    def handle_ansi_color(self):
        """
        Handles ANSI color sequences.
        Returns:
            bool: True the data is being handled, False otherwise.
        """
        # Map of ANSI color codes to their corresponding color values
        # noinspection SpellCheckingInspection
        color_map = {
            "32": "#00FF00",  # green
            "31": "#FF0000",  # red
            "33": "#FFA500",  # orange
            "34": "#0000FF",  # blue
            "35": "#FF00FF",  # purple
            "36": "#00FFFF",  # cyan
            "37": "#FFFFFF",  # white
            "30": "#000000"  # black
        }

        if self.ansi_sequence.startswith("\x1b["):  # escape [ is for color
            # validate that the sequence is complete
            if self.ansi_sequence[-1] == "m":
                # set the current color to the color specified in the sequence
                color_code = self.ansi_sequence[2:-1]
                # set the current color to the color specified
                self.current_text_color = color_map.get(color_code, self.current_text_color)
                # clear the ansi_sequence since we're done with this sequence
                self.ansi_sequence = None
            return True  # this was handled
        else:
            # if the sequence we are building becomes too long to be valid, clear the sequence
            if len(self.ansi_sequence) > 10:  # arbitrary limit
                self.ansi_sequence = None
            return False  # this was not handled

    def write_to_display_buffer(self, address, value: str):
        """
        This method writes a character to the display buffer at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        y = address // self._width
        x = address % self._width
        self.display_buffer[y][x].set_character_and_color(character=value, color=self.current_text_color)

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

        if self.input_queue.qsize() > 0:
            interrupt_bus.set_interrupt(self.interrupt_number)

        self.process_keypress()
        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                if not self.input_queue.empty():
                    buffer_data = self.input_queue.get()
                    if len(buffer_data) > 0:
                        data_bus.set_data(ord(buffer_data))
                    control_bus.set_read_request(False)
                    control_bus.set_response(True)
            if control_bus.get_write_request():
                data = data_bus.get_data()
                self.output_queue.put(data)
                control_bus.set_write_request(False)
                control_bus.set_response(True)

    def scroll_up(self):
        """
        Scrolls the display buffer up by one line.
        """
        self.display_buffer = self.display_buffer[1:] + [
            [ScreenElement(' ', self.current_text_color) for _ in range(self._width)]]

    def console_is_ready(self):
        """
        Checks if the console is ready.

        Returns:
            bool: True if the console is ready, False otherwise.
        """
        return self.console_window is not None and self.form_ready

    def process_keypress(self):
        """
        Processes the keypress event by putting the keypress into the input queue.

        """
        if self.keypress_event.is_set():
            log_message("Keypress detected")
            self.input_queue.put(self.keypress)
            self.keypress_event.clear()
            log_message(f"Keypress: {self.keypress} cleared.")

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

        def process_cursor():
            """
            Toggles the cursor.
            """
            self._cursor_is_displayed = not self._cursor_is_displayed
            show_display_buffer()
            self.console_window.after(int(1000 / CURSOR_CHANGES_PER_SECOND), process_cursor)

        def process_data(data: int):
            """
            Processes the data to be displayed on the console.
            If the data is a CR, LF, or BS, the cursor is moved accordingly and the display buffer is updated.
            If the data is a printable character, the character is written to the display buffer and the cursor
            is moved.
            Args:
                data:

            Returns:

            """

            if self.handle_meta_data(data):
                return

            self.write_to_display_buffer(self._cursorY * self._width + self._cursorX, chr(data))
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
            Destroys console window widgets and set a flag to stop the console window.
            Returns:
                None

            """
            widgets = self.console_window.winfo_children()
            for widget in widgets:
                widget.destroy()
            self.console_closed = True

        def show_display_buffer():
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                                         fill=self.current_back_color)

            for y in range(self._height):
                for x in range(self._width):
                    if self._cursor_is_displayed and self._cursorX == x and self._cursorY == y:
                        character = '_'
                    else:
                        character = self.display_buffer[y][x].get_character()
                    color = self.display_buffer[y][x].get_color()
                    self.canvas.create_text((x * CHARACTER_WIDTH) + (x * HORIZONTAL_PIXEL_SEPARATION),
                                            (y * CHARACTER_HEIGHT) + (y * VERTICAL_PIXEL_SEPARATION),
                                            anchor="nw",
                                            text=character,
                                            fill=color, font=(CONSOLE_FONT, 16, ""))

        def create_canvas():
            """
            Creates the canvas for the console.
            Returns:

            """
            canvas_width = (self._width * CHARACTER_WIDTH) + (self._width * HORIZONTAL_PIXEL_SEPARATION)
            canvas_height = (self._height * CHARACTER_HEIGHT) + (self._height * VERTICAL_PIXEL_SEPARATION)
            self.canvas = tk.Canvas(self.console_window, width=canvas_width, height=canvas_height)
            self.canvas.pack()

        def process_output_queue():
            """
            Processes the output queue.
            This queue contains the data to be displayed on the console.
            Returns:
                None

            """
            data_changed = False
            while not self.output_queue.empty():
                data_changed = True
                log_message(f"Queue size: {self.output_queue.qsize()}")
                data = self.output_queue.get(block=True)
                process_data(data)
            if data_changed:
                show_display_buffer()
            self.console_window.after(OUTPUT_QUEUE_PROCESSING_RATE, process_output_queue)

        self.console_window = tk.Tk()
        self.console_window.title("RubbishPy Console v4")
        window_icon = tk.PhotoImage(file="../Resources/graphics/console_icon.png")
        self.console_window.iconphoto(True, window_icon)
        create_canvas()
        self.console_window.bind("<KeyPress>", capture_keypress)
        self.console_window.protocol("WM_DELETE_WINDOW", on_close)
        self.form_ready = True
        process_output_queue()
        process_cursor()
        self.console_window.mainloop()

    def handle_ansi_escaped_escape(self):
        """
        Handles ANSI escaped escape sequences.
        Returns:
            bool: Always returns False.
        """
        if self.ansi_sequence == "\x1b\x1b":
            self.ansi_sequence = None
            return True
        return False
