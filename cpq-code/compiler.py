from cpq_lexer import CpqLexer
from cpq_parser import CpqParser
from parser_classes import CodeConstruct
from symbol_table import SymbolTable
from utils import error_print, legal_filename

PARSING_ERROR_MSG = "A runtime error occured while trying to parse your file..."


class Compiler:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.lexer = CpqLexer(self.symbol_table)
        self.parser = CpqParser(self.symbol_table)

    def run_on_file(self, filename: str):
        error_print("-------Ilai Azaria 327650255-------")
        try:
            if not legal_filename(filename):
                error_print("error: filename doesn't have .ou at the end of it...")
                raise Exception
            with open(filename, "r") as file:
                try:
                    input_text = file.read()
                    for tok in self.lexer.tokenize(input_text):
                        print("type=%r, value=%r" % (tok.type, tok.value))
                    result: CodeConstruct = self.parser.parse(
                        self.lexer.tokenize(input_text)
                    )
                    # for now we print the code, will check print variable, and create a file soon
                    print(
                        f"The code generated is:\n{result.generated_code}"
                    )  # needs to change to '.generated_code'
                    print(f"final symbol table: {self.symbol_table.table}")
                    # after we print the new code to the file, we need to add a signature line at the end
                except Exception as e:
                    print(type(e).__name__, "–", e)
                    error_print(f"error: Compilation failed: {PARSING_ERROR_MSG}")
        except:
            print(type(e).__name__, "–", e)
            error_print(f"error: could not open file {filename}...")
