import queue
import threading
import time
import numpy
import pygame
from pygame.mixer import Sound
from typing import List

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice

END_OF_FRAME = -1
END_OF_TRANSACTION = -2


def play_sounds(sounds: List[Sound]):
    """
    This method plays a list of sounds.
    """
    pygame.mixer.init(channels=len(sounds))
    channels = []
    # Create a channel for each sound and play it
    for i, sound in enumerate(sounds):
        channel = pygame.mixer.Channel(i)
        channel.play(sound)
        channels.append(channel)
        time.sleep(0)

    while any(channel.get_busy() for channel in channels):
        time.sleep(0)


def build_sound(duration_ms: int, frequency: float, volume: float) -> Sound:
    """
    This method builds a pygame sound to be played
    Args:
        duration_ms: The duration of the sound in milliseconds.
        frequency: The frequency of the sound.
        volume: The volume of the sound.

    Returns: A pygame sound to be played.

    """
    sample_rate: int = 44100
    n_samples: int = int(round(duration_ms / 1000 * sample_rate))
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2 ** 15 - 1
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(volume * max_sample * numpy.sin(2 * numpy.pi * frequency * t)))
        buf[s][1] = int(round(volume * max_sample * numpy.sin(2 * numpy.pi * frequency * t)))
    sound = pygame.sndarray.make_sound(buf)
    return sound


def build_sounds_from_queue(command_queue: queue.Queue) -> List[Sound]:
    """
    This method builds sounds from the command queue.
    """
    sounds = []
    # build a list of sounds from the queue
    duration_ms = command_queue.get()
    queue_byte: int
    queue_byte = command_queue.get()
    while queue_byte != END_OF_FRAME:
        frequency: float = queue_byte / 100
        volume: float = command_queue.get() / 10
        sound = build_sound(duration_ms, frequency, volume)
        sounds.append(sound)
        queue_byte = command_queue.get()
    return sounds


def complete_frame_is_ready(command_queue: queue.Queue) -> bool:
    """
    This method checks the command queue for a complete frame to play.
    A frame is complete when a -1 is found in the queue.
    """
    queue_end_index = len(command_queue.queue)
    for i in range(queue_end_index):
        if command_queue.queue[i] == END_OF_FRAME:
            return True
    return False


class SoundCard(BaseDevice):
    """
    A class used to represent a Sound Card device.
    Sounds are played by sending frames to the sound card within a transaction.
    All frames are built and queued up until the transaction is complete.
    After the transaction is complete, the sounds in the queue are played.
    A frame consists of:
        - Integer representing the length of the sound in milliseconds.
        - One or more frames consisting of two integers:
            - The first integer represents the frequency of the sound with two decimal places, packed * 100
              For example, middle C of 261.63Hz would be 26163.
            - The second integer represents the volume of the sound from 0 to 1, packed * 10
        - A final integer of -1 to signify the end of the sound frame
        - A final integer of -2 to signify the end of the transaction
    When the transaction is complete, the sound card will play the sound frames.
    """

    def start(self) -> None:
        """
        This method starts the sound card.
        Returns:

        """
        threading.Thread(target=self.process_buses, name=self.device_id + "::process_buses").start()

    def __init__(self, starting_address: int, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus,
                 interrupt_bus: InterruptBus):
        super().__init__(starting_address, 1, address_bus, data_bus, control_bus, interrupt_bus)
        self.__command_queue = queue.Queue()
        self.__processing_queue: bool = False

    @property
    def command_queue(self) -> queue.Queue:
        return self.__command_queue

    @command_queue.setter
    def command_queue(self, value: queue.Queue):
        self.__command_queue = value

    @property
    def processing_queue(self) -> bool:
        return self.__processing_queue

    @processing_queue.setter
    def processing_queue(self, value: bool):
        self.__processing_queue = value

    def process_buses(self) -> None:
        """
        Initializes the sound card and starts the main loop.
        Returns:

        """
        pygame.mixer.init()
        self.main_loop()
        self.wait_until_queue_is_empty()
        self.finished = True

    def main_loop(self) -> None:
        """
        The main loop of the sound card.  This runs continuously to monitor for sound requests.
        The loop ends when the sound card is halted.
        Returns:

        """
        while self.running:
            queue_changed: bool = False
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                if self.address_is_valid(self.address_bus):
                    if self.control_bus.write_request:
                        self.command_queue.put(self.data_bus.data)
                        queue_changed = True
                        self.control_bus.write_request = False
                        self.control_bus.response = True
            self.control_bus.unlock_bus()
            if queue_changed:
                # run process_queue on new thread if not already running
                if not self.processing_queue:
                    threading.Thread(target=self.process_queue, name=self.device_id + "::process_queue").start()

    def process_queue(self) -> None:
        """
        This method processes the command queue.
        Returns:

        """
        self.processing_queue = True

        while not self.command_queue.empty():
            while not self.complete_transaction_is_ready():
                time.sleep(0.05)
            transaction = []
            # copy transaction to new queue
            transaction_queue = queue.Queue()
            queue_byte = self.command_queue.get()
            while queue_byte != END_OF_TRANSACTION:
                transaction_queue.put(queue_byte)
                queue_byte = self.command_queue.get()
            while complete_frame_is_ready(transaction_queue):
                frame_sounds = build_sounds_from_queue(transaction_queue)
                transaction.append(frame_sounds)

            for frame_sounds in transaction:
                play_sounds(frame_sounds)
            time.sleep(0)
        self.processing_queue = False

    def wait_until_queue_is_empty(self) -> None:
        """
        This method waits until the command queue is empty.
        Returns:

        """
        while self.processing_queue:
            time.sleep(0.05)

    def complete_transaction_is_ready(self) -> bool:
        """
        This method checks the command queue for a complete transaction to play.
        A transaction is complete when -2 is found in the queue.
        """
        queue_end_index = len(self.command_queue.queue)
        for i in range(queue_end_index):
            if self.command_queue.queue[i] == END_OF_TRANSACTION:
                return True
        return False
