from sly import Lexer
from utils import error_print


class CpqLexer(Lexer):

    tokens = {SUM, ZERO, HEIGHT, DOUBLE, NUMBER, LPAREN, RPAREN}
    ignore = " \t"

    # Tokens
    SUM = r"sum"
    ZERO = r"zero"
    HEIGHT = r"height"
    DOUBLE = r"double"
    NUMBER = r"[0-9]+"

    # Special symbols
    LPAREN = r"\("
    RPAREN = r"\)"

    # Ignored pattern
    ignore_newline = r"\n+"

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table = symbol_table
        self.errors_detected = False

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        error_print(
            f"error: Error in lexical analysis on line {self.lineno}: Illegal character '%s'"
            % t.value[0]
        )
        self.index += 1
        self.errors_detected = True
