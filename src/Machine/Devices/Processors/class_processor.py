import threading
from datetime import datetime
from time import sleep

from Constants.class_compare_results import CompareResults
from Constants.class_instruction_set import InstructionSet
from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_processor import BaseProcessor


class Processor(BaseProcessor):

    def __init__(self, starting_address: int, size: int, address_bus: AddressBus, data_bus: DataBus,
                 control_bus: ControlBus, interrupt_bus: InterruptBus):

        super().__init__(starting_address, size, address_bus, data_bus,
                         control_bus, interrupt_bus)
        # flow control
        self.instruction_pointer: int = 0
        self.instruction_pointer_stack: list[int] = []
        self.interrupt_vectors: dict[int, int] = {}
        self.handling_interrupt: bool = False
        self.interrupt_instruction_pointer_stack_depth: int = 0
        self.processor_raised_interrupt: int = 0  # the interrupt number that the processor raised via INT instruction
        self.sleeping: bool = False
        self.sleep_mode: bool = False

        # data
        self.registers: list[int] = []
        self.register_stack: list[list[int]] = []
        self.user_stack: list[int] = []
        self.data_cache: dict[int, int] = {}
        self.compare_result: CompareResults = CompareResults.Inconclusive
        self.cache_enabled: bool = True

    def reset_processor(self):
        self.instruction_pointer = 0
        self.registers = [0] * 8
        self.register_stack = []
        self.sleeping = False
        self.sleep_mode = False
        self.compare_result = CompareResults.Inconclusive
        self.user_stack = []

    def start(self) -> None:

        """
        This method starts the processor.
        Returns:

        """
        threading.Thread(target=self.main_loop, name=self.device_id + "::process_cycle").start()

    def main_loop(self) -> None:
        self.reset_processor()
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            power_is_on: bool = self.control_bus.power_on
            self.control_bus.unlock_bus()
            if power_is_on:
                self.process_interrupts()
                if not self.sleeping:
                    try:
                        self.perform_instruction_processing()
                    except Exception as e:
                        print(f"Exception caught: {e}")
                        print(f"Instruction Pointer: {self.instruction_pointer}")
                        print(f"Registers: {self.registers}")
                        self.control_bus.lock_bus()
                        self.interrupt_bus.set_interrupt(Interrupts.halt)
                        self.control_bus.unlock_bus()
            self.finished = True

    def get_value_from_address(self, address: int, cacheable: bool = False):
        """
        This function retrieves data from the specified address.
        It can optionally cache the data for future use.

        Args:
            address (int): The memory address from which to retrieve the data.
            cacheable (bool, optional): If True, the retrieved data will be cached for future use.
            Defaults to False.

        Returns:
            int: The retrieved data.

        Note:
            - If `cacheable` is True and the requested address is already present in the cache,
                the data will be retrieved from the cache.
            - If `cacheable` is True and the requested address is not present in the cache,
                the data will be retrieved from the memory and then cached for future use.
            - If `cacheable` is False, the data will always be retrieved from the memory.
        """
        if self.cache_enabled and cacheable:
            if address in self.data_cache:
                return self.data_cache[address]
        self.control_bus.lock_bus()
        self.address_bus.address = address
        self.control_bus.read_request = True
        self.control_bus.unlock_bus()
        while not self.control_bus.response and self.control_bus.power_on:
            sleep(0)
        self.control_bus.lock_bus()
        value: int = self.data_bus.data
        self.control_bus.response = False
        self.control_bus.unlock_bus()
        if self.cache_enabled and cacheable:
            self.data_cache[address] = value
        else:
            self.data_cache.pop(address, None)
        return value

    def send_value_to_address(self, address: int, value: int, cacheable: bool = False):
        """
        Sends a value to a given address.

        Args:
            address: The address to send the value to.
            value: The value to send.
            cacheable: Boolean indicating whether the value can be cached.
            Default is False.
        """
        if self.cache_enabled and cacheable:
            self.data_cache[address] = value
        else:
            self.data_cache.pop(address, None)
        while self.control_bus.read_request or self.control_bus.write_request:
            sleep(0)
        self.control_bus.lock_bus()
        self.address_bus.address = address
        self.data_bus.data = value
        self.control_bus.write_request = True
        self.control_bus.unlock_bus()
        while not self.control_bus.response and self.control_bus.power_on:
            sleep(0)
        self.control_bus.response = False            

    def perform_instruction_processing(self) -> None:
        instruction: int = self.get_value_from_address(
            self.instruction_pointer, cacheable=True)

        match instruction:
            case InstructionSet.NOP:
                self.instruction_pointer += 1
            case InstructionSet.LR:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                value: int = self.get_value_from_address(
                    self.instruction_pointer + 2, cacheable=True)
                self.registers[destination_register] = value
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()
                self.instruction_pointer += 3
            case InstructionSet.LRM:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                value: int = self.get_value_from_address(
                    self.convert_register_pointer_if_necessary(
                        self.get_value_from_address(self.instruction_pointer + 2)))
                self.registers[destination_register] = value
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()
                self.instruction_pointer += 3
            case InstructionSet.LRR:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                source_register: int = self.get_value_from_address(
                    self.instruction_pointer + 2, cacheable=True)
                self.registers[destination_register] = self.registers[source_register]
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()
                self.instruction_pointer += 3
            case InstructionSet.MRM:
                source_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                address = self.convert_register_pointer_if_necessary(
                    self.get_value_from_address(
                        self.instruction_pointer + 2, cacheable=True))
                self.send_value_to_address(address, self.registers[source_register])
                self.instruction_pointer += 3
            case InstructionSet.ADD:
                self.registers[3] = self.registers[1] + self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.SUB:
                self.registers[3] = self.registers[1] - self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.MUL:
                self.registers[3] = self.registers[1] * self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.DIV:
                self.registers[3] = self.registers[1] // self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.HALT:
                self.control_bus.lock_bus()
                self.interrupt_bus.set_interrupt(Interrupts.halt)
                self.control_bus.unlock_bus()
                self.instruction_pointer += 1
            case InstructionSet.DEBUG:
                print(f"Processor: Debug instruction encountered at {datetime.now().strftime('%H:%M:%S')}")
                print("Current registers:")
                print(self.registers)
                self.instruction_pointer += 1
            case InstructionSet.JMP:
                destination_address: int = self.convert_register_pointer_if_necessary(
                    self.get_value_from_address(self.instruction_pointer + 1, cacheable=True))
                self.instruction_pointer = destination_address
            case InstructionSet.RST:
                self.reset_processor()
            case InstructionSet.CMP:
                # no longer necessary, as any change to registers 1 or 2 will trigger an automatic compare
                self.instruction_pointer += 1
            case InstructionSet.JE:
                if self.compare_result == CompareResults.Equal:
                    destination_address: int = self.convert_register_pointer_if_necessary(
                        self.get_value_from_address(
                            self.instruction_pointer + 1, cacheable=True))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JNE:
                if self.compare_result != CompareResults.Equal:
                    destination_address: int = self.convert_register_pointer_if_necessary(
                        self.get_value_from_address(
                            self.instruction_pointer + 1, cacheable=True))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JL:
                if self.compare_result == CompareResults.LessThan:
                    destination_address: int = self.convert_register_pointer_if_necessary(
                        self.get_value_from_address(
                            self.instruction_pointer + 1, cacheable=True))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JG:
                if self.compare_result == CompareResults.GreaterThan:
                    destination_address: int = self.convert_register_pointer_if_necessary(
                        self.get_value_from_address(
                            self.instruction_pointer + 1, cacheable=True))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.PUSH:
                source_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.user_stack.append(self.registers[source_register])
                self.instruction_pointer += 2
            case InstructionSet.POP:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.registers[destination_register] = self.user_stack.pop()
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()                
                self.instruction_pointer += 2
            case InstructionSet.CALL:
                destination_address: int = self.convert_register_pointer_if_necessary(
                    self.get_value_from_address(self.instruction_pointer + 1, cacheable=True))
                self.instruction_pointer += 2  # address of next instruction after call
                self.execute_call(destination_address)
            case InstructionSet.RTN:
                self.registers = self.register_stack.pop()
                self.perform_register_compare()                
                self.instruction_pointer = self.instruction_pointer_stack.pop()
                if len(self.instruction_pointer_stack) == 0:
                    self.sleeping = self.sleep_mode
                if self.handling_interrupt:
                    # we remembered how deep into the instruction pointer stack we were when the interrupt was raised.
                    # if we are back to that point, the interrupt has been handled. we can now handle another
                    # interrupt by clearing the handling_interrupt flag
                    if self.interrupt_instruction_pointer_stack_depth == len(self.instruction_pointer_stack):
                        self.handling_interrupt = False
            case InstructionSet.NOT:
                self.registers[3] = ~self.registers[1]
                self.instruction_pointer += 1
            case InstructionSet.OR:
                self.registers[3] = self.registers[1] | self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.AND:
                self.registers[3] = self.registers[1] & self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.XOR:
                self.registers[3] = self.registers[1] ^ self.registers[2]
                self.instruction_pointer += 1
            case InstructionSet.SIV:
                interrupt_number: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                destination_address: int = self.convert_register_pointer_if_necessary(
                    self.get_value_from_address(
                        self.instruction_pointer + 2, cacheable=True))
                self.interrupt_vectors[interrupt_number] = destination_address
                self.instruction_pointer += 3
            case InstructionSet.INC:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.registers[destination_register] += 1
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()                
                self.instruction_pointer += 2
            case InstructionSet.DEC:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.registers[destination_register] -= 1
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()               
                self.instruction_pointer += 2
            case InstructionSet.SLEEP:
                self.sleep_mode = True
                self.sleeping = True
                self.instruction_pointer += 1
            case InstructionSet.WAKE:
                self.sleep_mode = False
                self.sleeping = False
                self.instruction_pointer += 1
            case InstructionSet.PEEK:
                destination_register: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.registers[destination_register] = self.user_stack[-1]
                if destination_register == 1 or destination_register == 2:
                    self.perform_register_compare()                
                self.instruction_pointer += 2
            case InstructionSet.INT:
                interrupt_number: int = self.get_value_from_address(
                    self.instruction_pointer + 1, cacheable=True)
                self.processor_raised_interrupt = interrupt_number
                self.interrupt_bus.set_interrupt(interrupt_number)
                self.instruction_pointer += 2

            case _:
                # Raise an error for unknown instruction
                raise ValueError(
                    f"Unknown instruction encountered at address {self.instruction_pointer}. Opcode is {instruction}")

    def perform_register_compare(self):
        if self.registers[1] < self.registers[2]:
            self.compare_result = CompareResults.LessThan
        elif self.registers[1] > self.registers[2]:
            self.compare_result = CompareResults.GreaterThan
        else:
            self.compare_result = CompareResults.Equal

    def execute_call(self, destination_address):
        self.register_stack.append(self.registers.copy())
        self.instruction_pointer_stack.append(self.instruction_pointer)
        self.instruction_pointer = destination_address

    def process_interrupts(self):
        if not self.handling_interrupt:
            self.control_bus.lock_bus()
            interrupt_number = self.interrupt_bus.interrupt_awaiting()
            self.control_bus.unlock_bus()
            if interrupt_number in self.interrupt_vectors:
                if interrupt_number == self.processor_raised_interrupt:
                    self.interrupt_bus.clear_interrupt(interrupt_number)
                    self.processor_raised_interrupt = 0
                destination_address = self.interrupt_vectors[interrupt_number]
                self.sleeping = False
                self.handling_interrupt = True
                self.interrupt_instruction_pointer_stack_depth = len(self.instruction_pointer_stack)
                self.execute_call(destination_address)

    def convert_register_pointer_if_necessary(self, address: int) -> int:
        if address < 0:
            address = abs(address)
            return self.registers[address]
        return address
