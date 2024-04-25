from code_generator import CodeGenerator
from cpq_lexer import CpqLexer
from parser_classes import CodeConstruct
from sly import Parser
from symbol_table import SymbolTable
from utils import FLOAT, INT


class CpqParser(Parser):
    tokens = CpqLexer.tokens

    @_("declarations stmt_block")
    def program(self, p):
        return CodeConstruct(
            generated_code=(
                p.declarations.generated_code + "\n" + p.stmt_block.generated_code
            )
        )

    @_("declarations declaration")
    def declarations(self, p):
        return CodeConstruct(
            generated_code=(
                p.declarations.generated_code + "\n" + p.declaration.generated_code
            )
        )

    @_("empty")
    def declarations(self, p):
        return CodeConstruct(generated_code="")

    @_("idlist COLON type SEMICOLON")
    def declaration(self, p):
        for variable in p.idlist:
            self.symbol_table.change_variable_type(
                variable_name=variable, variable_type=p.type
            )
        return CodeConstruct(generated_code="")

    @_("INT")
    def type(self, p):
        return INT

    @_("FLOAT")
    def type(self, p):
        return FLOAT

    @_("idlist COMMA ID")
    def idlist(self, p):
        p.idlist.append(p.ID)
        return p.idlist

    @_("ID")
    def idlist(self, p):
        return [
            p.ID,
        ]

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
        return CodeConstruct(generated_code=p[0].generated_code)

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        expression: CodeConstruct = p.expression
        retval_var = expression.retval_var
        generated_code = self.code_generator.generate_assignment_stmt(
            expression_code=expression.generated_code,
            id=p.ID,
            expression_var=retval_var,
        )
        return CodeConstruct(generated_code=generated_code)

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
        return p.stmtlist

    @_("stmtlist stmt")
    def stmtlist(self, p):
        return CodeConstruct(
            generated_code=p.stmtlist.generated_code + "\n" + p.stmt.generated_code
        )

    @_("empty")
    def stmtlist(self, p):
        return CodeConstruct(generated_code="")

    @_("boolexpr OR boolterm", "boolterm")
    def boolexpr(self, p):
        return ""

    @_("boolterm AND boolfactor", "boolfactor")
    def boolterm(self, p):
        return ""

    @_("NOT LPAREN boolexpr RPAREN", "expression RELOP expression")
    def boolfactor(self, p):
        return ""

    @_("expression ADDOP term")
    def expression(self, p):
        # take term's last retval and addop it to expression's retval, this is the new expression retval
        expression: CodeConstruct = p.expression
        expression_retval_var = expression.retval_var
        term: CodeConstruct = p.term
        term_retval_var = term.retval_var
        generated_code, retval_var = self.code_generator.generate_expression(
            expression_code=expression.generated_code,
            expression_retval_var=expression_retval_var,
            addop=p.ADDOP,
            term_code=term.generated_code,
            term_retval_var=term_retval_var,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("term")
    def expression(self, p):
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        # take factor's last retval and mulop it to term's retval, this is the new term retval
        term: CodeConstruct = p.term
        term_retval_var = term.retval_var
        factor: CodeConstruct = p.factor
        factor_retval_var = factor.retval_var
        generated_code, retval_var = self.code_generator.generate_term(
            term_code=term.generated_code,
            term_retval_var=term_retval_var,
            mulop=p.MULOP,
            factor_code=factor.generated_code,
            factor_retval_var=factor_retval_var,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("factor")
    def term(self, p):
        return p.factor

    @_("LPAREN expression RPAREN")
    def factor(self, p):
        return p.expression

    @_("CAST LPAREN expression RPAREN")
    def factor(self, p):
        return ""

    @_("ID")
    def factor(self, p):
        return CodeConstruct(generated_code="", retval_var=p.ID)

    @_("NUM")
    def factor(self, p):
        return CodeConstruct(generated_code="", retval_var=p.NUM)

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        if p:
            print("Syntax error at token", p.type)
            # Just discard the token and tell the parser it's okay.
            self.errok()
        else:
            print("Syntax error at EOF")

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table: SymbolTable = symbol_table
        self.errors_detected = False
        self.code_generator: CodeGenerator = CodeGenerator(symbol_table)
