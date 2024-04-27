import re
import sys

INT = "int"
FLOAT = "float"
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
        )  # ceck if there is a decimal point, indicating it's a float
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
    return clean_newlines(code) + "\nHALT"


if __name__ == "__main__":
    print(is_float("3.14"))  # Output: True
    print(is_float("5"))  # Output: False
    print(is_float("3.0"))

    print(is_integer("3"))  # Output: True
    print(is_integer("3.0"))  # Output: False

    print(float_to_int_str("3.8"))
