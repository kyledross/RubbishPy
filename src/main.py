# lylt <3

import sys
from typing import List

# hello

def intro() -> None:
    print("RubbishPy")
    print("Copyright (c) 2025 Kyle D. Ross")
    print("--help for help")
    print()
    print("Session started.")


def check_python_version() -> bool:
    """Checks the python version.  Returns True if the version is 3.10 or greater.  Returns False otherwise."""
    if sys.version_info < (3, 10):
        print("Python 3.10 or greater is required.")
        return False
    return True


def start_machine() -> None:
    """Starts the machine.  This is the entry point into the emulator."""
    intro()
    if check_python_version():
        if len(sys.argv) > 1:

            from MachineConfiguration.class_machine_builder import MachineBuilder
            builder = MachineBuilder(parse_command_line())
            builder.build_machine().run()
        else:
            show_help()
    print("Session ended.")


def check_required_parameters(device: str, parameters: {str}, keys: List[str]):
    """
    Checks if any of the specified keys are None in the "parameters" dictionary.

    Parameters:
    parameters (dict): The dictionary of parameters to check.
    keys (list): The list of keys to check in the "parameters" dictionary.
    """
    for key in keys:
        if parameters.get(key) is None:
            print(f"Error: The {device} device requires {key} to be specified.")
            print("Use --help for help.")
            exit(1)


# noinspection SpellCheckingInspection
def add_sound_card(args, devices: {}) -> None:
    """
    Adds one or more sound card devices to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    device_type = 'soundcard'
    # Handle the unnumbered argument
    if hasattr(args, device_type) and getattr(args, device_type) is not None:
        soundcard_args = dict(getattr(args, device_type))
        address = soundcard_args.get("address")
        check_required_parameters("Soundcard", soundcard_args, ["address"])
        devices.append({'device_name': device_type, 'address': address})

    # Handle the numbered arguments
    for i in range(1, 11):
        device_attr_name = f'{device_type}{i}'
        if hasattr(args, device_attr_name) and getattr(args, device_attr_name) is not None:
            soundcard_args = dict(getattr(args, device_attr_name))
            address = soundcard_args.get("address")
            check_required_parameters("Soundcard", soundcard_args, ["address"])
            devices.append({'device_name': device_type, 'address': address})


def add_rtc(args, devices):
    device_type = 'rtc'
    # Handle the unnumbered argument
    if hasattr(args, device_type) and getattr(args, device_type) is not None:
        rtc_args = dict(getattr(args, device_type))
        address = rtc_args.get("address")
        interrupt = rtc_args.get("interrupt")
        check_required_parameters("RTC", rtc_args, ["address", "interrupt"])
        devices.append({'device_name': device_type, 'address': address, 'interrupt': interrupt})

    # Handle the numbered arguments
    for i in range(1, 11):
        device_attr_name = f'{device_type}{i}'
        if hasattr(args, device_attr_name) and getattr(args, device_attr_name) is not None:
            rtc_args = dict(getattr(args, device_attr_name))
            address = rtc_args.get("address")
            interrupt = rtc_args.get("interrupt")
            check_required_parameters("RTC", rtc_args, ["address", "interrupt"])
            devices.append({'device_name': device_type, 'address': address, 'interrupt': interrupt})

def parse_command_line() -> {}:
    """Parses the command line arguments and returns a list of device groups. Each device group is a dictionary"""
    devices = []
    import argparse

    # Create an argument parser
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--help', action='store_const', const=True)

    # Add arguments for each device type, including numbered versions
    device_types = ['ram', 'processor', 'console', 'compiler', 'soundcard', 'rtc']
    for device_type in device_types:
        parser.add_argument(f'--{device_type}', type=lambda x: x.split('='), nargs='*')
        for i in range(1, 11):  # Add up to 10 numbered instances
            parser.add_argument(f'--{device_type}{i}', type=lambda x: x.split('='), nargs='*')

    args = parser.parse_args()
    if args.help:
        show_help()
        exit()

    # build the devices list to pass to the machine builder
    add_processor(args, devices)
    add_ram(args, devices)
    add_console(args, devices)
    add_compiler(args, devices)
    add_sound_card(args, devices)
    add_rtc(args, devices)
    return devices


def add_compiler(args, devices: {}) -> None:
    """
    Adds one or more compiler devices to the list of devices to add to the backplane, and loads it with a compiled program.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    device_type = 'compiler'
    # Handle the unnumbered argument
    if hasattr(args, device_type) and getattr(args, device_type) is not None:
        compiler_args = dict(getattr(args, device_type))
        address = compiler_args.get("address")
        program = compiler_args.get("program")
        size = compiler_args.get("size")
        check_required_parameters("Compiler", compiler_args, ["address", "program", "size"])
        devices.append({'device_name': device_type, 'address': address, 'program': program, 'size': size})

    # Handle the numbered arguments
    for i in range(1, 11):
        device_attr_name = f'{device_type}{i}'
        if hasattr(args, device_attr_name) and getattr(args, device_attr_name) is not None:
            compiler_args = dict(getattr(args, device_attr_name))
            address = compiler_args.get("address")
            program = compiler_args.get("program")
            size = compiler_args.get("size")
            check_required_parameters("Compiler", compiler_args, ["address", "program", "size"])
            devices.append({'device_name': device_type, 'address': address, 'program': program, 'size': size})


