""" Written by Ilai Azaria, 2024
    This module takes care of generating code for the parser in real-time
"""

from symbol_table import SymbolTable
from utils import (
    FLOAT,
    FLOAT_CAST,
    FLOAT_VAR,
    INT,
    INT_CAST,
    INT_VAR,
    MULTIPLY,
    PLUS,
    RELOP_EQUALS,
    RELOP_GREATER_THAN_OR_EQUALS,
    RELOP_LESS_THAN_OR_EQUALS,
    RELOP_NOT_EQUALS,
    RELOP_REALLY_GREATER_THAN,
    float_to_int_str,
    is_num_float,
    is_num_integer,
)


# this is the code generator class that generates code for the parser
class CodeGenerator:
    def __init__(self, symbol_table):
        # the code generator has a variable generator, label generator and the symbol table
        self.variable_generator: VariableGenerator = VariableGenerator(symbol_table)
        self.label_generator: LabelGenerator = LabelGenerator()
        self.symbol_table: SymbolTable = symbol_table

    # var can be an id, temporary variable or a num
    def is_variable_float(self, var):
        return (
            (self.symbol_table.get_variable_type(var) == FLOAT)
            or is_num_float(var)
            or var.startswith(FLOAT_VAR)
        )

    # var can be an id, temporary variable or a num
    def is_variable_integer(self, var):
        return (
            (self.symbol_table.get_variable_type(var) == INT)
            or is_num_integer(var)
            or var.startswith(INT_VAR)
        )

    # this function generates an assignment stmt
    def generate_assignment_stmt(self, expression_code, id, expression_var):
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
                if is_num_integer(expression_var):
                    expression_var += ".0"
                else:
                    new_expression_var = (
                        self.variable_generator.get_new_float_variable()
                    )
                    generated_code += f"ITOR {new_expression_var} {expression_var}\n"
                    expression_var = new_expression_var
            generated_code += f"RASN {id} {expression_var}"
        return generated_code

    # this function generated an input stmt
    def generate_input_stmt(self, id):
        # we generate depending on the id type
        generated_code = ""
        if self.symbol_table.get_variable_type(id) == INT:
            generated_code += f"IINP {id}"
        else:
            generated_code += f"RINP {id}"
        return generated_code

    # this function generated an output stmt
    def generate_output_stmt(self, expression_code, expression_retval_var):
        # we generate depending on the id type
        generated_code = ""
        if expression_code != "":
            generated_code += f"{expression_code}\n"

        if self.is_variable_integer(expression_retval_var):
            generated_code += f"IPRT {expression_retval_var}"
        elif self.is_variable_float(expression_retval_var):
            generated_code += f"RPRT {expression_retval_var}"
        return generated_code

    def generate_if_stmt(
        self, boolexpr_code, boolexpr_retval_var, positive_stmt_code, negative_stmt_code
    ):
        # we create two new labels for the code and call the function to generate the new if code
        positive_label = self.label_generator.get_new_label()
        negative_label = self.label_generator.get_new_label()
        return self.generate_if_code(
            boolexpr_code,
            boolexpr_retval_var,
            positive_stmt_code,
            negative_stmt_code,
            positive_label,
            negative_label,
        )

    def generate_while_stmt(self, boolexpr_code, boolexpr_retval_var, stmt_code):
        while_entry_label = self.label_generator.get_new_label()
        while_exit_label = self.label_generator.get_new_label()
        # we create two new labels for the code and call the function to generate the new while code
        return self.generate_while_code(
            boolexpr_code,
            boolexpr_retval_var,
            stmt_code,
            while_entry_label,
            while_exit_label,
        )

    # here we generate an expression from an expression, an addop and a term
    # we split the code to 4 parts depending on expression and term types, for correct casting if needed and code
    def generate_expression(
        self, expression_code, expression_retval_var, addop, term_code, term_retval_var
    ):
        # we initialize the generated code and the quad command we are going to use
        generated_code, COMMAND = self.initialize_code_and_command_expression(
            expression_code, addop, term_code
        )

        # both are integers
        if (
            self.is_variable_integer(expression_retval_var)
        ) and self.is_variable_integer(term_retval_var):
            new_retval_var = self.variable_generator.get_new_int_variable()
            generated_code += f"{COMMAND[INT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
            return generated_code, new_retval_var

        # both are floats
        elif (self.is_variable_float(expression_retval_var)) and self.is_variable_float(
            term_retval_var
        ):
            new_retval_var = self.variable_generator.get_new_float_variable()
            generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
            return generated_code, new_retval_var

        # expression is float term is int, need to cast
        elif (
            self.is_variable_float(expression_retval_var)
        ) and self.is_variable_integer(term_retval_var):
            new_retval_var = self.variable_generator.get_new_float_variable()
            # we cast term and then generate the code
            if is_num_integer(term_retval_var):
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
            new_retval_var = self.variable_generator.get_new_float_variable()
            # we cast expression and then generate the code
            if is_num_integer(expression_retval_var):
                expression_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression_retval_var} {term_retval_var}"
                return generated_code, new_retval_var
            else:
                new_expression = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression} {expression_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {new_expression} {term_retval_var}"
                return generated_code, new_retval_var

    # here we generate a term from a term, a mulop and a factor
    # we split the code to 4 parts depending on term and factor types, for correct casting if needed and code
    def generate_term(
        self, term_code, term_retval_var, mulop, factor_code, factor_retval_var
    ):
        # we initialize the generated code and the quad command we are going to use
        generated_code, COMMAND = self.initialize_code_and_command_term(
            term_code, mulop, factor_code
        )

        # both are integers
        if self.is_variable_integer(term_retval_var) and (
            self.is_variable_integer(factor_retval_var)
        ):
            new_retval_var = self.variable_generator.get_new_int_variable()
            generated_code += (
                f"{COMMAND[INT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
            )
            return generated_code, new_retval_var

        # both are floats
        elif self.is_variable_float(term_retval_var) and (
            self.is_variable_float(factor_retval_var)
        ):
            new_retval_var = self.variable_generator.get_new_float_variable()
            generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
            return generated_code, new_retval_var

        # term is float factor is int, need to cast
        elif self.is_variable_float(term_retval_var) and (
            self.is_variable_integer(factor_retval_var)
        ):
            new_retval_var = self.variable_generator.get_new_float_variable()
            # we cast factor and then generate the code
            if is_num_integer(factor_retval_var):
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
            new_retval_var = self.variable_generator.get_new_float_variable()
            # we cast factor and then generate the code
            if is_num_integer(term_retval_var):
                term_retval_var += ".0"
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {term_retval_var} {factor_retval_var}"
                return generated_code, new_retval_var
            else:
                new_term = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_term} {term_retval_var}\n{COMMAND[FLOAT]} {new_retval_var} {new_term} {factor_retval_var}"
                return generated_code, new_retval_var

    # this function generates casting code
    def generate_casting_factor(self, expression_code, expression_retval_var, cast):
        # if no cast is actually needed
        if (self.is_variable_integer(expression_retval_var) and cast == INT_CAST) or (
            self.is_variable_float(expression_retval_var) and cast == FLOAT_CAST
        ):
            return expression_code, expression_retval_var

        # we initialize the generated code and the quad command we are going to use
        generated_code, COMMAND = self.initialize_code_and_command_casting_factor(
            expression_code, cast
        )

        # we split to two cases, casting to float and casting to int. Then we split to casting numbers and variables
        if self.is_variable_integer(expression_retval_var) and cast == FLOAT_CAST:
            if is_num_integer(expression_retval_var):
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
            if is_num_float(expression_retval_var):
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

    # this function generated code for a boolfactor from 2 expression and a relop
    # we split again to 4 cases, for correct casting and code
    # if the relop is greater than or equals, or less than or equals, then we generate 4 quad commands instead of 1
    def generate_relop_boolfactor(
        self,
        expression1_code,
        expression1_retval_var,
        relop,
        expression2_code,
        expression2_retval_var,
    ):
        # we initialize the generated code and the quad commands (potentially 2) we are going to use
        generated_code, COMMAND, COMMAND1 = (
            self.initialize_code_and_command_relop_boolfactor(
                expression1_code, relop, expression2_code
            )
        )

        # both are integers
        if (
            self.is_variable_integer(expression1_retval_var)
        ) and self.is_variable_integer(expression2_retval_var):
            new_retval_var = self.variable_generator.get_new_int_variable()
            # we generate 4 commands instead of 1
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                # we create 3 new variables, set into the first one the result of less or greater, into the second one the result of equals,
                # then add both results to the third variable and check if greater than 0 to mimic an 'or'. We save the result into a 4th variable
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[INT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}\n\
{COMMAND1[INT]} {new_retval_var2} {expression1_retval_var} {expression2_retval_var}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            # we generate 1 command
            else:
                generated_code += f"{COMMAND[INT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}"
                return generated_code, new_retval_var

        # both are floats
        elif (
            self.is_variable_float(expression1_retval_var)
        ) and self.is_variable_float(expression2_retval_var):
            new_retval_var = self.variable_generator.get_new_int_variable()
            # we generate 4 commands instead of 1
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                # we create 3 new variables, set into the first one the result of less or greater, into the second one the result of equals,
                # then add both results to the third variable and check if greater than 0 to mimic an 'or'. We save the result into a 4th variable
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {expression1_retval_var} {expression2_retval_var}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            # we generate one command
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {expression2_retval_var}"
                return generated_code, new_retval_var

        # expression1 is float expression2 is int, need to cast
        elif (
            self.is_variable_float(expression1_retval_var)
        ) and self.is_variable_integer(expression2_retval_var):
            # first we cast
            new_retval_var = self.variable_generator.get_new_int_variable()
            if is_num_integer(expression2_retval_var):
                expression2_retval_var += ".0"
                new_expression2 = expression2_retval_var
            else:
                new_expression2 = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression2} {expression2_retval_var}\n"

            # now we generate 4 commands instead of 1
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                # we create 3 new variables, set into the first one the result of less or greater, into the second one the result of equals,
                # then add both results to the third variable and check if greater than 0 to mimic an 'or'. We save the result into a 4th variable
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression2}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {expression1_retval_var} {new_expression2}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            # here we generate 1 command
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {expression1_retval_var} {new_expression2}"
                return generated_code, new_retval_var

        # expression1 is int expression2 is float, need to cast
        elif (
            self.is_variable_integer(expression1_retval_var)
        ) and self.is_variable_float(expression2_retval_var):
            # first we cast
            new_retval_var = self.variable_generator.get_new_int_variable()
            if is_num_integer(expression1_retval_var):
                expression1_retval_var += ".0"
                new_expression1 = expression1_retval_var
            else:
                new_expression1 = self.variable_generator.get_new_float_variable()
                generated_code += f"ITOR {new_expression1} {expression1_retval_var}\n"
            # we generate 4 commands instead of 1
            if (
                relop == RELOP_GREATER_THAN_OR_EQUALS
                or relop == RELOP_LESS_THAN_OR_EQUALS
            ):
                # we create 3 new variables, set into the first one the result of less or greater, into the second one the result of equals,
                # then add both results to the third variable and check if greater than 0 to mimic an 'or'. We save the result into a 4th variable
                new_retval_var2 = self.variable_generator.get_new_int_variable()
                new_retval_var3 = self.variable_generator.get_new_int_variable()
                new_retval_var4 = self.variable_generator.get_new_int_variable()
                generated_code += f"""{COMMAND[FLOAT]} {new_retval_var} {new_expression1} {expression2_retval_var}\n\
{COMMAND1[FLOAT]} {new_retval_var2} {new_expression1} {expression2_retval_var}\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
                return generated_code, new_retval_var4
            # here we generate one command
            else:
                generated_code += f"{COMMAND[FLOAT]} {new_retval_var} {new_expression1} {expression2_retval_var}"
                return generated_code, new_retval_var

    # this function generates code for a 'not' boolfactor with a boolexpr
    def generate_not_boolfactor(self, boolexpr_code, boolexpr_retval_var):
        # we calculate 1 - boolexpr and then it is !boolexpr (1 - 0 = 1, 1 - 1 = 0)
        generated_code = f"{boolexpr_code}\n"
        new_retval_var = self.variable_generator.get_new_int_variable()
        generated_code += f"ISUB {new_retval_var} 1 {boolexpr_retval_var}"
        return generated_code, new_retval_var

    # this function generates code for an 'and' boolterm, from a boolterm and a boolfactor
    def generate_and_boolterm(
        self, boolterm_code, boolterm_retval_var, boolfactor_code, boolfactor_retval_var
    ):
        # we calculate into var boolterm != 0, into var2 boolfactor != 0, then multiply both into var 3 - this
        # gives us an AND of boolterm and boolfactor.
        generated_code = f"{boolterm_code}\n{boolfactor_code}\n"
        new_retval_var = self.variable_generator.get_new_int_variable()
        new_retval_var2 = self.variable_generator.get_new_int_variable()
        new_retval_var3 = self.variable_generator.get_new_int_variable()
        new_retval_var4 = self.variable_generator.get_new_int_variable()
        generated_code += f"""INQL {new_retval_var} {boolterm_retval_var} 0\n\
