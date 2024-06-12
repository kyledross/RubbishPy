import collections
import threading
from collections import deque
from datetime import datetime
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


def execute_halt(interrupt_bus: InterruptBus):
    interrupt_bus.set_interrupt(Interrupts.halt)


class Processor(BaseProcessor):
    """
    The Processor class represents a processor in the system.
    """

    def start(self) -> None:
        """
        This method starts the processor.
        Returns:

        """
        threading.Thread(target=self.main_loop, name=self.device_id + "::process_cycle").start()

    def __init__(self, starting_address: int, size: int, disable_instruction_caching: bool,
                 address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):
        # registers
        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self._handling_interrupt: bool = False
        self._call_source_stack = deque()
        self._disable_instruction_caching: bool = disable_instruction_caching
        self._current_instruction: int = InstructionSet.NoInstruction
        self._data_pointer: int = 0
        self._phase: int = 0
        self._registers = [0] * 8

        # stacks
        self._internal_stack = deque()
        self._general_purpose_stack = deque()
        self._register_stack = deque()
        self._call_stack = deque()

        # vectors
        self._interrupt_vectors: collections.OrderedDict[int, int] = collections.OrderedDict()

        # flags
        self._compare_result: CompareResults = CompareResults.Equal
        self._sleeping: bool = False
        self._sleep_mode: bool = False

        # instruction caching
        self._instruction_and_operand_cache = {}

        # interrupt handling
        self._interrupt_to_handle: bool = False
        self._interrupt_number_to_handle: int = 0

    def main_loop(self) -> None:
        """
        The main loop of the processor.  This runs continuously to process instructions.
        Returns:

        """
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            if self.control_bus.power_on:
                self.perform_instruction_processing()
            self.control_bus.unlock_bus()
        self.finished = True

    def perform_instruction_processing(self) -> None:
        """
        Perform instruction processing.
        This method will load instructions and operands from the instruction cache, or from memory if not cached.
        It then executes the instruction, accordingly.
        Returns:

        """
        address_bus = self.address_bus
        control_bus = self.control_bus
        data_bus = self.data_bus
        interrupt_bus = self.interrupt_bus
        self.cache_instruction(address_bus, control_bus, data_bus)
        while True:  # loop until a cached instruction request is not fulfilled
            # handle interrupts
            if self._sleeping and not self._handling_interrupt:
                interrupt_number = interrupt_bus.interrupt_awaiting()
                if interrupt_number in self._interrupt_vectors:
                    self._interrupt_to_handle = True
                    self._interrupt_number_to_handle = interrupt_number
                    self._sleeping = False
                    self._handling_interrupt = True
                    break

            if self._sleeping:
                break
            else:
                # Instruction routing
                match self._current_instruction:

                    case InstructionSet.NOP:
                        self.finish_instruction(True)

                    case InstructionSet.DEBUG:
                        self.execute_debug()

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
                        # is there an interrupt waiting?
                        # if so, fake a call to the interrupt vector
                        if self._interrupt_to_handle:
                            # fake the call
                            self._interrupt_to_handle = False
                            self.make_call(self._data_pointer,
                                           self._interrupt_vectors[self._interrupt_number_to_handle],
                                           True)
                        else:
                            self.load_instruction(address_bus, control_bus, data_bus)

            if not self.cached_instruction_will_be_used(address_bus, control_bus, data_bus):
                break

    def execute_debug(self) -> None:
        """
        Execute the debug instruction.
        This will print the current registers.
        Returns:

        """
        print(f"Processor: Debug instruction encountered at {datetime.now().strftime('%H:%M:%S')}")
        print("Current registers:")
        print(self._registers)
        self.finish_instruction(True)

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
        if self._disable_instruction_caching:
            return False
        if (self._phase in [Phases.AwaitingInstruction, Phases.AwaitingFirstOperand, Phases.AwaitingSecondOperand]
                and control_bus.read_request
                and address_bus.address in self._instruction_and_operand_cache):
            data_bus.data = self._instruction_and_operand_cache[address_bus.address]
            control_bus.read_request = False
            control_bus.response = True
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
        if self._disable_instruction_caching:
            return
        # if the processor is awaiting an instruction, and a response has been received, cache it
        if (self._phase == Phases.AwaitingInstruction or
                self._phase == Phases.AwaitingFirstOperand or
                self._phase == Phases.AwaitingSecondOperand):
            if control_bus.response:
                self._instruction_and_operand_cache[address_bus.address] = data_bus.data

    # instruction fetching and execution
    def execute_reset(self) -> None:
        """
        Reset the processor's state.
        Returns:

        """
        self._current_instruction = InstructionSet.NoInstruction
        self._data_pointer = 0
        self._phase = 0
        self._internal_stack = deque()
        self._general_purpose_stack = deque()
        self._register_stack = deque()
        self._call_stack = deque()
        self._registers = [0] * 8
        self._compare_result = CompareResults.Equal
        self._interrupt_vectors = collections.OrderedDict()
        self._sleeping = False
        self._sleep_mode = False

    def execute_wake(self) -> None:
        self._sleeping = False
        self._sleep_mode = False
        self.finish_instruction(True)

    def execute_sleep(self) -> None:
        self._sleeping = True
        self._sleep_mode = True
        self.finish_instruction(True)

    def load_instruction(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        """
        Load an instruction from memory.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:

        """
        if self._phase == Phases.NothingPending:
            address_bus.address = self._data_pointer
            control_bus.read_request = True
            self._phase = Phases.AwaitingInstruction
        elif self._phase == Phases.AwaitingInstruction:
            if control_bus.response:
                control_bus.response = False
                self._current_instruction = data_bus.data
                self._phase = Phases.NothingPending

    def execute_add(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] + self._registers[2]
            self.finish_instruction(True)

    def execute_sub(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] - self._registers[2]
            self.finish_instruction(True)

    def execute_integer_divide(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] // self._registers[2]
            self.finish_instruction(True)

    def execute_multiply(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] * self._registers[2]
            self.finish_instruction(True)

    def execute_lrr(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            destination_register = self._internal_stack.pop()
            self._registers[destination_register] = self._registers[value]
            self.finish_instruction(True)

    def execute_lrm(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            #  the data bus contains the memory address where the value destined for the register resides.
            #  fetch the value from memory
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.address = self._registers[abs(data_bus_data)]
                case _:
                    address_bus.address = value
            control_bus.read_request = True
            control_bus.response = False
            self._phase = Phases.AwaitingResponse
        elif self._phase == Phases.AwaitingResponse:
            if control_bus.response:
                control_bus.response = False
                self._registers[self._internal_stack.pop()] = data_bus.data
                self.finish_instruction(True)

    def execute_mrm(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            data_bus_data: int = value
            match data_bus_data < 0:
                case True:
                    address_bus.address = self._registers[abs(data_bus_data)]
                case _:
                    address_bus.address = value

            data_bus.data = self._registers[self._internal_stack.pop()]
            control_bus.write_request = True
            control_bus.response = False
            self._phase = Phases.AwaitingResponse
        elif self._phase == Phases.AwaitingResponse:
            if control_bus.response:
                control_bus.response = False
                self.finish_instruction(True)

    def execute_lr(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            value: int = value
            destination_register = self._internal_stack.pop()
            self._registers[destination_register] = value
            self.finish_instruction(True)

    def execute_jmp(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self._data_pointer = value
            self.finish_instruction(False)

    def execute_je(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self._compare_result == CompareResults.Equal:
                self._data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jne(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if (self._compare_result == CompareResults.GreaterThan
                    or self._compare_result == CompareResults.LessThan):
                self._data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jl(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self._compare_result == CompareResults.LessThan:
                self._data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_jg(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            if self._compare_result == CompareResults.GreaterThan:
                self._data_pointer = value
                self.finish_instruction(False)
            else:
                self.finish_instruction(True)

    def execute_cmp(self) -> None:
        if self._phase == Phases.NothingPending:
            if self._registers[1] == self._registers[2]:
                self._compare_result = CompareResults.Equal
            elif self._registers[1] > self._registers[2]:
                self._compare_result = CompareResults.GreaterThan
            elif self._registers[1] < self._registers[2]:
                self._compare_result = CompareResults.LessThan
            self.finish_instruction(True)

    def execute_push(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self._general_purpose_stack.append(self._registers[value])
            self._phase = Phases.NothingPending
            self.finish_instruction(True)

    def execute_pop(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self._registers[value] = self._general_purpose_stack.pop()
            self.finish_instruction(True)

    def execute_peek(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self._registers[value] = self._general_purpose_stack[-1]()
            self.finish_instruction(True)

    def execute_call(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            pointer: int = self._data_pointer
            self.make_call(pointer, value, False)

    def make_call(self, current_pointer: int, new_pointer: int, is_interrupt_sourced_call: bool) -> None:
        self._call_source_stack.append(is_interrupt_sourced_call)
        self._sleeping = False
        self._call_stack.append(current_pointer)
        self._data_pointer = new_pointer
        self.push_registers()
        self.finish_instruction(False)

    def execute_rtn(self) -> None:
        if self._phase == Phases.NothingPending:
            self._data_pointer = self._call_stack.pop()
            self.pop_registers()
            is_interrupt_sourced_call = self._call_source_stack.pop()
            if is_interrupt_sourced_call:
                if self._sleep_mode:
                    self._sleeping = True
                self._handling_interrupt = False

            self.finish_instruction(True)

    def execute_siv(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_two_operands(address_bus, control_bus, data_bus)
        if value is not None:
            interrupt_number = self._internal_stack.pop()
            if interrupt_number <= Interrupts.none or interrupt_number >= Interrupts.irq8:
                raise ValueError(f"Invalid interrupt number {interrupt_number}")
            self._interrupt_vectors[interrupt_number] = value
            self.finish_instruction(True)

    # instruction helpers
    def request_operand(self, address_bus: AddressBus, control_bus: ControlBus):
        """
        Requests an operand for the current instruction.
        Args:
            address_bus:
            control_bus:

        Returns:

        """
        self._data_pointer += 1
        address_bus.address = self._data_pointer
        control_bus.read_request = True
        control_bus.response = False

    def finish_instruction(self, advance_pointer: bool = True):
        """
        Finishes the execution of the current instruction and advances the data pointer if necessary.
        Args:
            advance_pointer:

        Returns:

        """
        if advance_pointer:
            self._data_pointer += 1
        self._current_instruction = InstructionSet.NoInstruction
        self._phase = Phases.NothingPending

    def push_registers(self) -> None:
        """
        Pushes all registers onto the register stack.
        Returns:

        """
        for i in range(8):
            self._register_stack.append(self._registers[i])

    def pop_registers(self) -> None:
        """
        Pops all registers from the register stack.
        Returns:

        """
        for i in range(7, -1, -1):
            self._registers[i] = self._register_stack.pop()

    def execute_or(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] | self._registers[2]
            self.finish_instruction(True)

    def execute_and(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] & self._registers[2]
            self.finish_instruction(True)

    def execute_xor(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = self._registers[1] ^ self._registers[2]
            self.finish_instruction(True)

    def execute_not(self) -> None:
        if self._phase == Phases.NothingPending:
            self._registers[3] = ~self._registers[1]
            self.finish_instruction(True)

    def execute_inc(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        value = self.request_single_operand(address_bus, control_bus, data_bus)
        if value is not None:
            self._registers[value] += 1
            self.finish_instruction(True)

    def request_single_operand(self, address_bus: AddressBus, control_bus: ControlBus, data_bus: DataBus):
        """
        Request a single operand from the address bus and data bus for the current instruction.
        Args:
            address_bus:
            control_bus:
            data_bus:

        Returns:

        """
        if self._phase == Phases.NothingPending:
            self.request_operand(address_bus, control_bus)
            self._phase = Phases.AwaitingFirstOperand
        elif self._phase == Phases.AwaitingFirstOperand:
            if control_bus.response:
                control_bus.response = False
                return data_bus.data
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
            self._internal_stack.append(value)
            self.request_operand(address_bus, control_bus)
            self._phase = Phases.AwaitingSecondOperand
        elif self._phase == Phases.AwaitingSecondOperand:
            if control_bus.response:
                control_bus.response = False
                return data_bus.data
        return None
