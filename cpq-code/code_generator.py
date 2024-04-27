from symbol_table import SymbolTable
from utils import (
    DIVIDE,
    FLOAT,
    FLOAT_CAST,
    INT,
    INT_CAST,
    MINUS,
    MULTIPLY,
    PLUS,
    RELOP_EQUALS,
    RELOP_GREATER_THAN_OR_EQUALS,
    RELOP_LESS_THAN_OR_EQUALS,
    RELOP_NOT_EQUALS,
    RELOP_REALLY_GREATER_THAN,
    RELOP_REALLY_LESS_THAN,
    error_print,
    float_to_int_str,
    is_float,
    is_integer,
)

INT_VAR = "ti"
FLOAT_VAR = "tf"


class CodeGenerator:
    def __init__(self, symbol_table):
        self.variable_generator: VariableGenerator = VariableGenerator(symbol_table)
        self.lable_generator: LableGenerator = LableGenerator()
        self.symbol_table: SymbolTable = symbol_table

    # var can be an id, temporary variable or a num
    def is_variable_float(self, var):
        return (
            (self.symbol_table.get_variable_type(var) == FLOAT)
            or is_float(var)
            or var.startswith(FLOAT_VAR)
        )

    # var can be an id, temporary variable or a num
    def is_variable_integer(self, var):
        return (
            (self.symbol_table.get_variable_type(var) == INT)
            or is_integer(var)
            or var.startswith(INT_VAR)
        )

    def generate_assignment_stmt(self, expression_code, id, expression_var):
        # we need to add a check, if the expression is int and id is float we need to cast the expression retval.
        # also if expression is float and id is int we put out an error
        generated_code = ""
        if expression_code != "":
            generated_code = f"{expression_code}\n"
        if self.symbol_table.get_variable_type(id) == INT:
            # check if var is float then error, else all good
            if self.is_variable_float(expression_var):
                return False
            generated_code += f"IASN {id} {expression_var}"
        elif self.symbol_table.get_variable_type(id) == FLOAT:
            # check if var is int then cast it to float, else continue
            if self.is_variable_integer(expression_var):
                new_expression_var = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression_var} {expression_var}\n"
                expression_var = new_expression_var
            generated_code += f"RASN {id} {expression_var}"
        return generated_code

    def generate_expression(
        self, expression_code, expression_retval_var, addop, term_code, term_retval_var
    ):
        generated_code = ""
        if expression_code != "":
            generated_code += f"{expression_code}\n"
        if term_code != "":
            generated_code += f"{term_code}\n"
        if addop == PLUS:
            COMMAND = {INT: "IADD", FLOAT: "RADD"}
        else:
            COMMAND = {INT: "ISUB", FLOAT: "RSUB"}

        # both are integers
        if (
            self.is_variable_integer(expression_retval_var)
        ) and self.is_variable_integer(term_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            generated_code += f"{COMMAND[INT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
            return generated_code, new_retval_var

        # both are floats
        elif (self.is_variable_float(expression_retval_var)) and self.is_variable_float(
            term_retval_var
        ):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
            return generated_code, new_retval_var

        # expression is float term is int, need to cast
        elif (
            self.is_variable_float(expression_retval_var)
        ) and self.is_variable_integer(term_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            if is_integer(term_retval_var):
                term_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
                return generated_code, new_retval_var
            else:
                new_term = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_term} {term_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {new_term}"
                return generated_code, new_retval_var

        # expression is int term is float, need to cast
        elif (
            self.is_variable_integer(expression_retval_var)
        ) and self.is_variable_float(term_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            if is_integer(expression_retval_var):
                expression_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
                return generated_code, new_retval_var
            else:
                new_expression = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression} {expression_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {new_expression} {term_retval_var}"
                return generated_code, new_retval_var

    def generate_term(
        self, term_code, term_retval_var, mulop, factor_code, factor_retval_var
    ):
        generated_code = ""
        if term_code != "":
            generated_code += f"{term_code}\n"
        if factor_code != "":
            generated_code += f"{factor_code}\n"
        if mulop == MULTIPLY:
            COMMAND = {INT: "IMLT", FLOAT: "RMLT"}
        else:
            COMMAND = {INT: "IDIV", FLOAT: "RDIV"}

        # both are integers
        if self.is_variable_integer(term_retval_var) and (
            self.is_variable_integer(factor_retval_var)
        ):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            generated_code += (
                f"{COMMAND[INT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
            )
            return generated_code, new_retval_var

        # both are floats
        elif self.is_variable_float(term_retval_var) and (
            self.is_variable_float(factor_retval_var)
        ):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
            return generated_code, new_retval_var

        # term is float factor is int, need to cast
        elif self.is_variable_float(term_retval_var) and (
            self.is_variable_integer(factor_retval_var)
        ):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            if is_integer(factor_retval_var):
                factor_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
                return generated_code, new_retval_var
            else:
                new_factor = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_factor} {factor_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {new_factor}"
                return generated_code, new_retval_var

        # term is int factor is float, need to cast
        elif self.is_variable_integer(term_retval_var) and (
            self.is_variable_float(factor_retval_var)
        ):
            new_retval_var = (
                self.variable_generator.get_new_float_variable()
            )  # make sure variable is new
            if is_integer(term_retval_var):
                term_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
                return generated_code, new_retval_var
            else:
                new_term = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_term} {term_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {new_term} {factor_retval_var}"
                return generated_code, new_retval_var

    def generate_casting_factor(self, expression_code, expression_retval_var, cast):
        # if no cast is actually needed
        if (self.is_variable_integer(expression_retval_var) and cast == INT_CAST) or (
            self.is_variable_float(expression_retval_var) and cast == FLOAT_CAST
        ):
            return expression_code, expression_retval_var
        generated_code = ""
        if expression_code != "":
            generated_code += f"{expression_code}\n"
        if cast == INT_CAST:
            COMMAND = "RTOI"
        else:
            COMMAND = "ITOR"

        if self.is_variable_integer(expression_retval_var) and cast == FLOAT_CAST:
            if is_integer(expression_retval_var):
                expression_retval_var += ".0"
                return generated_code, expression_retval_var
            else:
                new_expression_retval_var = (
                    self.variable_generator.get_new_float_variable()
                )
                generated_code += (
                    f"{COMMAND} {new_expression_retval_var} {expression_retval_var}"
                )
                return generated_code, new_expression_retval_var
        else:
            if is_float(expression_retval_var):
                expression_retval_var = float_to_int_str(expression_retval_var)
                return generated_code, expression_retval_var
            else:
                new_expression_retval_var = (
                    self.variable_generator.get_new_int_variable()
                )
                generated_code += (
                    f"{COMMAND} {new_expression_retval_var} {expression_retval_var}"
                )
                return generated_code, new_expression_retval_var

    def generate_relop_boolfactor(
        self,
        expression1_code,
        expression1_retval_var,
        relop,
        expression2_code,
        expression2_retval_var,
    ):
        generated_code = ""
        if expression1_code != "":
            generated_code += f"{expression1_code}\n"
        if expression2_code != "":
            generated_code += f"{expression2_code}\n"
        if relop == RELOP_EQUALS:
            COMMAND = {INT: "IEQL", FLOAT: "REQL"}
        elif relop == RELOP_NOT_EQUALS:
            COMMAND = {INT: "INQL", FLOAT: "RNQL"}
        elif relop == RELOP_GREATER_THAN_OR_EQUALS:
            COMMAND = {INT: "IGRT", FLOAT: "RGRT"}
            COMMAND1 = {INT: "IEQL", FLOAT: "REQL"}
        elif relop == RELOP_LESS_THAN_OR_EQUALS:
            COMMAND = {INT: "ILSS", FLOAT: "RLSS"}
            COMMAND1 = {INT: "IEQL", FLOAT: "REQL"}
        elif relop == RELOP_REALLY_GREATER_THAN:
            COMMAND = {INT: "IGRT", FLOAT: "RGRT"}
        else:
            COMMAND = {INT: "ILSS", FLOAT: "RLSS"}

        # both are integers
        if (
            self.is_variable_integer(expression1_retval_var)
        ) and self.is_variable_integer(expression2_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[INT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}\n\
{COMMAND1[INT]} {new_retval_var2} {expression1_retval_var} {expression2_retval_var}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            else:
                generated_code += f"{COMMAND[INT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}"
                return generated_code, new_retval_var

        # both are floats
        elif (
            self.is_variable_float(expression1_retval_var)
        ) and self.is_variable_float(expression2_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {expression1_retval_var} {expression2_retval_var}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}"
                return generated_code, new_retval_var

        # expression1 is float expression2 is int, need to cast
        elif (
            self.is_variable_float(expression1_retval_var)
        ) and self.is_variable_integer(expression2_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            if is_integer(expression2_retval_var):
                expression2_retval_var += ".0"
            else:
                new_expression2 = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression2} {expression2_retval_var}\n"
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression2}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {expression1_retval_var} {new_expression2}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression2}"
                return generated_code, new_retval_var

        # expression1 is int expression2 is float, need to cast
        elif (
            self.is_variable_integer(expression1_retval_var)
        ) and self.is_variable_float(expression2_retval_var):
            new_retval_var = (
                self.variable_generator.get_new_int_variable()
            )  # make sure variable is new
            if is_integer(expression1_retval_var):
                expression1_retval_var += ".0"
            else:
                new_expression1 = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression1} {expression1_retval_var}\n"
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression1}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {expression1_retval_var} {new_expression1}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression1}"
                return generated_code, new_retval_var


class VariableGenerator:
    # designates between int and float variable names
    def __init__(self, symbol_table):
        self.int_variable_count = 0
        self.float_variable_count = 0
        self.symbol_table: SymbolTable = symbol_table

    """ we need to add checks in symbol table here if variable already exists """

    def get_new_int_variable(self):
        var = f"{INT_VAR}{self.int_variable_count}"
        while self.symbol_table.has_variable(var):
            self.int_variable_count += 1
            var = f"{INT_VAR}{self.int_variable_count}"
        self.int_variable_count += 1
        return var

    def get_new_float_variable(self):
        var = f"{FLOAT_VAR}{self.float_variable_count}"
        while self.symbol_table.has_variable(var):
            self.float_variable_count += 1
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
