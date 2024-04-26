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

    # if variable already in table - does nothing!
    def add_variable(self, variable_name, variable_type=None):
        if variable_name not in self.table.keys():
            self.table[variable_name] = variable_type

    def has_variable(self, variable_name):
        return variable_name in self.table.keys()

    # also checks if variable exists - if it doesn't returns False and None
    def get_variable_type(self, variable_name):
        try:
            return self.table[variable_name]
        except Exception:
            return False

    def change_variable_type(self, variable_name, variable_type):
        if not variable_name in self.table.keys():
            error_print(
                f"Error while trying to change a variable {variable_name}'s value in the symbol table: it doesn't exist..."
            )
        else:
            self.table[variable_name] = variable_type
