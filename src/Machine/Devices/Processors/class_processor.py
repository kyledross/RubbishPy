import collections
import threading
from collections import deque
from enum import IntFlag

from Constants.class_compare_results import CompareResults
from Constants.class_instruction_set import InstructionSet
from Constants.class_interrupts import Interrupts
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_processor import BaseProcessor


class Phases(IntFlag):
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


def execute_halt(interrupt_bus: InterruptBus):
    interrupt_bus.set_interrupt(Interrupts.halt)


# noinspection DuplicatedCode
class Processor(BaseProcessor):

    def start(self):
        threading.Thread(target=self.process_cycle, name=self.get_device_id() + "::process_cycle").start()

    def __init__(self, starting_address: int, size: int, disable_instruction_caching: bool,
                 address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        # registers
        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self.__disable_instruction_caching = disable_instruction_caching
        self.__current_instruction: int = -1
        self.__data_pointer: int = 0
        self.__phase: int = 0
        self.__registers = [0] * 8

        # stacks
        self.__internal_stack = deque()
        self.__general_purpose_stack = deque()
        self.__register_stack = deque()
        self.__call_stack = deque()

        # vectors
        self.__interrupt_vectors: collections.OrderedDict[int, int] = collections.OrderedDict()

        # flags
        self.__compare_result = CompareResults.Equal
        self.__interrupt_in_progress = False
        self.__sleeping: bool = False
        self.__sleep_mode: bool = False

        # instruction caching
        self.__instruction_and_operand_cache = {}

    def process_cycle(self):
        while self.is_running():
            self.control_bus().lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus().is_power_on():
                self.perform_instruction_processing()
            self.control_bus().unlock_bus()
        self.set_finished()

    def perform_instruction_processing(self):
        address_bus = self.address_bus()
        control_bus = self.control_bus()
        data_bus = self.data_bus()
        interrupt_bus = self.interrupt_bus()
        self.cache_instruction(address_bus, control_bus, data_bus)
        while True:  # loop until a cached instruction request is not fulfilled
            # Interrupt processing
            if self.__phase == Phases.NothingPending:
                if not self.__interrupt_in_progress:
                    for interruptBit in range(0, 32):
                        interrupt_number = 2 ** interruptBit
                        if interrupt_bus.test_interrupt(interrupt_number):
                            if interrupt_number in self.__interrupt_vectors:
                                self.__sleeping = False
                                self.__call_stack.append(self.__data_pointer)
                                self.__data_pointer = self.__interrupt_vectors[interrupt_number]
                                self.push_registers()
                                interrupt_bus.clear_interrupt(interrupt_number)
                                self.__interrupt_in_progress = True
                                break

            # Instruction routing
            if self.__sleeping:
                break
            else:
                match self.__current_instruction:

                    case InstructionSet.NOP:
                        self.finish_instruction(True)

                    case InstructionSet.DEBUG:
                        print("Processor: Debug instruction encountered.")
                        print("Current registers:")
                        print(self.__registers)
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

    def cached_instruction_will_be_used(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
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
        if self.__disable_instruction_caching:
            return False
        if (self.__phase in [Phases.AwaitingInstruction, Phases.AwaitingFirstOperand, Phases.AwaitingSecondOperand]
                and control_bus.get_read_request()
                and address_bus.get_address() in self.__instruction_and_operand_cache):
            data_bus.set_data(self.__instruction_and_operand_cache[address_bus.get_address()])
            control_bus.set_read_request(False)
            control_bus.set_response(True)
            return True
        return False

    def cache_instruction(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        """
        Cache incoming data from the data bus if the processor is awaiting an instruction or operand.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:

        """
        if self.__disable_instruction_caching:
            return
        # if the processor is awaiting an instruction, and a response has been received, cache it
        if (self.__phase == Phases.AwaitingInstruction or
                self.__phase == Phases.AwaitingFirstOperand or
                self.__phase == Phases.AwaitingSecondOperand):
            if control_bus.peek_response():
                self.__instruction_and_operand_cache[address_bus.get_address()] = data_bus.get_data()

    # instruction fetching and execution
    def execute_reset(self):
        """
        Reset the processor's state.
        Returns:

        """
        self.__current_instruction: int = -1
        self.__data_pointer: int = 0
        self.__phase: int = 0
        self.__internal_stack = deque()
        self.__general_purpose_stack = deque()
        self.__register_stack = deque()
        self.__call_stack = deque()
        self.__registers = [0] * 8
        self.__compare_result = CompareResults.Equal
        self.__interrupt_in_progress = False
        self.__interrupt_vectors: collections.OrderedDict[int, int] = collections.OrderedDict()
        self.__sleeping: bool = False
        self.__sleep_mode: bool = False

    def execute_wake(self):
        self.__sleeping = False
        self.__sleep_mode = False
        self.finish_instruction(True)

    def execute_sleep(self):
        self.__sleeping = True
        self.__sleep_mode = True
        self.finish_instruction(True)

    def load_instruction(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        if self.__phase == Phases.NothingPending:
            address_bus.set_address(self.__data_pointer)
            control_bus.set_read_request(True)
            self.__phase = Phases.AwaitingInstruction
        elif self.__phase == Phases.AwaitingInstruction:
            if control_bus.get_response():
                self.__current_instruction = data_bus.get_data()
                self.__phase = Phases.NothingPending

    def execute_add(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] + self.__registers[2]
            self.finish_instruction(True)

    def execute_sub(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] - self.__registers[2]
            self.finish_instruction(True)

    def execute_integer_divide(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] // self.__registers[2]
            self.finish_instruction(True)

    def execute_multiply(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] * self.__registers[2]
            self.finish_instruction(True)

    def execute_lrr(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            destination_register = self.__internal_stack.pop()
            self.__registers[destination_register] = self.__registers[value]
            self.finish_instruction(True)

    def execute_lrm(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            #  the data bus contains the memory address where the value destined for the register resides.
            #  fetch the value from memory
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.set_address(self.__registers[abs(data_bus_data)])
                case _:
                    address_bus.set_address(value)
            control_bus.set_read_request(True)
            control_bus.set_response(False)
            self.__phase = Phases.AwaitingResponse
        elif self.__phase == Phases.AwaitingResponse:
            if control_bus.get_response():
                self.__registers[self.__internal_stack.pop()] = data_bus.get_data()
                self.finish_instruction(True)

    def execute_mrm(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            #  the data bus contains the memory address where the register's value is destined.
            #  send the value to memory
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.set_address(self.__registers[abs(data_bus_data)])
                case _:
                    address_bus.set_address(value)

            data_bus.set_data(self.__registers[self.__internal_stack.pop()])
            control_bus.set_write_request(True)
            control_bus.set_response(False)
            self.__phase = Phases.AwaitingResponse
        elif self.__phase == Phases.AwaitingResponse:
            if control_bus.get_response():
                self.finish_instruction(True)

    def execute_lr(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            value: int = value
            destination_register = self.__internal_stack.pop()
            self.__registers[destination_register] = value
            self.finish_instruction(True)

    def execute_jmp(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__data_pointer = value
            self.finish_instruction(False)

    def execute_je(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.__compare_result == CompareResults.Equal:
                self.__data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jne(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if (self.__compare_result == CompareResults.GreaterThan
                    or self.__compare_result == CompareResults.LessThan):
                self.__data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jl(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.__compare_result == CompareResults.LessThan:
                self.__data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jg(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self.__compare_result == CompareResults.GreaterThan:
                self.__data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_cmp(self):
        if self.__phase == Phases.NothingPending:
            if self.__registers[1] == self.__registers[2]:
                self.__compare_result = CompareResults.Equal
            elif self.__registers[1] > self.__registers[2]:
                self.__compare_result = CompareResults.GreaterThan
            elif self.__registers[1] < self.__registers[2]:
                self.__compare_result = CompareResults.LessThan
            self.finish_instruction(True)

    def execute_push(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__general_purpose_stack.append(self.__registers[value])
            self.__phase = Phases.NothingPending
            self.finish_instruction(True)

    def execute_pop(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__registers[value] = self.__general_purpose_stack.pop()
            self.finish_instruction(True)

    def execute_peek(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__registers[value] = self.__general_purpose_stack[-1]()
            self.finish_instruction(True)

    def execute_call(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__call_stack.append(self.__data_pointer)
            self.__data_pointer = value
            self.push_registers()
            self.finish_instruction(False)

    def execute_rtn(self):
        if self.__phase == Phases.NothingPending:
            self.__interrupt_in_progress = False
            self.__data_pointer = self.__call_stack.pop()
            self.pop_registers()
            if self.__sleep_mode:
                self.__sleeping = True
            self.finish_instruction(True)

    def execute_siv(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            call_address: int = value
            interrupt_number = self.__internal_stack.pop()
            self.__interrupt_vectors[interrupt_number] = call_address
            self.finish_instruction(True)

    # instruction helpers
    def request_operand(self, address_bus: AddressBus, control_bus: ControlBus):
        self.__data_pointer += 1
        address_bus.set_address(self.__data_pointer)
        control_bus.set_read_request(True)
        control_bus.set_response(False)

    def finish_instruction(self, advance_pointer: bool = True):
        if advance_pointer:
            self.__data_pointer += 1
        self.__current_instruction = -1
        self.__phase = Phases.NothingPending

    def push_registers(self):
        for i in range(8):
            self.__register_stack.append(self.__registers[i])

    def pop_registers(self):
        for i in range(7, -1, -1):
            self.__registers[i] = self.__register_stack.pop()

    def execute_or(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] | self.__registers[2]
            self.finish_instruction(True)

    def execute_and(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] & self.__registers[2]
            self.finish_instruction(True)

    def execute_xor(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = self.__registers[1] ^ self.__registers[2]
            self.finish_instruction(True)

    def execute_not(self):
        if self.__phase == Phases.NothingPending:
            self.__registers[3] = ~self.__registers[1]
            self.finish_instruction(True)

    def execute_inc(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self.__registers[value] += 1
            self.finish_instruction(True)

    def request_single_operand(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        if self.__phase == Phases.NothingPending:
            self.request_operand(address_bus, control_bus)
            self.__phase = Phases.AwaitingFirstOperand
        elif self.__phase == Phases.AwaitingFirstOperand:
            if control_bus.get_response():
                return data_bus.get_data()
        return None

    def request_two_operands(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
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
            self.__internal_stack.append(value)
            self.request_operand(address_bus, control_bus)
            self.__phase = Phases.AwaitingSecondOperand
        elif self.__phase == Phases.AwaitingSecondOperand:
            if control_bus.get_response():
                return data_bus.get_data()
        return None
