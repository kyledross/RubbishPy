import os
import queue
import threading
import time
from enum import IntFlag

import pygame

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice

MAX_FRAMERATE = 90
"""
The maximum framerate for the console display.
"""
CURSOR_BLINK_MILLISECONDS = 250
"""
The number of milliseconds between cursor blinks.
"""


class DisplayCommandList(IntFlag):
    """
    A list of commands that can be sent to the display.
    """
    clear = 0
    cursor_x = 1
    cursor_y = 2


class DisplayCommand:
    """
    This is the base class for display elements and display controls.
    """


class DisplayControl(DisplayCommand):
    """
    A command to the display.
    This is used to send commands to the display.
    """

    def __init__(self, command: DisplayCommandList, value: str):
        self.__value = value
        self.__command = command

    @property
    def command(self) -> DisplayCommandList:
        return self.__command

    @command.setter
    def command(self, command: DisplayCommandList):
        self.__command = command

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value


class DisplayElement(DisplayCommand):
    """
    A display element for rendering characters on a screen.

    This class represents an element with properties such as position and a character to
    display. It provides methods to retrieve and update these attributes while keeping
    track of whether the element needs to be redrawn.

    Attributes:
        x (int): The horizontal position of the display element.
        y (int): The vertical position of the display element.
        character (str): The character to display.
        redraw (bool): Indicates if the element needs to be redrawn.
    """
    def __init__(self, x, y, character: str):
        self.__x = x
        self.__y = y
        self.__character = character
        self.__redraw = True

    @property
    def x(self) -> int:
        """
        The x position of the display element.

        """
        return self.__x

    @property
    def y(self) -> int:
        """
        The y position of the display element.

        """
        return self.__y

    @property
    def character(self) -> str:
        """
        The character to display.

        """
        return self.__character

    @character.setter
    def character(self, character: str):
        """
        Sets the character to display.
        Args:
            character: The character to display.

        """
        if character != self.__character:
            self.__redraw = True
        self.__character = character

    @property
    def redraw(self) -> bool:
        """
        Whether the display element needs to be redrawn.
        Returns:

        """
        return self.__redraw

    @redraw.setter
    def redraw(self, redraw: bool):
        """
        Sets whether the display element needs to be redrawn.
        Args:
            redraw: True if the element needs to be redrawn, False otherwise.

        """
        self.__redraw = redraw


