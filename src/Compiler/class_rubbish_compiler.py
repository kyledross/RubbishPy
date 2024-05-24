class RubbishCompiler:
    """
    The RubbishCompiler class represents a compiler for the Rubbish language.
    It provides methods to compile the source code into machine code.
    """

    def __init__(self, address: int):
        """
        Constructor for the RubbishCompiler class.
        Initializes the source code and the address to compile to.
        :param address: The address to compile to.
        """
        self.labels = {}
        self.address: int = address

    def compile(self, source_pathname):
        """
        This method compiles the source code into machine code.
        It goes through two phases:
        Phase 1 - compile code, so we know the offset of labels
        Phase 2 - compile code and use label address offsets
        :return: The compiled machine code.

        Args:
            source_pathname:
        """
        code = []
        try:
            lines = []
            self.read_file(source_pathname, lines)

            for phase in range(1, 3):
                # phase 1 - compile code, so we know the offset of labels
                # phase 2 - compile code and use label address offsets
                code = []
                line_number = 0
                for line in lines:
                    line_number += 1
                    if len(line.strip()) != 0:
                        parameters = line.strip().split()
                        if ":" in parameters[0]:
                            label_name = parameters[0][:parameters[0].index(":")]
                            if phase == 1:
                                self.labels[label_name] = len(code) + self.address
                            parameters[0] = parameters[0].replace(label_name + ":", "")
                            if len(parameters[0]) == 0:
                                parameters.pop(0)
                            if len(parameters) == 0:  # this was a stand-alone label
                                continue

                        instruction = parameters[0].strip().upper()
                        # noinspection SpellCheckingInspection
                        if instruction == "'":
                            # This is just a comment
                            pass
                        elif instruction == "NOP":
                            self.add_instruction(0, [], code, phase == 2)

                        elif instruction == "DATA":
                            data = line[line.index(parameters[0]) + len(parameters[0]) + 1:]
                            data = data.replace(r"\r", "\r").replace(r"\n", "\n").replace(r"\0", "\0").replace(r"\f",
                                                                                                               "\f")
                            code.extend(ord(char) for char in data)

                        elif instruction in {"LR", "LRM", "LRR", "MRM", "ADD", "DIV", "MUL", "SUB", "JMP", "HALT",
                                             "DEBUG", "RST", "CMP", "JE", "JNE", "JL", "JG", "PUSH", "POP", "CALL",
                                             "RTN", "SIV", "SLEEP", "WAKE", "PEEK", "OR", "AND", "XOR", "NOT"}:
                            self.add_instruction(self.get_instruction_code(instruction), parameters, code, phase == 2)

                        else:
                            print("Compile failed.")
                            out = f"Unknown instruction {instruction} at line {line_number}"
                            print(out)
                            raise Exception(out)

            return code

        except Exception as ex:
            raise ex
        finally:
            pass

    def read_file(self, source_pathname, lines):
        with open(source_pathname, 'r') as file:
            for line in file:
                strip = line.strip()
                if strip.startswith("include "):
                    self.read_file(strip[8:], lines)
                else:
                    lines.append(strip)

    # Function to cross-reference register
    @staticmethod
    def cross_reference_register(parameters, parameter_number):
        """
        This function checks if the parameter starts with '@' and if so, it multiplies the parameter by -1.
        This is used to indicate that the parameter is a register.
        :param parameters: The list of parameters.
        :param parameter_number: The index of the parameter to cross-reference.
        """
        if str(parameters[parameter_number]).startswith("@"):
            parameters[parameter_number] = str(int(parameters[parameter_number][1:]) * -1)

    def cross_reference_label(self, parameters, parameter_number, cross_reference_labels: bool = False):
        """
        This method cross-references a label.
        If the parameter starts with ':' or is not numeric, it replaces the parameter with the address of the label.
        :param parameters: The list of parameters.
        :param parameter_number: The index of the parameter to cross-reference.
        :param cross_reference_labels: Whether to cross-reference labels or not.
        """
        parameter = str(parameters[parameter_number])
        if not self.is_numeric(parameter) and not parameter.startswith("@"):  # don't cross-reference pointers
            # label references used to be required to be prefixed with a colon
            # this is no longer necessary, so remove the colon if it exists
            if parameter.startswith(":"):
                parameter = parameter[1:]
            if cross_reference_labels:
                parameters[parameter_number] = str(self.get_address_from_label(parameter))
            else:
                parameters[parameter_number] = 0  # dummy placeholder

    def get_address(self, address_parameter):
        """
        This method returns the address for the given parameter.
        If the parameter is a digit, it returns the integer value of the parameter.
        Otherwise, it returns the address of the label with the same name as the parameter.
        :param address_parameter: The parameter to get the address for.
        :return: The address for the given parameter.
        """
        if self.is_numeric(address_parameter):
            return int(address_parameter)
        return self.labels[address_parameter]

    def add_instruction(self, instruction, parameters, code, cross_reference_labels: bool):
        """
        This method adds an instruction to the code.
        Cross-references labels and registers and then adds the instruction and its parameters to the code.
        :param instruction: The instruction to add.
        :param parameters: The parameters for the instruction.
        :param code: The code to add the instruction to.
        :param cross_reference_labels: Whether to cross-reference labels or not.
        """
        # code.extend(parameters)
        code.append(instruction)
        for parameter_index in range(1, len(parameters)):
            self.cross_reference_label(parameters, parameter_index, cross_reference_labels)
            self.cross_reference_register(parameters, parameter_index)
            code.append(int(parameters[parameter_index]))

    def get_address_from_label(self, label):
        """
        This method returns the address for the given label.
        :param label: The label to get the address for.
        :return: The address for the given label.
        """
        return str(self.labels[label])

    # Function to get instruction code
    @staticmethod
    def get_instruction_code(instruction):
        """
        This function returns the op code for the given instruction.
        :param instruction: The instruction to get the op code for.
        :return: The op code for the given instruction.
        """
        # noinspection SpellCheckingInspection
        op_codes = {
            "LR": 1, "LRM": 2, "LRR": 3, "MRM": 4, "ADD": 5, "DIV": 8, "MUL": 7, "SUB": 6, "JMP": 11, "HALT": 9,
            "DEBUG": 10, "RST": 12, "CMP": 13, "JE": 14, "JNE": 15, "JL": 16, "JG": 17, "PUSH": 18, "POP": 19,
            "CALL": 20, "RTN": 21, "SIV": 26, "SLEEP": 28, "WAKE": 29, "PEEK": 34, "OR": 23, "AND": 24, "XOR": 25,
            "NOT": 22
        }
        return op_codes[instruction]

    @staticmethod
    def is_numeric(s):
        """
        This function checks if the input string can be converted to a float.
        It returns True if the string can be converted to a float, otherwise it returns False.

        :param s: The string to check.
        :return: True if the string can be converted to a float, otherwise False.
        """
        try:
            float(s)
            return True
        except ValueError:
            return False
