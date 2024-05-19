#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.md for license information.

# lylt <3

import sys
import warnings


# This is the entry point into the emulator.
# This entry point will create an instance of the machine builder.
# The machine builder will return an instance of the backplane with all devices attached.
# This entry point will start the backplane.
# The backplane will begin iterating through each attached device and calling the Cycle method.

def intro():
    print("RubbishPy")
    print("Version 1.0")
    print("Copyright (c) 2024 Kyle D. Ross")
    print("--help for help")
    print()
    print("Session started.")


def check_python_version():
    """Checks the python version.  Returns True if the version is 3.10 or greater.  Returns False otherwise."""
    if sys.version_info < (3, 10):
        print("Python 3.10 or greater is required.")
        return False
    return True


def start_machine():
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


def check_required_parameters(device: str, parameters, keys):
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
def parse_command_line():
    """Parses the command line arguments and returns a list of device groups.  Each device group is a dictionary"""
    devices = []
    import argparse

    # Create an argument parser
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--help', action='store_const', const=True)
    parser.add_argument('--ram', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--processor', action='store_const', const=True)
    parser.add_argument('--processor_with_cache', action='store_const', const=True)
    parser.add_argument('--debugger', action='store_const', const=True)
    parser.add_argument('--console', type=lambda x: x.split('='), nargs='+')
    # noinspection SpellCheckingInspection
    parser.add_argument('--consolev2', type=lambda x: x.split('='), nargs='+')
    # noinspection SpellCheckingInspection
    parser.add_argument('--consolev3', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--consolev4', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--consolev5', type=lambda x: x.split('='), nargs='+')
    # noinspection SpellCheckingInspection
    parser.add_argument('--consolev31', type=lambda x: x.split('='), nargs='+')
    parser.add_argument("--compiler", type=lambda x: x.split('='), nargs='+')
    parser.add_argument("--display", type=lambda x: x.split('='), nargs='+')

    args = parser.parse_args()
    if args.help:
        show_help()
        exit()

    # build the devices list to pass to the machine builder
    add_processor(args, devices)
    add_processor_with_cache(args, devices)
    add_debugger(args, devices)
    add_ram(args, devices)
    add_console_v1(args, devices)
    add_console_v2(args, devices)
    add_console_v3(args, devices)
    add_console_v31(args, devices)
    add_console_v4(args, devices)
    add_console_v5(args, devices)
    add_addressable_display(args, devices)
    add_compiler(args, devices)
    return devices


def add_compiler(args, devices):
    if args.compiler:
        compiler_args = dict(args.compiler)
        address = compiler_args.get("address")
        program = compiler_args.get("program")
        size = compiler_args.get("size")
        check_required_parameters("Compiler", compiler_args, ["address", "program", "size"])
        devices.append({'device_name': 'compiler', 'address': address, 'program': program, 'size': size})


def add_addressable_display(args, devices):
    if args.display:
        display_args = dict(args.display)
        address = display_args.get("address")
        width = 80
        height = 25
        if "width" in display_args:
            width = display_args.get("width")
        if "height" in display_args:
            height = display_args.get("height")
        check_required_parameters("Display", display_args, ["address"])
        devices.append({'device_name': 'display', 'address': address, 'width': width, 'height': height})


def add_console_v5(args, devices):
    if args.consolev5:
        console_args = dict(args.consolev5)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        # noinspection SpellCheckingInspection
        check_required_parameters("Consolev5", console_args, ["address", "interrupt", "width", "height"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'consolev5', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


# noinspection SpellCheckingInspection
def add_console_v4(args, devices):
    if args.consolev4:
        warnings.warn("The consolev4 device is deprecated.  Use --consolev5 instead.")
        console_args = dict(args.consolev4)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        # noinspection SpellCheckingInspection
        check_required_parameters("Consolev4", console_args, ["address", "interrupt", "width", "height"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'consolev4', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


# noinspection SpellCheckingInspection
def add_console_v31(args, devices):
    if args.consolev31:
        warnings.warn("The consolev31 device is deprecated.  Use --consolev5 instead.")
        console_args = dict(args.consolev31)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        # noinspection SpellCheckingInspection
        check_required_parameters("Consolev31", console_args, ["address", "interrupt", "width", "height"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'consolev31', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


# noinspection SpellCheckingInspection
def add_console_v3(args, devices):
    if args.consolev3:
        warnings.warn("The consolev3 device is deprecated.  Use --consolev5 instead.")
        console_args = dict(args.consolev3)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        # noinspection SpellCheckingInspection
        check_required_parameters("Consolev3", console_args, ["address", "interrupt", "width", "height"])
        # noinspection SpellCheckingInspection
        devices.append(
            {'device_name': 'consolev3', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})


# noinspection SpellCheckingInspection
def add_console_v2(args, devices):
    if args.consolev2:
        warnings.warn("The consolev2 device is deprecated.  Use --consolev5 instead.")
        console_args = dict(args.consolev2)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        # noinspection SpellCheckingInspection
        check_required_parameters("Consolev2", console_args, ["address", "interrupt"])
        # noinspection SpellCheckingInspection
        devices.append({'device_name': 'consolev2', 'address': address, 'interrupt': interrupt})


# noinspection SpellCheckingInspection
def add_console_v1(args, devices):
    if args.console:
        warnings.warn("The console device is deprecated.  Use --consolev5 instead.")
        console_args = dict(args.console)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        check_required_parameters("Console", console_args, ["address", "interrupt"])
        devices.append({'device_name': 'console', 'address': address, 'interrupt': interrupt})


def add_ram(args, devices):
    if args.ram:
        ram_args = dict(args.ram)
        address = ram_args.get("address")
        size = ram_args.get("size")
        check_required_parameters("RAM", ram_args, ["address", "size"])
        devices.append({'device_name': 'ram', 'address': address, 'size': size})


def add_debugger(args, devices):
    if args.debugger:
        devices.append({'device_name': 'debugger'})


def add_processor_with_cache(args, devices):
    if args.processor_with_cache:
        devices.append({'device_name': 'processor_with_cache', 'options': ''})


def add_processor(args, devices):
    if args.processor:
        devices.append({'device_name': 'processor', 'options': ''})


def show_help():
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
    print()
    print("   Example:")
    print("         --console address=1024 interrupt=2")
    print()
    print("   Note:  Console's size is always 1 and can't be changed.")
    print()
    # noinspection SpellCheckingInspection
    print("--consolev2")
    print("   Adds a console device to the backplane which accepts keystrokes and displays output.")
    print()
    print("   Syntax:")
    print("         --console address={starting address} interrupt={interrupt to be raised upon keystroke}")
    print()
    print("   Example:")
    print("         --console address=1024 interrupt=2")
    print()
    print("   Note:  Console's size is always 1 and can't be changed.")
    # noinspection SpellCheckingInspection
    print("          Consolev2 is a newer and more stable version of the console device.")
    print()
    print("--display")
    print("   Adds an 80x25 addressable text display device.")
    print()
    print("   Syntax:")
    print("         --display address={starting address} [width={width of display}] [height={height of display}]")
    print()
    print("   Example:")
    print("         --display address=2048")
    print("         --display address=2048 width=40 height=20")
    print()
    print("   Note:  The display's size is 80x25 by default. Width and height may be specified.")
    print("          The display's memory is linearly addressed with position 0x0 at the starting address.")
    print("          The display is not scrollable.")
    print("          The display occupies [width x height] bytes of address space starting at the specified address.")
    print("          The display memory is readable and writeable.")
    print("          The display does not accept keyboard input.")
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
    print("   address space of the RAM.  The size of the RAM that is added is exactly the size of the compiled")
    print("   program.")
    print()
    print("   Syntax:")
    print("         --compiler address={starting address} size={size of ram address space} "
          "           program={pathname to program}")
    print()
    print("   Example:")
    print("         --compiler address=0 size=2048 program=./my_program.txt")
    print()


if __name__ == '__main__':
    start_machine()
