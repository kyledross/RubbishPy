import queue
import threading

import pygame

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice


class DisplayCommand:
    """
    This is the base class for display elements and display controls.
    """


class DisplayControl(DisplayCommand):
    """
    A command to the display.

    command of "clear" clears the display.

    """

    def __init__(self, command: str):
        self.command = command

    def get_command(self):
        return self.command

    def set_command(self, command):
        self.command = command


class DisplayElement(DisplayCommand):
    def __init__(self, x, y, character: str):
        self.x = x
        self.y = y
        self.character = character

    def get_character(self):
        return self.character

    def set_character(self, character):
        self.character = character


class Consolev5(BaseDevice):
    class Display:
        def __init__(self, output_q, input_q):
            self.display_queue = output_q  # a queue of DisplayElement objects to process
            self.input_queue = input_q
            self.screen = pygame.display.set_mode((800, 600))
            self.character_width = 20
            self.character_height = 20
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 36)

        def run(self):
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        # add to input queue
                        self.input_queue.put(event.key)

                if self.display_queue.empty():
                    continue
                command = self.display_queue.get_nowait()
                # if command is a DisplayControl object, process it
                if isinstance(command, DisplayControl):
                    if command.get_command() == 'clear':
                        self.screen.fill((0, 0, 0))
                if isinstance(command, DisplayElement):
                    display_element: DisplayElement = command
                    text_to_display = display_element.get_character()
                    text = self.font.render(text_to_display, True, (255, 255, 255))
                    self.screen.blit(text, (
                        display_element.x * self.character_width, display_element.y * self.character_height))

                pygame.display.flip()
                self.clock.tick(10)

            pygame.quit()

    def __init__(self, starting_address: int, size: int):
        super().__init__(starting_address, size)
        pygame.init()
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.display = self.Display(self.output_queue, self.input_queue)
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.width: int = 80
        self.height: int = 25
        self.display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]
        self.output_form = threading.Thread(target=self.display.run)
        self.output_form.start()

    def scroll_up(self):
        """
        Scrolls the display buffer up by one line.
        """
        for y in range(1, self.height):
            for x in range(self.width):
                self.display_buffer[y - 1][x].character = self.display_buffer[y][x].character
        for x in range(self.width):
            self.display_buffer[self.height - 1][x].character = ' '

    def find_last_non_space_character_on_current_row(self):
        """
        Finds the last non-space character on the current row.
        Returns:
            int: The last non-space character on the current row.
        """
        for x in range(self.width - 1, -1, -1):
            if self.display_buffer[self.cursor_y][x].get_character() != ' ':
                return x + 1
        return 0

    def write_to_display_buffer(self, address, value: str):
        """
        This method writes a character to the display buffer at a given address.
        :param address: The address to write to.
        :param value: The character to write.
        """
        y = address // self.width
        x = address % self.width
        self.display_buffer[y][x].set_character(character=value)

    def handle_control_character(self, data):
        """
        Handles control characters.
        Args:
            data: int: The data to process.

        Returns:
            True if the data was handled, False otherwise.
        """
        if data == 13:  # CR
            self.cursor_x = 0
            self.output_queue.put(DisplayControl('clear'))
            return True
        elif data == 10:  # LF
            self.cursor_y += 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y -= 1
            return True
        elif data == 9:  # TAB
            self.cursor_x += 4
            if self.cursor_x >= self.width:
                self.cursor_x = self.width - 1
            return True
        elif data == 12:  # FF
            self.display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]
            return True
        elif data == 8:  # BS
            self.cursor_x -= 1
            if self.cursor_x < 0:
                self.cursor_y -= 1
                if self.cursor_y < 0:
                    self.cursor_y = 0
                    self.cursor_x = 0
                self.cursor_x = self.find_last_non_space_character_on_current_row()
            self.write_to_display_buffer(self.cursor_y * self.width + self.cursor_x, chr(32))
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
        self.cursor_x += 1
        if self.cursor_x >= self.width:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y -= 1

        output_string = ''
        for y in range(self.height):
            for x in range(self.width):
                output_string += self.display_buffer[y][x].get_character()
        self.output_queue.put(output_string)

    def cycle(self, address_bus, data_bus, control_bus, interrupt_bus):
        # if the display thread has ended, raise the halt interrupt
        if not self.output_form.is_alive():
            interrupt_bus.set_interrupt(Interrupts.halt)
            return

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
                self.process_output(data)
                control_bus.set_write_request(False)
                control_bus.set_response(True)
