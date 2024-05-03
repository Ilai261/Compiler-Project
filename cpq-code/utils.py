""" Written by Ilai Azaria, 2024
    This is a utility module
"""

import re
import sys

# here we have all of the project's constants
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
SIGNATURE_LINE = "-------Ilai Azaria 2024-------"
PARSING_ERROR_MSG = (
    "Compilation failed: A runtime error occured while trying to parse your file..."
)
ILLEGAL_FILENAME_ERROR = "Error: Filename doesn't have .ou at the end of it..."
TOO_MANY_ARGV_PARAMS_ERROR = "Too many parameters given to argv. Please provide only the cpl filename! Aborting..."
NOT_ENOUGH_ARGV_PARAMS_ERROR = (
    "Not enough parameters given to argv. Please provide the cpl filename! Aborting..."
)
FILE_READING_ERROR = "Error while trying to read your file..."


# print to stderr
def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# checks if a filename ends with .ou
def legal_filename(filename: str):
    if not filename.endswith(".ou"):
        return False
    return True


# checks if a string is a float number
def is_num_float(string):
    try:
        float(string)
        return (
            "." in string
        )  # check if there is a decimal point, indicating it's a float
    except ValueError:
        return False


# checks if a string is an integer number
def is_num_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


# converts a float number string to an integer number string
def float_to_int_str(float_str):
    try:
        float_val = float(float_str)
        int_val = int(float_val)
        return str(int_val)
    except ValueError:
        print("Error: Input is not a valid float representation.")
        return None


# strips a string of newlines at the beginning and replaces 2 or more consecutive newlines with one newline
def clean_newlines(code: str):
    # we use regular expressions to replace consecutive \n with single \n, and also remove leading \n
    code = code.lstrip("\n")
    cleaned_text = re.sub(r"\n{2,}", "\n", code)
    return cleaned_text


# cleans newlines and adds a 'HALT' and a signature line in the end of the string
def reparse_output(code: str):
    return clean_newlines(code) + f"\nHALT\n{SIGNATURE_LINE}"


# strips a filename of .ou in its end
def raw_filename(filename: str):
    return filename.rstrip(".ou")


if __name__ == "__main__":
    pass
