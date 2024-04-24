import sys

INT = "int"
FLOAT = "float"
PLUS = "+"
MINUS = "-"


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def legal_filename(filename: str):
    if not filename.endswith(".ou"):
        return False
    return True
