#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

from Compiler.class_rubbish_compiler import RubbishCompiler
from Machine.Devices.IO.class_consolev4 import ConsoleV4
from Machine.Devices.IO.class_consolev2 import ConsoleV2
from Machine.Devices.IO.class_consolev3 import ConsoleV3
from Machine.Devices.IO.class_consolev31 import ConsoleV31
from Machine.Devices.Memory.class_ram import RAM
from Machine.Devices.Memory.class_rom import ROM
from Machine.Devices.Processors.class_processor import Processor
from Machine.Devices.Testers.class_debugger import Debugger
from Machine.Backplane.class_backplane import BackPlane
from Machine.Devices.IO.class_console import Console
from Machine.Devices.IO.class_addressable_text_display import AddressableTextDisplay

device_group = []


# This class is instantiated by the entry point.
# This class creates an instance of the backplane.
# This class creates instances of each device and attaches them to the backplane.
# This class then returns an outfitted machine to the entry point, where the machine is started.


class MachineBuilder:
    """
    A class used to build a machine.

    ...

    Attributes
    ----------
    _backplane : BackPlane
        the backplane of the machine
    device_group : list
        a list to store the devices of the machine

    Methods
    -------
    __init__(devices):
        Constructs all the necessary attributes for the machine builder.
    build_machine():
        Builds the machine and returns the outfitted backplane.
    check_device_overlap(device):
        Checks if a device overlaps with any other device in the machine.
    attach_device(device):
        Attaches a device to the machine.
    """

    def __init__(self, devices=None):
        """
        Constructs all the necessary attributes for the machine builder.

        Parameters:
        devices (list): The devices to be added to the machine.
        """
        self._backplane = BackPlane()
        self.device_group = devices

    def build_machine(self) -> BackPlane:
        """
        Builds the machine and returns the outfitted backplane.

        Returns:
        BackPlane: The outfitted backplane of the machine.
        """
        for device in self.device_group:
            self.check_device_overlap(device)
            self.attach_device(device)
        return self._backplane

    def check_device_overlap(self, device):
        """
        Checks if a device overlaps with any other device in the machine.

        Parameters:
        device (dict): The device to be checked for overlap.

        Returns:
        bool: True if the device overlaps with any other device, True otherwise.
        """
        if 'address' in device:
            device_memory_start = int(device['address'])
            device_memory_end = device_memory_start
            if 'size' in device:
                device_memory_end += int(device['size']) - 1

            for check_device in self.device_group:
                if device is check_device:  # don't check yourself
                    continue
                if 'address' in check_device:
                    check_device_memory_start = int(check_device['address'])
                    check_device_memory_end = check_device_memory_start
                    if 'size' in check_device:
                        # todo: compiler doesn't require a size, but when one isn't supplied, this blows up
                        # plus, since the size isn't known until the compiler finishes the job, we can't check
                        check_device_memory_end += int(check_device['size']) - 1
                    if (device_memory_start <= check_device_memory_end
                            and check_device_memory_start <= device_memory_end):
                        print(f"Warning: {device['device_name']} overlaps with {check_device['device_name']}")
                        return True
                    else:
                        return False

    def attach_device(self, device):
        """
        Attaches a device to the machine.

        Parameters:
        device (dict): The device to be attached to the machine.
        """
        address: int = 0
        size: int = 0
        interrupt: int = 0
        width: int = 0
        height: int = 0
        program_pathname: str = ""
        device_to_add: str = device['device_name']
        if 'address' in device:
            address: int = int(device['address'])
        if 'size' in device:
            size: int = int(device['size'])
        if 'program' in device:
            program_pathname: str = device['program']
        if 'interrupt' in device:
            interrupt: int = int(device['interrupt'])
        if 'width' in device:
            width: int = int(device['width'])
        if 'height' in device:
            height: int = int(device['height'])

        # noinspection SpellCheckingInspection
        match device_to_add:
            case 'ram':
                self._backplane.add_device(RAM(starting_address=address, size=size))
            case 'processor':
                self._backplane.add_device(Processor(size=size, starting_address=address))
            case 'console':
                self._backplane.add_device(Console(starting_address=address, interrupt=interrupt))
            case 'consolev2':
                self._backplane.add_device(ConsoleV2(starting_address=address, interrupt_number=interrupt))
            case 'consolev3':
                self._backplane.add_device(ConsoleV3(starting_address=address, width=width, height=height,
                                                     interrupt_number=interrupt))
            case 'consolev31':
                self._backplane.add_device(ConsoleV31(starting_address=address, width=width, height=height,
                                                      interrupt_number=interrupt))
            case 'consolev4':
                self._backplane.add_device(ConsoleV4(starting_address=address, width=width, height=height,
                                                     interrupt_number=interrupt))

            case 'display':
                self._backplane.add_device(AddressableTextDisplay(starting_address=address, width=width, height=height))
            case 'rom':
                self._backplane.add_device(ROM(starting_address=address))
            case 'compiler':
                compiler = RubbishCompiler(address=address)
                code = compiler.compile(program_pathname)
                if len(code) > size:
                    print("Warning: The compiled program size exceeds the specified size.")
                ram = RAM(starting_address=address, size=size)
                ram.load_data(data=code)
                self._backplane.add_device(ram)
            case 'debugger':
                self._backplane.add_device(Debugger())
            case _:
                print(f"Device {device_to_add} not found.")

    @staticmethod
    def read_file(filename):
        """
        Function to read a file and return its contents.

        Parameters:
        filename (str): The name of the file to be read.

        Returns:
        str: The contents of the file.
        """
        with open(filename, 'r') as file:
            contents = file.read()
        return contents
