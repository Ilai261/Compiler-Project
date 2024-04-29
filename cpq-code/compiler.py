from cpq_lexer import CpqLexer
from cpq_parser import CpqParser
from parser_classes import CodeConstruct
from symbol_table import SymbolTable
from utils import (
    FILE_READING_ERROR,
    ILLEGAL_FILENAME_ERROR,
    PARSING_ERROR_MSG,
    error_print,
    legal_filename,
    raw_filename,
    reparse_output,
)


class Compiler:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.lexer = CpqLexer(self.symbol_table)
        self.parser = CpqParser(self.symbol_table)

    def run_on_file(self, filename: str):
        try:
            if not legal_filename(filename):
                error_print(ILLEGAL_FILENAME_ERROR)
                raise Exception
            with open(filename, "r") as file:
                try:
                    input_text = file.read()
                    result: CodeConstruct = self.parser.parse(
                        self.lexer.tokenize(input_text)
                    )
                    # if errors were detected we don't create an output file
                    if (
                        not self.lexer.errors_detected
                        and not self.parser.errors_detected
                    ):
                        raw_file = raw_filename(filename)
                        # create the output file as .qud
                        with open(f"{raw_file}.qud", "w") as new_file:
                            new_file.write(reparse_output(result.generated_code))
                except Exception as e:
                    print(type(e).__name__, "–", e)
                    error_print(PARSING_ERROR_MSG)
        except Exception as e:
            print(type(e).__name__, "-", e)
            error_print(FILE_READING_ERROR)
