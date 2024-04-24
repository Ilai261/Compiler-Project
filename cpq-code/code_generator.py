from symbol_table import SymbolTable
from utils import FLOAT, INT, MINUS, PLUS

INT_VAR = "ti"
FLOAT_VAR = "tf"


class CodeGenerator:
    def __init__(self, symbol_table):
        self.variable_generator: VariableGenerator = VariableGenerator()
        self.lable_generator: LableGenerator = LableGenerator()
        self.symbol_table: SymbolTable = symbol_table

    def generate_assignment_stmt(self, expression_code, id, expression_var):
        generated_code = f"{expression_code}\n"
        if self.symbol_table.get_variable_type(id) == INT:
            generated_code += f"IASN {id} {expression_var}"
        elif self.symbol_table.get_variable_type(p.ID) == FLOAT:
            generated_code += f"RASN {id} {expression_var}"
        return generated_code

    def generate_expression(
        self, expression_code, expression_retval_var, addop, term_code, term_retval_var
    ):
        generated_code = f"{expression_code}\n{term_code}\n"
        if addop == PLUS:
            if expression_retval_var.startswith(INT_VAR) and term_retval_var.startswith(
                INT_VAR
            ):
                new_retval_var = (
                    self.variable_generator.get_new_int_variable()
                )  # make sure variable is new
                generated_code += (
                    f"IADD {new_retval_var} {expression_retval_var} {term_retval_var}"
                )


class VariableGenerator:
    # designates between int and float variable names
    def __init__(self):
        self.int_variable_count = 0
        self.float_variable_count = 0

    def get_new_int_variable(self):
        var = f"{INT_VAR}{self.int_variable_count}"
        self.int_variable_count += 1
        return var

    def get_new_float_variable(self):
        var = f"{FLOAT_VAR}{self.float_variable_count}"
        self.float_variable_count += 1
        return var


class LableGenerator:
    def __init__(self):
        self.lable_count = 0

    def get_new_lable(self):
        lable = f"L{self.lable_count}"
        self.lable_count += 1
        return lable
