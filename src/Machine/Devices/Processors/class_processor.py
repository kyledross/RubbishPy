import collections
import threading
from collections import deque

import time

from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_processor import BaseProcessor
from Constants.class_instruction_set import InstructionSet
from Constants.class_compare_results import CompareResults
from Constants.class_interrupts import Interrupts


class Phases:
    """
    The Phases class represents the different phases a processor can be in during its operation.
    It is a static class, meaning it does not need to be instantiated and its members can be accessed directly.
    """
    NothingPending = 0  # The processor has nothing pending.
    AwaitingInstruction = 1  # The processor is awaiting an instruction.
    AwaitingFirstOperand = 2  # The processor is awaiting the first operand.
    AwaitingSecondOperand = 3  # The processor is awaiting the second operand.
    AwaitingResponse = 4  # The processor is awaiting a response.
    # Developer: if a new phase is added, remember to update
    # the Processor class's cycle method in regard to data caching.


def execute_halt(interrupt_bus):
    interrupt_bus.set_interrupt(Interrupts.halt)


# noinspection DuplicatedCode
class Processor(BaseProcessor):

    def __init__(self, starting_address: int, size: int, disable_instruction_caching: bool,
                 address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        # registers
        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self.disable_instruction_caching = disable_instruction_caching
        self.current_instruction: int = -1
        self.data_pointer: int = 0
        self.phase: int = 0
        self.registers = [0] * 8

        # stacks
        self.internal_stack = deque()
        self.general_purpose_stack = deque()
        self.register_stack = deque()
        self.call_stack = deque()
        self.debug_stack = deque()

        # vectors
        self.interrupt_vectors: collections.OrderedDict[int, int] = collections.OrderedDict()

        # flags
        self.compare_result = CompareResults.Equal
        self.interrupt_in_progress = False
        self.sleeping: bool = False
        self.sleep_mode: bool = False

        # instruction caching
        self.instruction_and_operand_cache = {}

        threading.Thread(target=self.process_cycle).start()

    def cycle(self, address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        pass  # todo: remove cycle

    def process_cycle(self):
        while self.is_running():
            time.sleep(0)
            self.stop_running_if_halt_detected()
            if self.control_bus().is_running():
                self.perform_instruction_processing()

    def perform_instruction_processing(self):
        address_bus = self.address_bus()
        control_bus = self.control_bus()
        data_bus = self.data_bus()
        interrupt_bus = self.interrupt_bus()
        self.cache_instruction(address_bus, control_bus, data_bus)
        while True:  # loop until a cached instruction request is not fulfilled
            # Interrupt processing
            if self.phase == Phases.NothingPending:
                if not self.interrupt_in_progress:
                    for interruptBit in range(0, 32):
                        interrupt_number = 2 ** interruptBit
                        if interrupt_bus.test_interrupt(interrupt_number):
                            if interrupt_number in self.interrupt_vectors:
                                self.sleeping = False
                                self.call_stack.append(self.data_pointer)
                                self.data_pointer = self.interrupt_vectors[interrupt_number]
                                self.push_registers()
                                interrupt_bus.clear_interrupt(interrupt_number)
                                self.interrupt_in_progress = True
                                break

            # Instruction routing
            if self.sleeping:
                break
            else:
                match self.current_instruction:

                    case InstructionSet.NOP:
                        self.finish_instruction(True)

                    case InstructionSet.DEBUG:
                        print("Processor: Debug instruction encountered.")
                        print("Current registers:")
                        print(self.registers)
                        self.finish_instruction(True)

                    case InstructionSet.JMP:
                        self.execute_jmp(address_bus, control_bus, data_bus)

                    case InstructionSet.LR:
                        self.execute_lr(address_bus, control_bus, data_bus)

                    case InstructionSet.LRM:
                        self.execute_lrm(address_bus, control_bus, data_bus)

                    case InstructionSet.MRM:
                        self.execute_mrm(address_bus, control_bus, data_bus)

                    case InstructionSet.LRR:
                        self.execute_lrr(address_bus, control_bus, data_bus)

                    case InstructionSet.INC:
                        self.execute_inc(address_bus, control_bus, data_bus)

                    case InstructionSet.ADD:
                        self.execute_add()

                    case InstructionSet.DIV:
                        self.execute_integer_divide()

                    case InstructionSet.MUL:
                        self.execute_multiply()

                    case InstructionSet.SUB:
                        self.execute_sub()

                    case InstructionSet.OR:
                        self.execute_or()

                    case InstructionSet.AND:
                        self.execute_and()

                    case InstructionSet.XOR:
                        self.execute_xor()

                    case InstructionSet.NOT:
                        self.execute_not()

                    case InstructionSet.CMP:
                        self.execute_cmp()

                    case InstructionSet.JE:
                        self.execute_je(address_bus, control_bus, data_bus)

                    case InstructionSet.JNE:
                        self.execute_jne(address_bus, control_bus, data_bus)

                    case InstructionSet.JL:
                        self.execute_jl(address_bus, control_bus, data_bus)

                    case InstructionSet.JG:
                        self.execute_jg(address_bus, control_bus, data_bus)

                    case InstructionSet.RST:
                        self.execute_reset()

                    case InstructionSet.HALT:
                        execute_halt(interrupt_bus)

                    case InstructionSet.PUSH:
                        self.execute_push(address_bus, control_bus, data_bus)

                    case InstructionSet.POP:
                        self.execute_pop(address_bus, control_bus, data_bus)

                    case InstructionSet.PEEK:
                        self.execute_peek(address_bus, control_bus, data_bus)

                    case InstructionSet.CALL:
                        self.execute_call(address_bus, control_bus, data_bus)

                    case InstructionSet.RTN:
                        self.execute_rtn()

                    case InstructionSet.SLEEP:
                        self.execute_sleep()

                    case InstructionSet.WAKE:
                        self.execute_wake()

                    case InstructionSet.SIV:
                        self.execute_siv(address_bus, control_bus, data_bus)

                    case _:
                        self.load_instruction(address_bus, control_bus, data_bus)

            if not self.cached_instruction_will_be_used(address_bus, control_bus, data_bus):
                break

    def cached_instruction_will_be_used(self, address_bus, control_bus, data_bus):
        """
        Check if the cached instruction will be used in the current cycle.
        If instruction will be used, it is placed on the data bus and the control bus is updated, as if it were
        fetched from memory.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:
            True if the cached instruction will be used, False otherwise.

        """
        if self.disable_instruction_caching:
            return False
        if (self.phase in [Phases.AwaitingInstruction, Phases.AwaitingFirstOperand, Phases.AwaitingSecondOperand]
                and control_bus.get_read_request()
                and address_bus.get_address() in self.instruction_and_operand_cache):
            data_bus.set_data(self.instruction_and_operand_cache[address_bus.get_address()])
            control_bus.set_read_request(False)
            control_bus.set_response(True)
            return True
        return False

    def cache_instruction(self, address_bus, control_bus, data_bus):
        """
        Cache incoming data from the data bus if the processor is awaiting an instruction or operand.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:

        """
        if self.disable_instruction_caching:
            return
        # if the processor is awaiting an instruction, and a response has been received, cache it
        if (self.phase == Phases.AwaitingInstruction or
                self.phase == Phases.AwaitingFirstOperand or
                self.phase == Phases.AwaitingSecondOperand):
            if control_bus.peek_response():
                self.instruction_and_operand_cache[address_bus.get_address()] = data_bus.get_data()

    # instruction fetching and execution
    def execute_reset(self):
        """
        Reset the processor's state.
        Returns:

        """
        self.current_instruction: int = -1
        self.data_pointer: int = 0
        self.phase: int = 0
        self.internal_stack = deque()
        self.general_purpose_stack = deque()
        self.register_stack = deque()
        self.call_stack = deque()
        self.registers = [0] * 8
        self.compare_result = CompareResults.Equal
        self.interrupt_in_progress = False
        self.interrupt_vectors: collections.OrderedDict[int, int] = collections.OrderedDict()
        self.sleeping: bool = False
        self.sleep_mode: bool = False

    def execute_wake(self):
        self.sleeping = False
        self.sleep_mode = False
        self.finish_instruction(True)

    def execute_sleep(self):
        self.sleeping = True
        self.sleep_mode = True
        self.finish_instruction(True)

    def load_instruction(self, address_bus, control_bus, data_bus):
        if self.phase == Phases.NothingPending:
            address_bus.set_address(self.data_pointer)
            control_bus.set_read_request(True)
            self.phase = Phases.AwaitingInstruction
        elif self.phase == Phases.AwaitingInstruction:
            if control_bus.get_response():
                self.current_instruction = data_bus.get_data()
                self.phase = Phases.NothingPending

    def execute_add(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] + self.registers[2]
            self.finish_instruction(True)

    def execute_sub(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] - self.registers[2]
            self.finish_instruction(True)

    def execute_integer_divide(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] // self.registers[2]
            self.finish_instruction(True)

    def execute_multiply(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] * self.registers[2]
            self.finish_instruction(True)

    def execute_lrr(self, address_bus, control_bus, data_bus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            destination_register = self.internal_stack.pop()
            self.registers[destination_register] = self.registers[value]
            self.finish_instruction(True)

    def execute_lrm(self, address_bus, control_bus, data_bus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            #  the data bus contains the memory address where the value destined for the register resides.
            #  fetch the value from memory
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.set_address(self.registers[abs(data_bus_data)])
                case _:
                    address_bus.set_address(value)
            control_bus.set_read_request(True)
            control_bus.set_response(False)
            self.phase = Phases.AwaitingResponse
        elif self.phase == Phases.AwaitingResponse:
            if control_bus.get_response():
                self.registers[self.internal_stack.pop()] = data_bus.get_data()
                self.finish_instruction(True)

    def execute_mrm(self, address_bus, control_bus, data_bus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            #  the data bus contains the memory address where the register's value is destined.
            #  send the value to memory
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.set_address(self.registers[abs(data_bus_data)])
                case _:
                    address_bus.set_address(value)

            data_bus.set_data(self.registers[self.internal_stack.pop()])
            control_bus.set_write_request(True)
            control_bus.set_response(False)
            self.phase = Phases.AwaitingResponse
        elif self.phase == Phases.AwaitingResponse:
            if control_bus.get_response():
                self.finish_instruction(True)

    def execute_lr(self, address_bus, control_bus, data_bus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            value: int = value
            destination_register = self.internal_stack.pop()
            self.registers[destination_register] = value
            self.finish_instruction(True)

    def execute_jmp(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.data_pointer = value
            self.finish_instruction(False)

    def execute_je(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.compare_result == CompareResults.Equal:
                self.data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jne(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if (self.compare_result == CompareResults.GreaterThan
                    or self.compare_result == CompareResults.LessThan):
                self.data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jl(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.compare_result == CompareResults.LessThan:
                self.data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jg(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.compare_result == CompareResults.GreaterThan:
                self.data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_cmp(self):
        if self.phase == Phases.NothingPending:
            if self.registers[1] == self.registers[2]:
                self.compare_result = CompareResults.Equal
            elif self.registers[1] > self.registers[2]:
                self.compare_result = CompareResults.GreaterThan
            elif self.registers[1] < self.registers[2]:
                self.compare_result = CompareResults.LessThan
            self.finish_instruction(True)

    def execute_push(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.general_purpose_stack.append(self.registers[value])
            self.phase = Phases.NothingPending
            self.finish_instruction(True)

    def execute_pop(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.registers[value] = self.general_purpose_stack.pop()
            self.finish_instruction(True)

    def execute_peek(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.registers[value] = self.general_purpose_stack[-1]()
            self.finish_instruction(True)

    def execute_call(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.call_stack.append(self.data_pointer)
            self.data_pointer = value
            self.push_registers()
            self.finish_instruction(False)

    def execute_rtn(self):
        if self.phase == Phases.NothingPending:
            self.interrupt_in_progress = False
            self.data_pointer = self.call_stack.pop()
            self.pop_registers()
            if self.sleep_mode:
                self.sleeping = True
            self.finish_instruction(True)

    def execute_siv(self, address_bus, control_bus, data_bus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            call_address: int = value
            interrupt_number = self.internal_stack.pop()
            self.interrupt_vectors[interrupt_number] = call_address
            self.finish_instruction(True)

    # instruction helpers
    def request_operand(self, address_bus, control_bus):
        self.data_pointer += 1
        address_bus.set_address(self.data_pointer)
        control_bus.set_read_request(True)
        control_bus.set_response(False)

    def finish_instruction(self, advance_pointer: bool = True):
        if advance_pointer:
            self.data_pointer += 1
        self.current_instruction = -1
        self.phase = Phases.NothingPending

    def push_registers(self):
        for i in range(8):
            self.register_stack.append(self.registers[i])

    def pop_registers(self):
        for i in range(7, -1, -1):
            self.registers[i] = self.register_stack.pop()

    def execute_or(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] | self.registers[2]
            self.finish_instruction(True)

    def execute_and(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] & self.registers[2]
            self.finish_instruction(True)

    def execute_xor(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = self.registers[1] ^ self.registers[2]
            self.finish_instruction(True)

    def execute_not(self):
        if self.phase == Phases.NothingPending:
            self.registers[3] = ~self.registers[1]
            self.finish_instruction(True)

    def execute_inc(self, address_bus, control_bus, data_bus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.registers[value] += 1
            self.finish_instruction(True)

    def request_single_operand(self, address_bus, control_bus, data_bus):
        if self.phase == Phases.NothingPending:
            self.request_operand(address_bus, control_bus)
            self.phase = Phases.AwaitingFirstOperand
        elif self.phase == Phases.AwaitingFirstOperand:
            if control_bus.get_response():
                return data_bus.get_data()
        return None

    def request_two_operands(self, address_bus, control_bus, data_bus):
        """
        Request two operands from the address bus and data bus.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:
            The second operand if the first operand has been received, otherwise None.
            The first operand is on the stack.
        """
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.internal_stack.append(value)
            self.request_operand(address_bus, control_bus)
            self.phase = Phases.AwaitingSecondOperand
        elif self.phase == Phases.AwaitingSecondOperand:
            if control_bus.get_response():
                return data_bus.get_data()
        return None