class Console(BaseDevice):
    """
    A text display and input device.
    """

    class Display:
        """
        The visible display of the console.
        """

        def __init__(self, console_device_id: str, output_q: queue.Queue, input_q: queue.Queue, display_width: int,
                     display_height: int, character_width: int, character_height: int, font_size: int):
            self.__font = None
            self.__clock = None
            self.__screen = None
            self.__display_queue = output_q
            self.__input_queue = input_q
            self.__character_width = character_width
            self.__character_height = character_height
            self.__display_width = display_width
            self.__display_height = display_height
            self.__font_size = font_size
            self.__cursor_state = False
            self.__last_cursor_change = 0
            self.__cursor_x: int = 0
            self.__cursor_y: int = 0
            self.__running: bool = False
            self.__parent_console_device_id = console_device_id

        @property
        def cursor_x(self) -> int:
            """
            The x position of the cursor.
            Returns:

            """
            return self.__cursor_x

        @cursor_x.setter
        def cursor_x(self, cursor_x: int) -> None:
            """
            Sets the x position of the cursor.
            Args:
                cursor_x: The x position of the cursor.
            """
            self.__cursor_x = cursor_x

        @property
        def cursor_y(self) -> int:
            """
            The y position of the cursor.
            Returns: The y position of the cursor.

            """
            return self.__cursor_y

        @cursor_y.setter
        def cursor_y(self, cursor_y: int) -> None:
            """
            Sets the y position of the cursor.
            Args:
                cursor_y: The y position of the cursor.

            Returns:

            """
            self.__cursor_y = cursor_y

        @property
        def cursor_state(self) -> bool:
            """
            The state of the cursor.
            Returns: True if the cursor is visible, False otherwise.

            """
            return self.__cursor_state

        @cursor_state.setter
        def cursor_state(self, cursor_state: bool):
            """
            Sets the state of the cursor.
            Args:
                cursor_state: True if the cursor is visible, False otherwise.

            Returns:

            """
            self.__cursor_state = cursor_state

        @property
        def last_cursor_change(self) -> int:
            """
            The time of the last cursor change.
            This is used to determine when the cursor's visibility should be changed, based on the blink rate.
            Returns:

            """
            return self.__last_cursor_change

        @last_cursor_change.setter
        def last_cursor_change(self, last_cursor_change: int):
            """
            Sets the time of the last cursor change.
            Args:
                last_cursor_change: The time of the last cursor change.

            Returns:

            """
            self.__last_cursor_change = last_cursor_change

        def run(self) -> None:
            """
            The main loop for the visible display.
            Returns:

            """

            def process_events() -> None:
                """
                This method continuously processes events for the display,
                such as key presses and window close events.
                The loop runs until the display is no longer running.
                Returns:

                """
                while self.__running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.__running = False
                        if event.type == pygame.KEYDOWN:
                            # add to input queue
                            if event.unicode:
                                self.__input_queue.put(ord(event.unicode))
                    time.sleep(0)

            pygame.init()
            pygame.display.set_caption("RubbishPy Console")
            icon = pygame.image.load('../Resources/graphics/console_icon.png')
            pygame.display.set_icon(icon)
            self.__screen = pygame.display.set_mode((self.__display_width * self.__character_width,
                                                     self.__display_height * self.__character_height))
            self.__clock = pygame.time.Clock()
            if os.name == 'nt':  # Windows
                # noinspection SpellCheckingInspection
                windir = os.getenv('WINDIR')
                # noinspection SpellCheckingInspection
                font_path = os.path.join(windir, 'Fonts', 'consola.ttf')
            else:  # Unix/Linux/MacOS/BSD/etc
                font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
            self.__font = pygame.font.Font(font_path, self.__font_size)
            self.last_cursor_change = pygame.time.get_ticks()

            self.__running = True
            pygame.key.set_repeat(500, 50)

            # Start the event processing in a separate thread
            event_thread = threading.Thread(target=process_events,
                                            name=self.__parent_console_device_id + "_Display::process_events")
            event_thread.start()
            self.main_loop()

        def main_loop(self) -> None:
            """
            The main loop for the console.

            """
            while self.__running:
                while not self.__display_queue.empty():
                    command = self.__display_queue.get_nowait()
                    # if command is a DisplayControl object, process it
                    if isinstance(command, DisplayControl):
                        if command.command == DisplayCommandList.clear:
                            self.__screen.fill((0, 0, 0))
                    if isinstance(command, DisplayControl):
                        if command.command == DisplayCommandList.cursor_x:
                            self.turn_cursor_off()
                            self.cursor_x = int(command.value)
                        if command.command == DisplayCommandList.cursor_y:
                            self.turn_cursor_off()
                            self.cursor_y = int(command.value)
                    if isinstance(command, DisplayElement):
                        display_element: DisplayElement = command
                        text_to_display = display_element.character
                        self.turn_cursor_off()
                        text = self.__font.render(text_to_display, True, (255, 255, 255))
                        # blank the area we are about to write to
                        text_size = self.__font.size(text_to_display)
                        position = (display_element.x * self.__character_width,
                                    display_element.y * self.__character_height)
                        pygame.draw.rect(self.__screen, (0, 0, 0),
                                         (position[0], position[1], text_size[0], text_size[1]))
                        # draw the character
                        self.__screen.blit(text, position)

                # draw the cursor
                if pygame.time.get_ticks() - self.last_cursor_change > CURSOR_BLINK_MILLISECONDS:
                    self.update_cursor()
                    self.cursor_state = not self.cursor_state
                    self.last_cursor_change = pygame.time.get_ticks()
                pygame.display.flip()
                self.__clock.tick(MAX_FRAMERATE)
                pygame.event.pump()

        def turn_cursor_off(self) -> None:
            """
            Turns the cursor off.
            Returns:

            """
            # turn the cursor off before drawing the screen
            self.cursor_state = False
            self.update_cursor()

        def update_cursor(self) -> None:
            """
            Updates the cursor's visibility, creating a blinking effect.

            Returns:

            """
            if self.cursor_state:
                cursor = self.__font.render('_', False, (255, 255, 255))
                self.__screen.blit(cursor, (self.cursor_x * self.__character_width,
                                            self.cursor_y * self.__character_height))
            else:
                cursor = self.__font.render('_', False, (0, 0, 0))
                self.__screen.blit(cursor, (self.cursor_x * self.__character_width,
                                            self.cursor_y * self.__character_height))

    def __init__(self, starting_address: int, width: int, height: int, interrupt_number: int, address_bus: AddressBus,
                 data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        super().__init__(starting_address, 1, address_bus, data_bus, control_bus, interrupt_bus)
        self.__output_form = None
        self.__output_queue = queue.Queue()
        self.__input_queue = queue.Queue()
        self.__display = self.Display(console_device_id=self.device_id, output_q=self.__output_queue,
                                      input_q=self.__input_queue, display_width=width, display_height=height,
                                      character_width=12, character_height=22, font_size=20)
        self.__cursor_x: int = 0
        self.__cursor_y: int = 0
        self.__width: int = width
        self.__height: int = height
        self.__interrupt_number: int = interrupt_number
        self.__display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]

    @property
    def width(self) -> int:
        """
        The width of the console display in columns.
        Returns:

        """
        return self.__width

    @width.setter
    def width(self, width: int):
        """
        Sets the width of the console display in columns.
        Args:
            width: The number of columns of the console, must be >0.

        Returns:

        """
        self.__width = width

    @property
    def height(self) -> int:
        """
        The height of the console display in rows.
        Returns:

        """
        return self.__height

    @height.setter
    def height(self, height: int):
        """
        Sets the height of the console display in rows.
        Args:
            height: The number of rows of the console, must be >0.

        Returns:

        """
        self.__height = height

    @property
    def cursor_x(self) -> int:
        """
        The x position of the cursor.
        Returns: The x position of the cursor.

        """
        return self.__cursor_x

    @cursor_x.setter
    def cursor_x(self, cursor_x: int):
        """
        Sets the x position of the cursor.
        Args:
            cursor_x: The x position of the cursor.

        Returns:

        """
        self.__cursor_x = cursor_x

    @property
    def cursor_y(self) -> int:
        """
        The y position of the cursor.
        Returns: The y position of the cursor.

        """
        return self.__cursor_y

    @cursor_y.setter
    def cursor_y(self, cursor_y: int):
        """
        Sets the y position of the cursor.
        Args:
            cursor_y: The y position of the cursor.

        Returns:

        """
        self.__cursor_y = cursor_y

    @property
    def output_form(self) -> threading.Thread:
        """
        The thread that runs the display.
        Returns:

        """
        return self.__output_form

    @output_form.setter
    def output_form(self, output_form: threading.Thread):
        """
        Sets the thread that runs the display.
        Args:
            output_form:

        Returns:

        """
        self.__output_form = output_form

    @property
    def display_buffer(self) -> list:
        """
        The display buffer.
        Returns:

        """
        return self.__display_buffer

    @display_buffer.setter
    def display_buffer(self, display_buffer: list):
        """
        Sets the display buffer.
        Args:
            display_buffer: The display buffer to set.

        Returns:

        """
        self.__display_buffer = display_buffer

    def start(self) -> None:
        """
        Starts the console device.
        Returns:

        """
        self.output_form = threading.Thread(target=self.__display.run, name=self.device_id + "::display_run")
        self.output_form.start()
        self.write_buffer_to_queue()
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()

    def send_cursor_location(self) -> None:
        """
        Sends the cursor location to the output queue. This is used to update the cursor on the display.
        Returns:

        """
        self.__output_queue.put(DisplayControl(DisplayCommandList.cursor_x, str(self.cursor_x)))
        self.__output_queue.put(DisplayControl(DisplayCommandList.cursor_y, str(self.cursor_y)))

    def scroll_up(self) -> None:
        """
        Scrolls the display buffer up by one line.
        """
        for y in range(1, self.height):
            for x in range(self.width):
                self.display_buffer[y - 1][x].character = self.display_buffer[y][x].character
                self.display_buffer[y - 1][x].redraw = True
        for x in range(self.width):
            self.display_buffer[self.height - 1][x].character = ' '
            self.display_buffer[self.height - 1][x].redraw = True
        # add a clear command to the output queue
        self.__output_queue.put(DisplayControl(DisplayCommandList.clear, ''))

    def find_last_non_space_character_on_current_row(self) -> int:
        """
        Finds the last non-space character on the current row.
        Returns:
            int: The last non-space character on the current row.
        """
        for x in range(self.width - 1, -1, -1):
            if self.display_buffer[self.cursor_y][x].character != ' ':
                return x + 1
        return 0

    def write_to_display_buffer(self, address: int, value: str):
        """
        This method writes a character to the display buffer at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        y = address // self.width
        x = address % self.width
        self.display_buffer[y][x].character = value

    def handle_control_character(self, data: int):
        """
        Handles control characters.
        Args:
            data: int: The data to process.

        Returns:
            True if the data was handled, False otherwise.
        """
        if data == 13:  # CR
            self.cursor_x = 0
            self.send_cursor_location()
            return True
        elif data == 10:  # LF
            self.cursor_y = self.cursor_y + 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y = self.cursor_y - 1
            self.send_cursor_location()
            return True
        elif data == 9:  # TAB
            self.cursor_x = self.cursor_x + 4
            if self.cursor_x >= self.width:
                self.cursor_x = self.width - 1
            self.send_cursor_location()
            return True
        elif data == 12:  # FF
            self.display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]
            self.__output_queue.put(DisplayControl(DisplayCommandList.clear, ''))
            self.cursor_x = 0
            self.cursor_y = 0
            self.send_cursor_location()
            return True
        elif data == 8:  # BS
            self.cursor_x = self.cursor_x - 1
            if self.cursor_x < 0:
                self.cursor_y = self.cursor_y - 1
                if self.cursor_y < 0:
                    self.cursor_y = 0
                    self.cursor_x = 0
                self.cursor_x = self.find_last_non_space_character_on_current_row()
            self.write_to_display_buffer(self.cursor_y * self.width + self.cursor_x, " ")
            self.send_cursor_location()
            return True
        else:
            return False

    def process_output(self, data: int):
        """
        This routine creates a DisplayElement object for the current cursor location and adds it to the output queue.

        Args:
            data:

        Returns:

        """
        if self.handle_control_character(data):
            return

        self.write_to_display_buffer(self.cursor_y * self.width + self.cursor_x, chr(data))

        # add the DisplayElement object to the output queue
        self.__output_queue.put(self.display_buffer[self.cursor_y][self.cursor_x])
        self.cursor_x = self.cursor_x + 1
        if self.cursor_x >= self.width:
            self.cursor_x = 0
            self.cursor_y = self.cursor_y + 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y = self.cursor_y - 1
        self.send_cursor_location()

    def write_buffer_to_queue(self) -> None:
        """
        Writes the display buffer to the output queue.
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.display_buffer[y][x].redraw:
                    self.display_buffer[y][x].redraw = False
                    self.__output_queue.put(self.display_buffer[y][x])

    def process_buses(self) -> None:
        """
        This method continuously processes the buses to read and write data to and from the console.
        Returns:

        """
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                # if the display thread has ended, raise the halt interrupt
                if not self.output_form.is_alive():
                    self.interrupt_bus.set_interrupt(Interrupts.halt)

                # if there is data in the input queue,
                # raise the interrupt to signal that there is data available
                if not self.__input_queue.empty():
                    self.interrupt_bus.set_interrupt(self.__interrupt_number)

                if self.address_is_valid(self.address_bus):
                    if self.control_bus.read_request:
                        if not self.__input_queue.empty():
                            buffer_data = self.__input_queue.get()
                            self.data_bus.data = buffer_data
                            self.control_bus.read_request = False
                            self.control_bus.response = True
                        if self.__input_queue.empty():
                            self.interrupt_bus.clear_interrupt(self.__interrupt_number)

                    if self.control_bus.write_request:
                        data = self.data_bus.data
                        self.process_output(data)
                        self.write_buffer_to_queue()
                        self.control_bus.write_request = False
                        self.control_bus.response = True
            self.control_bus.unlock_bus()
        self.finished = True
