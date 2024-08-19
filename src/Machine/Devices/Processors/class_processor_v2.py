import threading
from asyncio import sleep
from datetime import datetime

from Constants.class_compare_results import CompareResults
from Constants.class_instruction_set import InstructionSet
from Machine.Buses.class_address_bus import AddressBus
from Machine.Buses.class_control_bus import ControlBus
from Machine.Buses.class_data_bus import DataBus
from Machine.Buses.class_interrupt_bus import InterruptBus
from Machine.Devices.Bases.class_base_processor import BaseProcessor

class ProcessorV2(BaseProcessor):

    def get_byte(self, address: int):
        self.control_bus.lock_bus()
        self.address_bus.address = address
        self.control_bus.read_request = True
        self.control_bus.unlock_bus()
        while not self.control_bus.response:
            sleep(.1)
        self.control_bus.lock_bus()
        value:int = self.data_bus.data
        self.control_bus.response = False
        self.control_bus.unlock_bus()
        return value
            
    
    def __init__(self, starting_address: int, size: int, disable_instruction_caching: bool,
                 address_bus: AddressBus, data_bus: DataBus, control_bus: ControlBus, interrupt_bus: InterruptBus):

        super().__init__(starting_address, size, address_bus, data_bus, control_bus, interrupt_bus)
        self.instruction_pointer: int = 0
        self.instruction_pointer_stack: list[int] = []

        self.registers: list[int] = []
        self.register_stack: list[list[int]] = []

        self.user_stack: list[int] = []

        self.sleeping: bool = False
        self.sleep_mode: bool = False

        self.compare_result: CompareResults = CompareResults.Inconclusive
        


    def start(self) -> None:

        """
        This method starts the processor.
        Returns:

        """
        threading.Thread(target=self.main_loop, name=self.device_id + "::process_cycle").start()
            
        
    def main_loop(self) -> None:
        while self.running:
            self.control_bus.lock_bus()
            self.stop_running_if_halt_detected()
            power_is_on: bool = self.control_bus.power_on
            self.control_bus.unlock_bus()
            if power_is_on:
                self.process_interrupts()
                if not self.sleeping:
                    self.perform_instruction_processing()
        self.finished = True

    def perform_instruction_processing(self) -> None:
        instruction = self.get_byte(self.instruction_pointer)
        
        match instruction:
            case InstructionSet.NOP:
                self.instruction_pointer += 1
            case InstructionSet.LR:
                destination_register:int = self.get_byte(self.instruction_pointer + 1)
                value: int = self.get_byte(self.instruction_pointer + 2)
                self.registers[destination_register] = value
                self.instruction_pointer += 3
            case InstructionSet.LRM:
                destination_register:int = self.get_byte(self.instruction_pointer + 1)
                address: int = self.get_byte(self.instruction_pointer + 2)
                address = self.convert_register_pointer_if_necessary(address)
                value: int = self.get_byte(address)
                self.registers[destination_register] = value    
                self.instruction_pointer += 3
            case InstructionSet.LRR:
                destination_register:int = self.get_byte(self.instruction_pointer + 1)
                source_register:int = self.get_byte(self.instruction_pointer + 2)
                self.registers[destination_register] = self.registers[source_register]
                self.instruction_pointer += 3
            case InstructionSet.MRM:
                source_register:int = self.get_byte(self.instruction_pointer + 1)
                address: int = self.get_byte(self.instruction_pointer + 2)
                address = self.convert_register_pointer_if_necessary(address)
                self.send_byte(address, self.registers[source_register])
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
                self.control_bus.halt = True
                self.control_bus.unlock_bus()
            case InstructionSet.DEBUG:
                print(f"Processor: Debug instruction encountered at {datetime.now().strftime('%H:%M:%S')}")
                print("Current registers:")
                print(self._registers)
            case InstructionSet.JMP:
                destination_address: int = self.convert_register_pointer_if_necessary(self.get_byte(self.instruction_pointer + 1))
                self.instruction_pointer = destination_address
            case InstructionSet.RST:
                # todo: implement processor reset
                pass
            case InstructionSet.CMP:
                if self.registers[1] < self.registers[2]:
                    self.compare_result = CompareResults.LessThan
                elif self.registers[1] > self.registers[2]:
                    self.compare_result = CompareResults.GreaterThan
                else:
                    self.compare_result = CompareResults.Equal
            case InstructionSet.JE:
                if self.compare_result == CompareResults.Equal:
                    destination_address: int = self.convert_register_pointer_if_necessary(self.get_byte(self.instruction_pointer + 1))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JNE:
                if self.compare_result != CompareResults.Equal:
                    destination_address: int = self.convert_register_pointer_if_necessary(self.get_byte(self.instruction_pointer + 1))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JL:
                if self.compare_result == CompareResults.LessThan:
                    destination_address: int = self.convert_register_pointer_if_necessary(self.get_byte(self.instruction_pointer + 1))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.JG:
                if self.compare_result == CompareResults.GreaterThan:
                    destination_address: int = self.convert_register_pointer_if_necessary(self.get_byte(self.instruction_pointer + 1))
                    self.instruction_pointer = destination_address
                else:
                    self.instruction_pointer += 2
            case InstructionSet.PUSH:
                source_register: int = self.get_byte(self.instruction_pointer + 1)
                self.user_stack.append(self.registers[source_register])
                self.instruction_pointer += 2
            case InstructionSet.POP:
                destination_register: int = self.get_byte(self.instruction_pointer + 1)
                self.registers[destination_register] = self.user_stack.pop()
                self.instruction_pointer += 2
            case InstructionSet.CALL:
                # todo: implement call
                pass
            case InstructionSet.RTN:
                # todo: implement return
                pass
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
                # todo: implement set interrupt vector
                pass
            case InstructionSet.INC:
                destination_register: int = self.get_byte(self.instruction_pointer + 1)
                self.registers[destination_register] += 1
                self.instruction_pointer += 2
            case InstructionSet.DEC:
                destination_register: int = self.get_byte(self.instruction_pointer + 1)
                self.registers[destination_register] -= 1
                self.instruction_pointer += 2
            case InstructionSet.SLEEP:
                # todo: implement sleep
                pass
            case InstructionSet.WAKE:
                # todo: implement wake
                pass
            case InstructionSet.PEEK:
                destination_register: int = self.get_byte(self.instruction_pointer + 1)
                self.registers[destination_register] = self.user_stack[-1]
                self.instruction_pointer += 2
            case _:
                # Raise an error for unknown instruction
                raise ValueError(f"Unknown instruction encountered at address {self.instruction_pointer}. Opcode is {instruction}")
                
    def process_interrupts(self):
        # self.control_bus.lock_bus()
        self.sleeping = False
        # todo: implement interrupt processing
        # in rtn, check if the call stack is empty
        # if it is, and the processor is in sleep mode, put the processor back to sleep
        # self.control_bus.unlock_bus()
        pass

    def convert_register_pointer_if_necessary(self, address: int) -> int:
        if address < 0:
            address = abs(address)
            return self.registers[address]
        return address

    def send_byte(self, address: int, value: int):
        pass
        
        
    
        