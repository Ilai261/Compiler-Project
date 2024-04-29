""" Written by Ilai Azaria, 327650255
    This module defines the 'CodeConstruct' class, which is the data structure used in generating code
"""


class CodeConstruct:
    def __init__(self, generated_code: str, retval_var: str = ""):
        self.generated_code = generated_code
        self.retval_var = retval_var
