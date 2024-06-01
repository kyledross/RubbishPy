import queue
import threading
import time

import numpy
from typing import List

import pygame
from pygame.mixer import Sound

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_device import BaseDevice


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
        time.sleep(0.05)


def build_sound(duration_ms: int, frequency: float, volume: float):
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


class SoundCard(BaseDevice):
    """
    A class used to represent a Sound Card device.
    Sounds are played by sending frames to the sound card within a transaction.
    All frames are built and queued up until the transaction is complete.
    After the transaction is complete, the sounds in the queue are played.
    A transaction is ended by sending -1 to the sound card.
    A frame consists of:
        - Integer representing the length of the sound in milliseconds.
        - One or more frames consisting of two integers:
            - The first integer represents the frequency of the sound with two decimal places, packed * 100
              For example, middle C of 261.63Hz would be 26163.
            - The second integer represents the volume of the sound from 0 to 1, packed * 10
        - A final integer of ASCII NULL (0) to signify the end of the sound frame
        - A final integer of -1 to signify the end of the transaction
    When the transaction is complete, the sound card will play the sound frames.
    """

    def start(self):
        # start process_buses thread
        threading.Thread(target=self.process_buses, name=self.get_device_id() + "::process_buses").start()

    def __init__(self, starting_address: int, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus,
                 interrupt_bus: InterruptBus):
        super().__init__(starting_address, 1, address_bus, data_bus, control_bus, interrupt_bus)
        self.__command_queue = queue.Queue()
        self.__processing_queue: bool = False

    def process_buses(self):
        pygame.mixer.init()
        while self.is_running():
            queue_changed: bool = False
            self.control_bus().lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus().is_power_on():
                if self.address_is_valid(self.address_bus()):
                    if self.control_bus().get_write_request():
                        self.__command_queue.put(self.data_bus().get_data())
                        queue_changed = True
                        self.control_bus().set_write_request(False)
                        self.control_bus().set_response(True)
            self.control_bus().unlock_bus()
            if queue_changed:
                # run process_queue on new thread if not already running
                if not self.__processing_queue:
                    threading.Thread(target=self.process_queue, name=self.get_device_id() + "::process_queue").start()
        self.wait_until_queue_is_empty()
        self.set_finished()

    def process_queue(self):
        self.__processing_queue = True
        transaction = []
        while not self.complete_transaction_is_ready():
            time.sleep(0.05)
        while self.complete_frame_is_ready():
            frame_sounds = self.build_sounds_from_queue()
            transaction.append(frame_sounds)

        for frame_sounds in transaction:
            play_sounds(frame_sounds)
        # there should be an end-transaction left on the queue here
        # remove it
        self.__command_queue.get()
        self.__processing_queue = False

    def wait_until_queue_is_empty(self):
        while self.__processing_queue:
            time.sleep(0.05)

    def build_sounds_from_queue(self) -> List[Sound]:
        """
        This method builds sounds from the command queue.
        """
        sounds = []
        # build a list of sounds from the queue
        duration_ms = self.__command_queue.get()
        queue_byte: int
        queue_byte = self.__command_queue.get()
        while queue_byte != 0:
            frequency: float = queue_byte / 100
            volume: float = self.__command_queue.get() / 10
            sound = build_sound(duration_ms, frequency, volume)
            sounds.append(sound)
            queue_byte = self.__command_queue.get()
        return sounds

    def complete_frame_is_ready(self) -> bool:
        """
        This method checks the command queue for a complete command to play.
        """

        # build a list of integers from the queue, without removing them from the queue, just yet.
        # we want to see if a complete frame is in the queue.

        # search the queue from index 0 to the end of the queue, looking for an ASCII NULL.
        # if an ASCII NULL is found, we have a complete frame.
        # if an ASCII NULL is not found, we do not have a complete frame.
        queue_end_index = len(self.__command_queue.queue)
        for i in range(queue_end_index):
            if self.__command_queue.queue[i] == 0:
                return True
        return False

    def complete_transaction_is_ready(self) -> bool:
        """
        This method checks the command queue for a complete transaction to play.
        """

        # build a list of integers from the queue, without removing them from the queue, just yet.
        # we want to see if a complete frame is in the queue.

        # search the queue from index 0 to the end of the queue, looking for an ASCII NULL.
        # if an ASCII NULL is found, we have a complete frame.
        # if an ASCII NULL is not found, we do not have a complete frame.
        queue_end_index = len(self.__command_queue.queue)
        for i in range(queue_end_index):
            if self.__command_queue.queue[i] == -1:
                return True
        return False
