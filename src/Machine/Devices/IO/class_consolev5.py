import queue
import threading

import pygame

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice

cursor_blink_milliseconds = 250


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
        self.value = value
        self.command = command

    def get_command(self):
        return self.command

    def set_command(self, command):
        self.command = command

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


class DisplayElement(DisplayCommand):
    def __init__(self, x, y, character: str):
        self.x = x
        self.y = y
        self.character = character
        self.redraw = True

    def get_character(self):
        return self.character

    def set_character(self, character):
        if character != self.character:
            self.redraw = True
        self.character = character

    def set_redraw(self, redraw):
        self.redraw = redraw


class ConsoleV5(BaseDevice):
    class Display:
        def __init__(self, output_q, input_q, display_width, display_height, character_width,
                     character_height, font_size):
            self.display_queue = output_q  # a queue of DisplayElement objects to process
            self.input_queue = input_q
            self.character_width = character_width
            self.character_height = character_height
            self.screen = pygame.display.set_mode((display_width * character_width, display_height * character_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', font_size)
            self.cursor_state = False
            self.last_cursor_change = pygame.time.get_ticks()
            self.cursor_x: int = 0
            self.cursor_y: int = 0

        def run(self):
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        # add to input queue
                        if event.unicode:
                            self.input_queue.put(ord(event.unicode))

                while not self.display_queue.empty():
                    command = self.display_queue.get_nowait()
                    # if command is a DisplayControl object, process it
                    if isinstance(command, DisplayControl):
                        if command.get_command() == 'clear':
                            self.screen.fill((0, 0, 0))
                    if isinstance(command, DisplayControl):
                        if command.get_command() == 'cursor_x':
                            self.turn_cursor_off()
                            self.cursor_x = int(command.get_value())
                        if command.get_command() == 'cursor_y':
                            self.turn_cursor_off()
                            self.cursor_y = int(command.get_value())
                    if isinstance(command, DisplayElement):
                        display_element: DisplayElement = command
                        text_to_display = display_element.get_character()
                        self.turn_cursor_off()
                        text = self.font.render(text_to_display, True, (255, 255, 255))
                        # blank the area we are about to write to
                        text_size = self.font.size(text_to_display)
                        position = (display_element.x * self.character_width, display_element.y * self.character_height)
                        pygame.draw.rect(self.screen, (0, 0, 0), (position[0], position[1], text_size[0], text_size[1]))
                        # draw the character
                        self.screen.blit(text, (
                            display_element.x * self.character_width, display_element.y * self.character_height))

                # draw the cursor
                if pygame.time.get_ticks() - self.last_cursor_change > cursor_blink_milliseconds:
                    self.update_cursor()
                    self.cursor_state = not self.cursor_state
                    self.last_cursor_change = pygame.time.get_ticks()
                pygame.display.flip()
                self.clock.tick(20)

            pygame.quit()

        def turn_cursor_off(self):
            # turn the cursor off before drawing the screen
            self.cursor_state = False
            self.update_cursor()

        def update_cursor(self):
            if self.cursor_state:
                cursor = self.font.render('_', False, (255, 255, 255))
                self.screen.blit(cursor, (self.cursor_x * self.character_width,
                                          self.cursor_y * self.character_height))
            else:
                cursor = self.font.render('_', False, (0, 0, 0))
                self.screen.blit(cursor, (self.cursor_x * self.character_width,
                                          self.cursor_y * self.character_height))

    def __init__(self, starting_address: int, width: int, height: int, interrupt_number: int):
        super().__init__(starting_address, 1)
        pygame.init()
        pygame.display.set_caption("RubbishPy Console v5")
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.display = self.Display(self.output_queue, self.input_queue, display_width=width, display_height=height,
                                    character_width=12, character_height=22, font_size=20)
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.width: int = width
        self.height: int = height
        self.interrupt_number: int = interrupt_number
        self.display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]
        self.output_form = threading.Thread(target=self.display.run)
        self.output_form.start()
        self.write_buffer_to_queue()

    def send_cursor_location(self):
        self.output_queue.put(DisplayControl('cursor_x', str(self.cursor_x)))
        self.output_queue.put(DisplayControl('cursor_y', str(self.cursor_y)))

    def scroll_up(self):
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
        self.output_queue.put(DisplayControl('clear', ''))

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
            self.send_cursor_location()
            return True
        elif data == 10:  # LF
            self.cursor_y += 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y -= 1
            self.send_cursor_location()
            return True
        elif data == 9:  # TAB
            self.cursor_x += 4
            if self.cursor_x >= self.width:
                self.cursor_x = self.width - 1
            self.send_cursor_location()
            return True
        elif data == 12:  # FF
            self.display_buffer = [[DisplayElement(x, y, ' ') for x in range(80)] for y in range(25)]
            self.output_queue.put(DisplayControl('clear', ''))
            self.cursor_x = 0
            self.cursor_y = 0
            self.send_cursor_location()
            return True
        elif data == 8:  # BS
            self.cursor_x -= 1
            if self.cursor_x < 0:
                self.cursor_y -= 1
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
        self.output_queue.put(self.display_buffer[self.cursor_y][self.cursor_x])
        self.cursor_x += 1
        if self.cursor_x >= self.width:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.height:
                self.scroll_up()
                self.cursor_y -= 1
        self.send_cursor_location()

    def write_buffer_to_queue(self):
        """
        Writes the display buffer to the output queue.
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.display_buffer[y][x].redraw:
                    self.display_buffer[y][x].redraw = False
                    self.output_queue.put(self.display_buffer[y][x])

    def cycle(self, address_bus, data_bus, control_bus, interrupt_bus):
        # if the display thread has ended, raise the halt interrupt
        if not self.output_form.is_alive():
            interrupt_bus.set_interrupt(Interrupts.halt)
            return

        # if there is data in the input queue,
        # raise the interrupt to signal that there is data available
        if not self.input_queue.empty():
            interrupt_bus.set_interrupt(self.interrupt_number)

        if self.address_is_valid(address_bus):
            if control_bus.get_read_request():
                if not self.input_queue.empty():
                    buffer_data = self.input_queue.get()
                    data_bus.set_data(buffer_data)
                    control_bus.set_read_request(False)
                    control_bus.set_response(True)
            if control_bus.get_write_request():
                data = data_bus.get_data()
                self.process_output(data)
                self.write_buffer_to_queue()
                control_bus.set_write_request(False)
                control_bus.set_response(True)