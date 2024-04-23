from utils import error_print

INT = "int"
FLOAT = "float"


class SymbolTable:
    def __init__(self):
        self.table: dict[str:str] = {}  # we save each variable's name and type

    def __str__(self) -> str:
        table = "The symbol table:\n----------------------------\n"
        for key, val in self.table.items():
            table += f"variable name: {key}, variable type: {val}\n"
        table += "----------------------------"
        return table

    def add_variable(self, variable_name, variable_type=None):
        self.table[variable_name] = variable_type

    def variable_in_table(self, variable_name):
        return self.table[variable_name]

    # also checks if variable exists - if it doesn't returns False and None
    def get_variable_type(self, variable_name):
        try:
            return self.table[variable_name]
        except Exception:
            error_print(
                f"Error: variable {variable_name} was not found while parsing in the symbol_table..."
            )

    def change_variable_type(self, variable_name, variable_type):
        if not variable_name in self.table.keys():
            error_print(
                f"Error while trying to change a variable {variable_name}'s value in the symbol table: it doesn't exist..."
            )
        else:
            self.table[variable_name] = variable_type
