from code_generator import CodeGenerator
from cpq_lexer import CpqLexer
from sly import Parser
from symbol_table import SymbolTable


class CpqParser(Parser):
    tokens = CpqLexer.tokens

    @_("declarations stmt_block")
    def program(self, p):
        return "nice"

    @_("declarations declaration", "empty")
    def declarations(self, p):
        return ""

    @_("idlist COLON type SEMICOLON")
    def declaration(self, p):
        return ""

    @_("INT", "FLOAT")
    def type(self, p):
        return ""

    @_("idlist COMMA ID", "ID")
    def idlist(self, p):
        return ""

    @_(
        "assignment_stmt",
        "input_stmt",
        "output_stmt",
        "if_stmt",
        "while_stmt",
        "switch_stmt",
        "break_stmt",
        "stmt_block",
    )
    def stmt(self, p):
        return ""

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        return ""

    @_("INPUT LPAREN ID RPAREN SEMICOLON")
    def input_stmt(self, p):
        return ""

    @_("OUTPUT LPAREN expression RPAREN SEMICOLON")
    def output_stmt(self, p):
        return ""

    @_("IF LPAREN boolexpr RPAREN stmt ELSE stmt")
    def if_stmt(self, p):
        return ""

    @_("WHILE LPAREN boolexpr RPAREN stmt")
    def while_stmt(self, p):
        return ""

    ######################## switch and break are ignored
    @_(
        "SWITCH LPAREN expression RPAREN LBRACES caselist DEFAULT COLON stmtlist RBRACES"
    )
    def switch_stmt(self, p):
        return ""

    @_("caselist CASE NUM COLON stmtlist", "empty")
    def caselist(self, p):
        return ""

    @_("BREAK SEMICOLON")
    def break_stmt(self, p):
        return ""

    ######################## switch and break are ignored

    @_("LBRACES stmtlist RBRACES")
    def stmt_block(self, p):
        return ""

    @_("stmtlist stmt", "empty")
    def stmtlist(self, p):
        return ""

    @_("boolexpr OR boolterm", "boolterm")
    def boolexpr(self, p):
        return ""

    @_("boolterm AND boolfactor", "boolfactor")
    def boolterm(self, p):
        return ""

    @_("NOT LPAREN boolexpr RPAREN", "expression RELOP expression")
    def boolfactor(self, p):
        return ""

    @_("expression ADDOP term", "term")
    def expression(self, p):
        return ""

    @_("term MULOP factor", "factor")
    def term(self, p):
        return ""

    @_("LPAREN expression RPAREN", "CAST LPAREN expression RPAREN", "ID", "NUM")
    def factor(self, p):
        return ""

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        print(f"There is a parsing error at line {p.lineno}!")
        if not p:
            print("End of File!")
            return
        self.restart()

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table: SymbolTable = symbol_table
        self.errors_detected = False
        self.code_generator: CodeGenerator = CodeGenerator()
