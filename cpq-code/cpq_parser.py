from code_generator import CodeGenerator
from cpq_lexer import CpqLexer
from parser_classes import CodeConstruct
from sly import Parser
from symbol_table import SymbolTable
from utils import FLOAT, INT, error_print


class CpqParser(Parser):
    tokens = CpqLexer.tokens

    @_("declarations stmt_block")
    def program(self, p):
        generated_code = p.declarations.generated_code + p.stmt_block.generated_code
        return CodeConstruct(generated_code=generated_code)

    @_("declarations declaration")
    def declarations(self, p):
        return CodeConstruct(
            generated_code=(
                p.declarations.generated_code + p.declaration.generated_code
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
        construct: CodeConstruct = p[0]
        return CodeConstruct(generated_code=construct.generated_code)

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        if p.expression.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        if self.symbol_table.get_variable_type(p.ID) is None:
            self.errors_detected = True
            error_print(
                f"error in assignment stmt on line {p.lineno}, tried to assign to non declared variable!.."
            )
            return CodeConstruct(generated_code="")
        expression: CodeConstruct = p.expression
        generated_code = self.code_generator.generate_assignment_stmt(
            expression_code=expression.generated_code,
            id=p.ID,
            expression_var=expression.retval_var,
        )
        if generated_code == False:
            self.errors_detected = True
            error_print(
                f"error in assignment stmt on line {p.lineno}, tried to assign float to int!.."
            )
            generated_code = ""
        return CodeConstruct(generated_code=generated_code)

    @_("INPUT LPAREN ID RPAREN SEMICOLON")
    def input_stmt(self, p):
        if self.symbol_table.get_variable_type(p.ID) is None:
            error_print(
                f"error in input stmt on line {p.lineno}, tried to get input into a non declared variable!.."
            )
            return CodeConstruct(generated_code="")
        return ""

    @_("OUTPUT LPAREN expression RPAREN SEMICOLON")
    def output_stmt(self, p):
        if p.expression.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return ""

    @_("IF LPAREN boolexpr RPAREN stmt ELSE stmt")
    def if_stmt(self, p):
        if p.boolexpr.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return CodeConstruct(generated_code=p.boolexpr.generated_code)

    @_("WHILE LPAREN boolexpr RPAREN stmt")
    def while_stmt(self, p):
        if p.boolexpr.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
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
        generated_code = p.stmtlist.generated_code + "\n" + p.stmt.generated_code
        return CodeConstruct(generated_code=generated_code)

    @_("empty")
    def stmtlist(self, p):
        return CodeConstruct(generated_code="")

    @_("boolexpr OR boolterm")
    def boolexpr(self, p):
        if (
            p.boolexpr.retval_var is None or p.boolterm.retval_var is None
        ):  # then we have an error in boolterm or boolfactor
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return ""

    @_("boolterm")
    def boolexpr(self, p):
        if p.boolterm.retval_var is None:  # then we have an error in boolexpr
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return p.boolterm

    @_("boolterm AND boolfactor")
    def boolterm(self, p):
        if (
            p.boolfactor.retval_var is None or p.boolterm.retval_var is None
        ):  # then we have an error in boolterm or boolfactor
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return ""

    @_("boolfactor")
    def boolterm(self, p):
        if p.boolfactor.retval_var is None:  # then we have an error in boolfactor
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return p.boolfactor

    @_("NOT LPAREN boolexpr RPAREN")
    def boolfactor(self, p):
        if p.boolexpr.retval_var is None:  # then we have an error in boolexpr
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return ""

    @_("expression RELOP expression")
    def boolfactor(self, p):
        if (
            p.expression0.retval_var is None or p.expression1.retval_var is None
        ):  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        expression1: CodeConstruct = p.expression0
        expression2: CodeConstruct = p.expression1
        generated_code, retval_var = self.code_generator.generate_relop_boolfactor(
            expression1_code=expression1.generated_code,
            expression1_retval_var=expression1.retval_var,
            relop=p.RELOP,
            expression2_code=expression2.generated_code,
            expression2_retval_var=expression2.retval_var,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("expression ADDOP term")
    def expression(self, p):
        if (
            p.term.retval_var is None or p.expression.retval_var is None
        ):  # then we have an error in term or expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        # take term's last retval and addop it to expression's retval, this is the new expression retval
        expression: CodeConstruct = p.expression
        term: CodeConstruct = p.term
        generated_code, retval_var = self.code_generator.generate_expression(
            expression_code=expression.generated_code,
            expression_retval_var=expression.retval_var,
            addop=p.ADDOP,
            term_code=term.generated_code,
            term_retval_var=term.retval_var,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("term")
    def expression(self, p):
        if p.term.retval_var is None:  # then we have an error in term
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        if (
            p.factor.retval_var is None or p.term.retval_var is None
        ):  # then we have an error in factor or term
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        # take factor's last retval and mulop it to term's retval, this is the new term retval
        term: CodeConstruct = p.term
        factor: CodeConstruct = p.factor
        generated_code, retval_var = self.code_generator.generate_term(
            term_code=term.generated_code,
            term_retval_var=term.retval_var,
            mulop=p.MULOP,
            factor_code=factor.generated_code,
            factor_retval_var=factor.retval_var,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("factor")
    def term(self, p):
        if p.factor.retval_var is None:  # then we have an error in factor
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return p.factor

    @_("LPAREN expression RPAREN")
    def factor(self, p):
        if p.expression.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        return p.expression

    @_("CAST LPAREN expression RPAREN")
    def factor(self, p):
        if p.expression.retval_var is None:  # then we have an error in expression
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
        expression: CodeConstruct = p.expression
        # we cast the expression into a new variable
        generated_code, retval_var = self.code_generator.generate_casting_factor(
            expression_code=expression.generated_code,
            expression_retval_var=expression.retval_var,
            cast=p.CAST,
        )
        return CodeConstruct(generated_code=generated_code, retval_var=retval_var)

    @_("ID")
    def factor(self, p):
        if self.symbol_table.get_variable_type(p.ID) is None:
            error_print(
                f"error on line {p.lineno}, tried to use a non declared variable!.."
            )
            self.errors_detected = True
            return CodeConstruct(generated_code="", retval_var=None)
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
