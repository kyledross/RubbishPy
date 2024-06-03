import hashlib
import os
import pickle
import queue
import threading
import time

import pygame

from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice

FRAMERATE = 90
CURSOR_BLINK_MILLISECONDS = 250


class DisplayCommand:
    """
    This is the base class for display elements and display controls.
    """


class DisplayControl(DisplayCommand):
    """
    A command to the display.

    command of "clear" clears the display.

    """

    def __init__(self, command: str, value: str):
        self.__value = value
        self.__command = command

    def get_command(self):
        return self.__command

    def set_command(self, command):
        self.__command = command

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value


class DisplayElement(DisplayCommand):
    def __init__(self, x, y, character: str):
        self.__x = x
        self.__y = y
        self.__character = character
        self.__redraw = True

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_character(self):
        return self.__character

    def set_character(self, character):
        if character != self.__character:
            self.__redraw = True
        self.__character = character

    def get_redraw(self):
        return self.__redraw

    def set_redraw(self, redraw):
        self.__redraw = redraw


def get_queue_hash(q: queue.Queue) -> str:
    q_hash = hashlib.sha256()
    q_list = list(q.queue)
    q_hash.update(pickle.dumps(q_list))
    return q_hash.hexdigest()


class Console(BaseDevice):
    class Display:
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

        def set_cursor_x(self, x: int):
            self.__cursor_x = x

        def get_cursor_x(self) -> int:
            return self.__cursor_x

        def set_cursor_y(self, y: int):
            self.__cursor_y = y

        def get_cursor_y(self) -> int:
            return self.__cursor_y

        def set_cursor_state(self, state: bool):
            self.__cursor_state = state

        def get_cursor_state(self) -> bool:
            return self.__cursor_state

        def get_last_cursor_change(self) -> int:
            return self.__last_cursor_change

        def set_last_cursor_change(self, change_time: int):
            self.__last_cursor_change = change_time

        def run(self):
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
            self.set_last_cursor_change(pygame.time.get_ticks())

            self.__running = True
            pygame.key.set_repeat(500, 50)

            def process_events():
                while self.__running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.__running = False
                        if event.type == pygame.KEYDOWN:
                            # add to input queue
                            if event.unicode:
                                self.__input_queue.put(ord(event.unicode))
                    time.sleep(0.05)

            # Start the event processing in a separate thread
            event_thread = threading.Thread(target=process_events,
                                            name=self.__parent_console_device_id + "_Display::process_events")
            event_thread.start()

            while self.__running:
                while not self.__display_queue.empty():
                    command = self.__display_queue.get_nowait()
                    # if command is a DisplayControl object, process it
                    if isinstance(command, DisplayControl):
                        if command.get_command() == 'clear':
                            self.__screen.fill((0, 0, 0))
                    if isinstance(command, DisplayControl):
                        if command.get_command() == 'cursor_x':
                            self.turn_cursor_off()
                            self.set_cursor_x(int(command.get_value()))
                        if command.get_command() == 'cursor_y':
                            self.turn_cursor_off()
                            self.set_cursor_y(int(command.get_value()))
                    if isinstance(command, DisplayElement):
                        display_element: DisplayElement = command
                        text_to_display = display_element.get_character()
                        self.turn_cursor_off()
                        text = self.__font.render(text_to_display, True, (255, 255, 255))
                        # blank the area we are about to write to
                        text_size = self.__font.size(text_to_display)
                        position = (display_element.get_x() * self.__character_width,
                                    display_element.get_y() * self.__character_height)
                        pygame.draw.rect(self.__screen, (0, 0, 0),
                                         (position[0], position[1], text_size[0], text_size[1]))
                        # draw the character
                        self.__screen.blit(text, (
                            display_element.get_x() * self.__character_width,
                            display_element.get_y() * self.__character_height))

                # draw the cursor
                if pygame.time.get_ticks() - self.get_last_cursor_change() > CURSOR_BLINK_MILLISECONDS:
                    self.update_cursor()
                    self.set_cursor_state(not self.get_cursor_state())
                    self.set_last_cursor_change(pygame.time.get_ticks())
                pygame.display.flip()
                self.__clock.tick(FRAMERATE)
                pygame.event.pump()

            pygame.quit()

        def turn_cursor_off(self):
            # turn the cursor off before drawing the screen
            self.set_cursor_state(False)
            self.update_cursor()

        def update_cursor(self):
            if self.get_cursor_state():
                cursor = self.__font.render('_', False, (255, 255, 255))
                self.__screen.blit(cursor, (self.get_cursor_x() * self.__character_width,
                                            self.get_cursor_y() * self.__character_height))
            else:
                cursor = self.__font.render('_', False, (0, 0, 0))
                self.__screen.blit(cursor, (self.get_cursor_x() * self.__character_width,
                                            self.get_cursor_y() * self.__character_height))

    def __init__(self, starting_address: int, width: int, height: int, interrupt_number: int, address_bus: AddressBus,
                 data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        super().__init__(starting_address, 1, address_bus, data_bus, control_bus, interrupt_bus)
        self.__output_form = None
        self.__output_queue = queue.Queue()
        self.__input_queue = queue.Queue()
        self.__last_input_queue_hash = get_queue_hash(self.__input_queue)
        self.__display = self.Display(console_device_id=self.get_device_id(), output_q=self.__output_queue,
                                      input_q=self.__input_queue, display_width=width, display_height=height,
                                      character_width=12, character_height=22, font_size=20)
        self.__cursor_x: int = 0
        self.__cursor_y: int = 0
        self.__width: int = width
        self.__height: int = height
        self.__interrupt_number: int = interrupt_number
        self.__display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]

    def get_cursor_x(self) -> int:
        return self.__cursor_x

    def set_cursor_x(self, cursor_x: int):
        self.__cursor_x = cursor_x

    def get_cursor_y(self) -> int:
        return self.__cursor_y

    def set_cursor_y(self, cursor_y: int):
        self.__cursor_y = cursor_y

    def get_output_form(self) -> threading.Thread:
        return self.__output_form

    def set_output_form(self, output_form: threading.Thread):
        self.__output_form = output_form

    def get_display_buffer(self) -> list:
        return self.__display_buffer

    def set_display_buffer(self, display_buffer: list):
        self.__display_buffer = display_buffer

    def start(self):
        self.set_output_form(threading.Thread(target=self.__display.run, name=self.get_device_id() + "::display_run"))
        self.get_output_form().start()
        self.write_buffer_to_queue()
        threading.Thread(target=self.process_buses, name=self.get_device_id() + "::process_buses").start()

    def send_cursor_location(self):
        self.__output_queue.put(DisplayControl('cursor_x', str(self.get_cursor_x())))
        self.__output_queue.put(DisplayControl('cursor_y', str(self.get_cursor_y())))

    def scroll_up(self):
        """
        Scrolls the display buffer up by one line.
        """
        for y in range(1, self.__height):
            for x in range(self.__width):
                self.get_display_buffer()[y - 1][x].set_character(self.get_display_buffer()[y][x].get_character())
                self.get_display_buffer()[y - 1][x].set_redraw(True)
        for x in range(self.__width):
            self.get_display_buffer()[self.__height - 1][x].set_character(' ')
            self.get_display_buffer()[self.__height - 1][x].set_redraw(True)
        # add a clear command to the output queue
        self.__output_queue.put(DisplayControl('clear', ''))

    def find_last_non_space_character_on_current_row(self):
        """
        Finds the last non-space character on the current row.
        Returns:
            int: The last non-space character on the current row.
        """
        for x in range(self.__width - 1, -1, -1):
            if self.get_display_buffer()[self.get_cursor_y()][x].get_character() != ' ':
                return x + 1
        return 0

    def write_to_display_buffer(self, address: int, value: str):
        """
        This method writes a character to the display buffer at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        y = address // self.__width
        x = address % self.__width
        self.get_display_buffer()[y][x].set_character(character=value)

    def handle_control_character(self, data: int):
        """
        Handles control characters.
        Args:
            data: int: The data to process.

        Returns:
            True if the data was handled, False otherwise.
        """
        if data == 13:  # CR
            self.set_cursor_x(0)
            self.send_cursor_location()
            return True
        elif data == 10:  # LF
            self.set_cursor_y(self.get_cursor_y() + 1)
            if self.get_cursor_y() >= self.__height:
                self.scroll_up()
                self.set_cursor_y(self.get_cursor_y() - 1)
            self.send_cursor_location()
            return True
        elif data == 9:  # TAB
            self.set_cursor_x(self.get_cursor_x() + 4)
            if self.get_cursor_x() >= self.__width:
                self.set_cursor_x(self.__width - 1)
            self.send_cursor_location()
            return True
        elif data == 12:  # FF
            self.set_display_buffer([[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)])
            self.__output_queue.put(DisplayControl('clear', ''))
            self.set_cursor_x(0)
            self.set_cursor_y(0)
            self.send_cursor_location()
            return True
        elif data == 8:  # BS
            self.set_cursor_x(self.get_cursor_x() - 1)
            if self.get_cursor_x() < 0:
                self.set_cursor_y(self.get_cursor_y() - 1)
                if self.get_cursor_y() < 0:
                    self.set_cursor_y(0)
                    self.set_cursor_x(0)
                self.set_cursor_x(self.find_last_non_space_character_on_current_row())
            self.write_to_display_buffer(self.get_cursor_y() * self.__width + self.get_cursor_x(), " ")
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

        self.write_to_display_buffer(self.get_cursor_y() * self.__width + self.get_cursor_x(), chr(data))

        # add the DisplayElement object to the output queue
        self.__output_queue.put(self.get_display_buffer()[self.get_cursor_y()][self.get_cursor_x()])
        self.set_cursor_x(self.get_cursor_x() + 1)
        if self.get_cursor_x() >= self.__width:
            self.set_cursor_x(0)
            self.set_cursor_y(self.get_cursor_y() + 1)
            if self.get_cursor_y() >= self.__height:
                self.scroll_up()
                self.set_cursor_y(self.get_cursor_y() - 1)
        self.send_cursor_location()

    def write_buffer_to_queue(self):
        """
        Writes the display buffer to the output queue.
        """
        for y in range(self.__height):
            for x in range(self.__width):
                if self.get_display_buffer()[y][x].get_redraw():
                    self.get_display_buffer()[y][x].set_redraw(False)
                    self.__output_queue.put(self.get_display_buffer()[y][x])

    def process_buses(self):
        while self.is_running():
            self.control_bus().lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus().power_on:
                # if the display thread has ended, raise the halt interrupt
                if not self.get_output_form().is_alive():
                    self.interrupt_bus().set_interrupt(Interrupts.halt)
                # if there is data in the input queue,
                # raise the interrupt to signal that there is data available
                if get_queue_hash(self.__input_queue) != self.__last_input_queue_hash:
                    self.__last_input_queue_hash = get_queue_hash(self.__input_queue)
                    self.interrupt_bus().set_interrupt(self.__interrupt_number)
                if self.address_is_valid(self.address_bus()):
                    if self.control_bus().read_request:
                        if not self.__input_queue.empty():
                            buffer_data = self.__input_queue.get()
                            self.data_bus().data = buffer_data
                            self.control_bus().read_request = False
                            self.control_bus().response = True
                    if self.control_bus().write_request:
                        data = self.data_bus().data
                        self.process_output(data)
                        self.write_buffer_to_queue()
                        self.control_bus().write_request = False
                        self.control_bus().response = True
            self.control_bus().unlock_bus()
        self.set_finished()
