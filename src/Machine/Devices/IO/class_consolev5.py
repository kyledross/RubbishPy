import queue
import threading
import time

import pygame
import datetime

from Constants.class_interrupts import Interrupts
from Machine.Devices.Bases.class_base_device import BaseDevice


class DisplayElement:
    def __init__(self, x, y, character: str):
        self.x = x
        self.y = y
        self.character = character


class Consolev5(BaseDevice):
    class Display:
        def __init__(self, output_q, input_q):
            self.display_queue = output_q  # a queue of DisplayElement objects to process
            self.input_queue = input_q
            self.screen = pygame.display.set_mode((800, 600))
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

                try:
                    text_to_display = self.display_queue.get_nowait()
                    self.screen.fill((0, 0, 0))
                except queue.Empty:
                    pass
                else:
                    text = self.font.render(text_to_display, True, (255, 255, 255))
                    self.screen.blit(text, (20, 20))

                pygame.display.flip()
                self.clock.tick(10)

            pygame.quit()

    def __init__(self, starting_address: int, size: int):
        super().__init__(starting_address, size)
        pygame.init()
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.display = self.Display(self.output_queue, self.input_queue)
        self.cursor_X: int = 0
        self.cursor_Y: int = 0
        self.output_form = threading.Thread(target=self.display.run)
        self.output_form.start()

    def process_output(self, data: int):
        """
        This routine creates a DisplayElement object for the current cursor location and adds it to the output queue.

        Args:
            data:

        Returns:

        """

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