def add_console(args, devices: {}) -> None:
    """
    Adds one or more console devices to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    device_type = 'console'
    # Handle the unnumbered argument
    if hasattr(args, device_type) and getattr(args, device_type) is not None:
        console_args = dict(getattr(args, device_type))
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        check_required_parameters("Console", console_args, ["address", "interrupt", "width", "height"])
        devices.append({'device_name': device_type, 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})

    # Handle the numbered arguments
    for i in range(1, 11):
        device_attr_name = f'{device_type}{i}'
        if hasattr(args, device_attr_name) and getattr(args, device_attr_name) is not None:
            console_args = dict(getattr(args, device_attr_name))
            address = console_args.get("address")
            interrupt = console_args.get("interrupt")
            width = console_args.get("width")
            height = console_args.get("height")
            check_required_parameters("Console", console_args, ["address", "interrupt", "width", "height"])
            devices.append({'device_name': device_type, 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


def add_ram(args, devices: {}) -> None:
    """
    Adds one or more RAM devices to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    device_type = 'ram'
    # Handle the unnumbered argument
    if hasattr(args, device_type) and getattr(args, device_type) is not None:
        ram_args = dict(getattr(args, device_type))
        address = ram_args.get("address")
        size = ram_args.get("size")
        check_required_parameters("RAM", ram_args, ["address", "size"])
        devices.append({'device_name': device_type, 'address': address, 'size': size})

    # Handle the numbered arguments
    for i in range(1, 11):
        device_attr_name = f'{device_type}{i}'
        if hasattr(args, device_attr_name) and getattr(args, device_attr_name) is not None:
            ram_args = dict(getattr(args, device_attr_name))
            address = ram_args.get("address")
            size = ram_args.get("size")
            check_required_parameters("RAM", ram_args, ["address", "size"])
            devices.append({'device_name': device_type, 'address': address, 'size': size})


def add_processor(args, devices: {}) -> None:
    """
    Adds one or more processor devices to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    # Add the default processor if it exists
    if hasattr(args, 'processor') and args.processor is not None:
        processor_args = dict(args.processor) if args.processor else {'address': '0'}
        address = processor_args.get('address', '0')
        devices.append({'device_name': 'processor', 'address': address, 'options': ''})

    # Loop through potential numbered processors
    for i in range(1, 11):  # Check for processors 1 through 10
        processor_attr_name = f'processor{i}'
        if hasattr(args, processor_attr_name) and getattr(args, processor_attr_name) is not None:
            processor_args = dict(getattr(args, processor_attr_name)) if getattr(args, processor_attr_name) else {'address': '0'}
            address = processor_args.get('address', '0')
            devices.append({'device_name': 'processor', 'address': address, 'options': ''})

def show_help() -> None:
    """Displays the help screen."""
    print("Commands:")
    print()
    print("--ram")
    print("   Adds a RAM device to the backplane.")
    print()
    print("   Syntax:")
    print("         --ram address={starting address} size={size of ram address space}")
    print()
    print("   Example:")
    print("         --ram address=0 size=1024")
    print()
    print("--console")
    print("   Adds a console device to the backplane which accepts keystrokes and displays output.")
    print()
    print("   Syntax:")
    print("         --console address={starting address} interrupt={interrupt to be raised upon keystroke}")
    print("           width={width of console} height={height of console}")
    print()
    print("   Example:")
    print("         --console address=1024 interrupt=2 --width=80 --height=24")
    print()
    print("   Note:  Console's memory size is always 1 and can't be changed.")
    print()
    print("--processor")
    print("   Adds a processor device to the backplane.")
    print()
    print("   Syntax:")
    print("         --processor")
    print()
    print("   Example:")
    print("         --processor")
    print()
    print("   Note: The processor always begins execution at address 0.")
    print()
    print("--compiler")
    print("   Adds a RAM device to the backplane and compiles a Rubbish assembly language program into the")
    print("   address space of the RAM.")
    print()
    print("   Syntax:")
    print("         --compiler address={starting address} size={size of ram address space} "
          "           program={pathname to program}")
    print()
    print("   Example:")
    print("         --compiler address=0 size=2048 program=./my_program.txt")
    print()
    print("--soundcard")
    print("   Adds a sound card device to the backplane.")
    print()
    print("   Syntax:")
    print("         --soundcard address={address}")
    print()
    print("   Example:")
    print("         --soundcard address=1025")
    print()


if __name__ == '__main__':
    """
    This is the entry point into the emulator.
    """
    start_machine()