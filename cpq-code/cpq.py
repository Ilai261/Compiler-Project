""" Written by Ilai Azaria, 2024
    This is the main module for running the compiler
"""

import sys

sys.path.insert(0, "sly-master\\src\\")
from compiler import Compiler
from utils import (
    NOT_ENOUGH_ARGV_PARAMS_ERROR,
    SIGNATURE_LINE,
    TOO_MANY_ARGV_PARAMS_ERROR,
    error_print,
)

if __name__ == "__main__":
    error_print(SIGNATURE_LINE)
    cpq_compiler = Compiler()
    if len(sys.argv) > 2:  # more than one parameter
        error_print(TOO_MANY_ARGV_PARAMS_ERROR)
    elif len(sys.argv) < 2:
        error_print(NOT_ENOUGH_ARGV_PARAMS_ERROR)
    else:
        cpq_compiler.run_on_file(sys.argv[1])
