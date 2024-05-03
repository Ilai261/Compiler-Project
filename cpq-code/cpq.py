""" Written by Ilai Azaria, 2024
    This is the main module for running the compiler
"""

import sys

# we insert sly library into the path
# this insertion is relative, therefore it's important to run cpq.py from the folder containing cpq-code
sys.path.insert(0, "sly-master\\src\\")
from compiler import Compiler
from utils import (
    NOT_ENOUGH_ARGV_PARAMS_ERROR,
    SIGNATURE_LINE,
    TOO_MANY_ARGV_PARAMS_ERROR,
    error_print,
)


# we print a signature to stderr, check if the length of argv is legal and if it is-
# we call the compiler to run on the file that the user supplied
def main():
    error_print(SIGNATURE_LINE)
    cpq_compiler = Compiler()
    if len(sys.argv) > 2:  # more than one parameter
        error_print(TOO_MANY_ARGV_PARAMS_ERROR)
    elif len(sys.argv) < 2:
        error_print(NOT_ENOUGH_ARGV_PARAMS_ERROR)
    else:
        cpq_compiler.run_on_file(sys.argv[1])


if __name__ == "__main__":
    main()
