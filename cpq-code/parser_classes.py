""" Written by Ilai Azaria, 2024
    This module defines the classes used for the parser. Specifically we only have the
    'CodeConstruct' class, which is the data structure used in generating code
"""


# this is the code construct class
class CodeConstruct:
    """
    Each part of the code that we generate during parsing is represented by a CodeConstruct object.
    This object contains two values, the generated code (a string) and the retval_var (also a string)
    The generated code simply represents the generated code of that part - and the retval var represents
    the name of the variable where that code's calculations (if exist) were saved.
    For example for an expression, a boolexpr, a factor we would need a retval var to calculate from them.
    But for a stmt this is not needed - we will only use the stmt's code and put it in the right place.
    """

    def __init__(self, generated_code: str, retval_var: str = ""):
        self.generated_code = generated_code
        self.retval_var = retval_var
