import sys

INT = "int"
FLOAT = "float"
PLUS = "+"
MINUS = "-"
MULTIPLY = "*"
DIVIDE = "/"
INT_CAST = "static_cast<int>"
FLOAT_CAST = "static_cast<float>"


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


if __name__ == "__main__":
    print(is_float("3.14"))  # Output: True
    print(is_float("5"))  # Output: False
    print(is_float("3.0"))

    print(is_integer("3"))  # Output: True
    print(is_integer("3.0"))  # Output: False

    print(float_to_int_str("3.8"))
