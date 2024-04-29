""" Written by Ilai Azaria, 327650255
    This is an utility module
"""

import re
import sys

INT = "int"
FLOAT = "float"
INT_VAR = "ti"
FLOAT_VAR = "tf"
PLUS = "+"
MINUS = "-"
MULTIPLY = "*"
DIVIDE = "/"
INT_CAST = "static_cast<int>"
FLOAT_CAST = "static_cast<float>"
RELOP_EQUALS = "=="
RELOP_NOT_EQUALS = "!="
RELOP_GREATER_THAN_OR_EQUALS = ">="
RELOP_LESS_THAN_OR_EQUALS = "<="
RELOP_REALLY_GREATER_THAN = ">"
RELOP_REALLY_LESS_THAN = "<"
SIGNATURE_LINE = "-------Ilai Azaria 327650255-------"
PARSING_ERROR_MSG = (
    "Compilation failed: A runtime error occured while trying to parse your file..."
)
ILLEGAL_FILENAME_ERROR = "Error: Filename doesn't have .ou at the end of it..."
TOO_MANY_ARGV_PARAMS_ERROR = "Too many parameters given to argv. Please provide only the cpl filename! Aborting..."
NOT_ENOUGH_ARGV_PARAMS_ERROR = (
    "Not enough parameters given to argv. Please provide the cpl filename! Aborting..."
)
FILE_READING_ERROR = "Error while trying to read your file..."


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def legal_filename(filename: str):
    if not filename.endswith(".ou"):
        return False
    return True


def is_float(string):
    try:
        float(string)
        return (
            "." in string
        )  # check if there is a decimal point, indicating it's a float
    except ValueError:
        return False


def is_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def float_to_int_str(float_str):
    try:
        float_val = float(float_str)
        int_val = int(float_val)
        return str(int_val)
    except ValueError:
        print("Error: Input is not a valid float representation.")
        return None


def clean_newlines(code: str):
    # we use regular expressions to replace consecutive \n with single \n, and also remove leading \n
    code = code.lstrip("\n")
    cleaned_text = re.sub(r"\n{2,}", "\n", code)
    return cleaned_text


def reparse_output(code: str):
    return clean_newlines(code) + f"\nHALT\n{SIGNATURE_LINE}"


def raw_filename(filename: str):
    return filename.rstrip(".ou")


if __name__ == "__main__":
    pass