INQL {new_retval_var2} {boolfactor_retval_var} 0\n\
IMLT {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
        return generated_code, new_retval_var4

    # this function generates code for an 'or' boolterm, from a boolexpr and a boolterm
    def generate_or_boolexpr(
        self, boolexpr_code, boolexpr_retval_var, boolterm_code, boolterm_retval_var
    ):
        # we calculate into var boolexpr != 0, into var2 boolterm != 0, then add both into var 3 - this
        # gives us an OR of boolexpr and boolterm.
        generated_code = f"{boolexpr_code}\n{boolterm_code}\n"
        new_retval_var = self.variable_generator.get_new_int_variable()
        new_retval_var2 = self.variable_generator.get_new_int_variable()
        new_retval_var3 = self.variable_generator.get_new_int_variable()
        new_retval_var4 = self.variable_generator.get_new_int_variable()
        generated_code += f"""INQL {new_retval_var} {boolexpr_retval_var} 0\n\
INQL {new_retval_var2} {boolterm_retval_var} 0\n\
IADD {new_retval_var3} {new_retval_var} {new_retval_var2}\n\
IGRT {new_retval_var4} {new_retval_var3} 0"""
        return generated_code, new_retval_var4

    #######################################

    def generate_if_code(
        self,
        boolexpr_code,
        boolexpr_retval_var,
        positive_stmt_code,
        negative_stmt_code,
        positive_label,
        negative_label,
    ):
        # the 'positive' label is the label that leads to the code that is executed if boolexpr is true,
        # and the 'negative' label leads to the code that is executed if boolexpr is false.
        generated_code = f"""{boolexpr_code}\n\
JMPZ {negative_label} {boolexpr_retval_var}\n\
{positive_stmt_code}\n\
JUMP {positive_label}\n\
{negative_label}:\n\
{negative_stmt_code}\n\
{positive_label}:"""
        return generated_code

    def generate_while_code(
        self,
        boolexpr_code,
        boolexpr_retval_var,
        stmt_code,
        while_entry_label,
        while_exit_label,
    ):
        # the 'while_entry' label is the label that leads to the calculation of boolexpr and the while body,
        # and the 'while_exit' label leads to exiting the while loop.
        generated_code = f"""{while_entry_label}:\n\
{boolexpr_code}\n\
JMPZ {while_exit_label} {boolexpr_retval_var}\n\
{stmt_code}\n\
JUMP {while_entry_label}\n\
{while_exit_label}:"""
        return generated_code

    # this function initializes the code and command before calculating an expression with an addop
    def initialize_code_and_command_expression(self, expression_code, addop, term_code):
        generated_code = ""
        # if expression_code or term_code is "", this means that we don't need to add their code
        # (this is done to get rid of obsolete new lines)
        if expression_code != "":
            generated_code += f"{expression_code}\n"
        if term_code != "":
            generated_code += f"{term_code}\n"
        if addop == PLUS:
            COMMAND = {INT: "IADD", FLOAT: "RADD"}
        else:
            COMMAND = {INT: "ISUB", FLOAT: "RSUB"}
        return generated_code, COMMAND

        # this function initializes the code and command before calculating a term with a mulop

    def initialize_code_and_command_term(self, term_code, mulop, factor_code):
        generated_code = ""
        # if term_code or factor_code is "", this means that we don't need to add their code
        # (this is done to get rid of obsolete new lines)
        if term_code != "":
            generated_code += f"{term_code}\n"
        if factor_code != "":
            generated_code += f"{factor_code}\n"
        if mulop == MULTIPLY:
            COMMAND = {INT: "IMLT", FLOAT: "RMLT"}
        else:
            COMMAND = {INT: "IDIV", FLOAT: "RDIV"}
        return generated_code, COMMAND

    # this function initializes the code and command before calculating a casting factor
    def initialize_code_and_command_casting_factor(self, expression_code, cast):
        generated_code = ""
        # if expression_code is "", this means that we don't need to add their code
        # (this is done to get rid of obsolete new lines)
        if expression_code != "":
            generated_code += f"{expression_code}\n"
        if cast == INT_CAST:
            COMMAND = "RTOI"
        else:
            COMMAND = "ITOR"
        return generated_code, COMMAND

    # this function initializes the code and command before calculating a relop boolfactor
    def initialize_code_and_command_relop_boolfactor(
        self, expression1_code, relop, expression2_code
    ):
        generated_code = ""
        # if expression1_code or expression2_code is "", this means that we don't need to add their code
        # (this is done to get rid of obsolete new lines)
        COMMAND = ""
        COMMAND1 = ""
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
        return generated_code, COMMAND, COMMAND1


class VariableGenerator:
    # designates between int and float variable names
    def __init__(self, symbol_table):
        self.int_variable_count = 0
        self.float_variable_count = 0
        self.symbol_table: SymbolTable = symbol_table

    """
        Each variable that we create during the code generation has a special prefix:
        ti (temporary int) for integer variables,
        and tf (temporary float) for float variables.
        The number after ti or tf indicates the order in which they were created,
        and is added to prevent two variables with the same name.
        A check is also conducted to make sure that a variable with the same name doesn't 
        already exist, only then we actually create the variable.
        Else we increment the count by 1.
    """

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


class LabelGenerator:
    def __init__(self):
        self.label_count = 0

        """
            The lable generator has similar logic to the variable generator, 
            but is much simpler for 2 reasons:
            1. A label is only created by us generating the code therefore we don't need
            to check if a label already exists
            2. Labels only have one 'type' in quad (in contrast to variables which have 2 types, int and float)
        """

    def get_new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
