#  Copyright (c) 2024. Kyle D. Ross.
#  Refer to LICENSE.txt for license information.

import os
import time

from Machine.Devices.Bases.class_base_device import BaseDevice
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Constants.class_interrupts import Interrupts


class BackPlane:
    """
    A class used to represent a BackPlane.

    ...

    Attributes
    ----------
    _devices : list
        a list to store the devices connected to the backplane
    _addressBus : AddressBus
        the address bus of the backplane
    _dataBus : DataBus
        the data bus of the backplane
    _controlBus : ControlBus
        the control bus of the backplane
    _interruptBus : InterruptBus
        the interrupt bus of the backplane

    Methods
    -------
    __init__():
        Constructs all the necessary attributes for the backplane.
    add_device(device):
        Adds a device to the backplane.
    run():
        Runs the backplane.
    """

    _devices = []
    _addressBus: AddressBus = None
    _dataBus: DataBus = None
    _controlBus: ControlBus = None
    _interruptBus: InterruptBus = None

    def __init__(self):
        """
        Constructs all the necessary attributes for the backplane.
        """
        self._addressBus = AddressBus()
        self._controlBus = ControlBus()
        self._dataBus = DataBus(self._controlBus)
        self._interruptBus = InterruptBus()

    def add_device(self, device: BaseDevice):
        """
        Adds a device to the backplane.

        Parameters:
            device (BaseDevice): The device to be added to the backplane.
        """
        self._devices.append(device)

    def run(self):
        """
        Runs the backplane.
        The backplane runs in an infinite loop, cycling through all the devices
        connected to it.  When a HALT interrupt is detected, the emulator
        is terminated.

        Raises:
            SystemExit: If the HALT interrupt is detected.
        """
        loop_counter = 0
        start_time = time.time()
        while True:
            loop_counter += 1
            for device in self._devices:
                device.cycle(self._addressBus, self._dataBus, self._controlBus, self._interruptBus)
                if self._interruptBus.test_interrupt(Interrupts.halt):
                    print("HALT interrupt detected.")
                    # noinspection PyProtectedMember,PyUnresolvedReferences
                    os._exit(0)
                if loop_counter == 500000:
                    end_time = time.time()
                    speed = loop_counter / (end_time - start_time)
                    print(f"{(speed / 1000):.0f} kHz")
                    start_time = time.time()
                    loop_counter = 0
