# lylt <3

import sys
from typing import List


def intro() -> None:
    print("RubbishPy")
    print("Copyright (c) 2024 Kyle D. Ross")
    print("--help for help")
    print()
    print("Session started.")


def check_python_version() -> bool:
    """Checks the python version.  Returns True if the version is 3.10 or greater.  Returns False otherwise."""
    if sys.version_info < (3, 11):
        print("Python 3.11 or greater is required.")
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
    Adds a sound card device to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    if args.soundcard:
        soundcard_args = dict(args.soundcard)
        address = soundcard_args.get("address")
        # noinspection SpellCheckingInspection
        check_required_parameters("Soundcard", soundcard_args, ["address"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'soundcard', 'address': address})


def parse_command_line() -> {}:
    """Parses the command line arguments and returns a list of device groups.  Each device group is a dictionary"""
    devices = []
    import argparse

    # Create an argument parser
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--help', action='store_const', const=True)
    parser.add_argument('--ram', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--processor', action='store_const', const=True)
    parser.add_argument('--console', type=lambda x: x.split('='), nargs='+')
    parser.add_argument("--compiler", type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--soundcard', type=lambda x: x.split('='), nargs='+')

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
    return devices


def add_compiler(args, devices: {}) -> None:
    """
    Adds a RAM device to the list of devices to add to the backplane, and loads it with a compiled program.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    if args.compiler:
        compiler_args = dict(args.compiler)
        address = compiler_args.get("address")
        program = compiler_args.get("program")
        size = compiler_args.get("size")
        check_required_parameters("Compiler", compiler_args, ["address", "program", "size"])
        devices.append({'device_name': 'compiler', 'address': address, 'program': program, 'size': size})


def add_console(args, devices: {}) -> None:
    """
    Adds a console device to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    if args.console:
        console_args = dict(args.console)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        # noinspection SpellCheckingInspection
        check_required_parameters("Console", console_args, ["address", "interrupt", "width", "height"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'console', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


def add_ram(args, devices: {}) -> None:
    """
    Adds a RAM device to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    if args.ram:
        ram_args = dict(args.ram)
        address = ram_args.get("address")
        size = ram_args.get("size")
        check_required_parameters("RAM", ram_args, ["address", "size"])
        devices.append({'device_name': 'ram', 'address': address, 'size': size})


def add_processor(args, devices: {}) -> None:
    """
    Adds a processor device to the list of devices to add to the backplane.
    Args:
        args: The command line arguments.
        devices: The list of devices that will be added to the machine.

    Returns:

    """
    if args.processor:
        devices.append({'device_name': 'processor', 'options': ''})

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
    print("         --console address=1024 interrupt=2")
    print()
    print("   Note:  Console's size is always 1 and can't be changed.")
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
