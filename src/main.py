#  Copyright (c) 2024 Kyle D. Ross.  All rights reserved.
#  Refer to LICENSE.txt for license information.

import sys

# change

# This is the entry point into the emulator.
# This entry point will create an instance of the machine builder.
# The machine builder will return an instance of the backplane with all devices attached.
# This entry point will start the backplane.
# The backplane will begin iterating through each attached device and calling the Cycle method.

def intro():
    print("RubbishPy")
    print("Version 1.0")
    print("Copyright (c) 2024 Kyle D. Ross")
    print()
    print("Dedicated to my wife, Amy. (lylt)")
    print()
    print("--help for help")
    print()
    print("Session started.")
    print()


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
            builder = MachineBuilder(parse_command_line_arguments())
            builder.build_machine().run()
        else:
            show_help()


def parse_command_line_arguments():
    """Parses the command line arguments and returns a list of device groups.  Each device group is a dictionary"""
    device_groups = []
    import argparse

    # Create an argument parser
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('--help', action='store_const', const=True)
    parser.add_argument('--ram', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--processor', action='store_const', const=True)
    parser.add_argument('--processor_with_cache', action='store_const', const=True)
    parser.add_argument('--debugger', action='store_const', const=True)
    parser.add_argument('--console', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--consolev2', type=lambda x: x.split('='), nargs='+')
    parser.add_argument('--consolev3', type=lambda x: x.split('='), nargs='+')
    parser.add_argument("--compiler", type=lambda x: x.split('='), nargs='+')
    parser.add_argument("--display", type=lambda x: x.split('='), nargs='+')
    # Parse the command-line arguments
    args = parser.parse_args()
    print("Command line arguments:")
    print(' '.join(sys.argv))
    print()
    if args.help:
        show_help()
        exit()

    if args.processor:
        device_groups.append({'device_name': 'processor', 'options': ''})
    if args.processor_with_cache:
        device_groups.append({'device_name': 'processor_with_cache', 'options': ''})
    if args.debugger:
        device_groups.append({'device_name': 'debugger'})
    if args.ram:
        ram_args = dict(args.ram)
        address = ram_args.get("address")
        size = ram_args.get("size")
        device_groups.append({'device_name': 'ram', 'address': address, 'size': size})
    if args.console:
        console_args = dict(args.console)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        device_groups.append({'device_name': 'console', 'address': address, 'interrupt': interrupt})

    if args.consolev2:
        console_args = dict(args.consolev2)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        device_groups.append({'device_name': 'consolev2', 'address': address, 'interrupt': interrupt})

    if args.consolev3:
        console_args = dict(args.consolev3)
        address = console_args.get("address")
        interrupt = console_args.get("interrupt")
        width = console_args.get("width")
        height = console_args.get("height")
        device_groups.append({'device_name': 'consolev3', 'address': address, 'interrupt': interrupt, 'width': width, 'height': height})

    if args.display:
        display_args = dict(args.display)
        address = display_args.get("address")
        width = 80
        height = 25
        if "width" in display_args:
            width = display_args.get("width")
        if "height" in display_args:
            height = display_args.get("height")
        device_groups.append({'device_name': 'display', 'address': address, 'width': width, 'height': height})

    if args.compiler:
        compiler_args = dict(args.compiler)
        address = compiler_args.get("address")
        program = compiler_args.get("program")
        size = compiler_args.get("size")
        device_groups.append({'device_name': 'compiler', 'address': address, 'program': program, 'size': size})

    # Print the device groups
    for device_group in device_groups:
        print(device_group)

    return device_groups


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
