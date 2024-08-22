from Compiler.class_rubbish_compiler import RubbishCompiler
from Machine.Devices.IO.class_console import Console
from Machine.Devices.Memory.class_ram import RAM
from Machine.Devices.Memory.class_rom import ROM
from Machine.Devices.Processors.class_processor import Processor
from Machine.Backplane.class_backplane import BackPlane
from Machine.Devices.IO.class_soundcard import SoundCard

device_group = []


# This class is instantiated by the entry point.
# This class creates an instance of the backplane.
# This class creates instances of each device and attaches them to the backplane.
# This class then returns an outfitted machine to the entry point, where the machine is started.


class MachineBuilder:
    """
    A class used to build a machine.
    """

    def __init__(self, devices=None) -> None:
        """
        Constructs all the necessary attributes for the machine builder.

        Parameters:
        devices (list): The devices to be added to the machine.
        """
        self.__backplane = BackPlane()
        self.__device_group = devices

    def build_machine(self) -> BackPlane:
        """
        Builds the machine and returns the outfitted backplane.

        Returns:
        BackPlane: The outfitted backplane of the machine.
        """
        for device in self.__device_group:
            self.check_device_overlap(device)
            self.attach_device(device)
        return self.__backplane

    def check_device_overlap(self, device: {}) -> bool:
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

            for check_device in self.__device_group:
                if device is check_device:  # don't check yourself
                    continue
                if 'address' in check_device:
                    check_device_memory_start = int(check_device['address'])
                    check_device_memory_end = check_device_memory_start
                    if 'size' in check_device:
                        check_device_memory_end += int(check_device['size']) - 1
                    if (device_memory_start <= check_device_memory_end
                            and check_device_memory_start <= device_memory_end):
                        print(f"Warning: {device['device_name']} overlaps with {check_device['device_name']}")
                        return True
                    else:
                        return False

    def attach_device(self, device: {}) -> None:
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
                self.__backplane.add_device(RAM(starting_address=address,
                                                size=size,
                                                address_bus=self.__backplane.address_bus,
                                                data_bus=self.__backplane.data_bus,
                                                control_bus=self.__backplane.control_bus,
                                                interrupt_bus=self.__backplane.interrupt_bus))
            case 'processor':
                self.__backplane.add_device(Processor(size=size,
                                                      starting_address=address,
                                                      address_bus=self.__backplane.address_bus,
                                                      data_bus=self.__backplane.data_bus,
                                                      control_bus=self.__backplane.control_bus,
                                                      interrupt_bus=self.__backplane.interrupt_bus))
            case 'console':
                self.__backplane.add_device(Console(starting_address=address,
                                                    width=width,
                                                    height=height,
                                                    interrupt_number=interrupt,
                                                    address_bus=self.__backplane.address_bus,
                                                    data_bus=self.__backplane.data_bus,
                                                    control_bus=self.__backplane.control_bus,
                                                    interrupt_bus=self.__backplane.interrupt_bus))
            case 'soundcard':
                self.__backplane.add_device(SoundCard(starting_address=address,
                                                      address_bus=self.__backplane.address_bus,
                                                      data_bus=self.__backplane.data_bus,
                                                      control_bus=self.__backplane.control_bus,
                                                      interrupt_bus=self.__backplane.interrupt_bus))
            case 'rom':
                self.__backplane.add_device(ROM(starting_address=address,
                                                address_bus=self.__backplane.address_bus,
                                                data_bus=self.__backplane.data_bus,
                                                control_bus=self.__backplane.control_bus,
                                                interrupt_bus=self.__backplane.interrupt_bus))
            case 'compiler':
                compiler = RubbishCompiler(starting_address=address)
                code = compiler.compile(program_pathname)
                if len(code) > size:
                    print("Warning: The compiled program size exceeds the specified size.")
                ram = RAM(starting_address=address,
                          size=size,
                          address_bus=self.__backplane.address_bus,
                          data_bus=self.__backplane.data_bus,
                          control_bus=self.__backplane.control_bus,
                          interrupt_bus=self.__backplane.interrupt_bus)
                ram.load_data(data=code)
                self.__backplane.add_device(ram)

            case _:
                print(f"Device {device_to_add} not found.")

    @staticmethod
    def read_file(filename: str):
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
