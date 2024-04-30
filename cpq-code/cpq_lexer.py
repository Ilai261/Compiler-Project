""" Written by Ilai Azaria, 2024
    This module defines the Lexer class for the compiler's lexical analysis 
"""

import re

from sly import Lexer
from symbol_table import SymbolTable
from utils import error_print


class CpqLexer(Lexer):

    tokens = {
        BREAK,
        CASE,
        DEFAULT,
        ELSE,
        FLOAT,
        IF,
        INPUT,
        INT,
        OUTPUT,
        SWITCH,
        WHILE,
        LBRACES,
        RBRACES,
        LPAREN,
        RPAREN,
        COMMA,
        COLON,
        SEMICOLON,
        ASSIGN,
        NUM,
        ID,
        RELOP,
        ADDOP,
        MULOP,
        OR,
        AND,
        NOT,
        CAST,
    }

    ignore = " \t\r"  # whitespace
    ignore_newline = r"\n+"

    # comments
    @_(r"(\"[^\"]*\"(?!\\))|(//[^\n]*$|/(?!\\)\*[\s\S]*?\*(?!\\)/)")
    def COMMENT(self, t):
        self.lineno += t.value.count("\n")  # count lines in comment

    # count newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    # Tokens
    BREAK = r"break"
    CASE = r"case"
    DEFAULT = r"default"
    ELSE = r"else"
    FLOAT = r"float"
    IF = r"if"
    INPUT = r"input"
    INT = r"int"
    OUTPUT = r"output"
    SWITCH = r"switch"
    WHILE = r"while"

    # Special symbols
    LBRACES = r"\{"
    RBRACES = r"\}"
    LPAREN = r"\("
    RPAREN = r"\)"
    COMMA = r"\,"
    COLON = r"\:"
    SEMICOLON = r"\;"
    RELOP = r"(==|!=|>=|<=|<|>)"
    ASSIGN = r"\="

    # more tokens
    CAST = r"(static_cast<int>)|(static_cast<float>)"
    NUM = r"([0-9]+\.[0-9]*)|[0-9]+"
    ID = r"[a-zA-Z]([a-zA-Z]|[0-9])*"
    ADDOP = r"[+-]"
    MULOP = r"[*/]"
    OR = r"\|\|"
    AND = r"&&"
    NOT = r"\!"

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table: SymbolTable = symbol_table
        self.errors_detected = False

    def ID(self, t):
        self.symbol_table.add_variable(variable_name=str(t.value))
        return t

    def LBRACES(self, t):
        self.symbol_table.curly_braces_nesting_level += 1
        return t

    def RBRACES(self, t):
        self.symbol_table.curly_braces_nesting_level -= 1
        return t

    def error(self, t):
        error_print(
            f"Error in lexical analysis on line {self.lineno}: Illegal character '%s'"
            % t.value[0]
        )
        self.index += 1
        self.errors_detected = True
