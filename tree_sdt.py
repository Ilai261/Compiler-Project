import sys
sys.path.insert(0, "sly-master\\src\\")

from sly import Lexer, Parser

class S():
    def __init__(self, val):
        self.val = val

class Tree():
    def __init__(self, val, height):
        self.val = val
        self.height = height

class Treelist():
    def __init__(self, sum, height):
        self.sum = sum
        self.height = height

class TreeLexer(Lexer):
    tokens = { SUM, ZERO, HEIGHT, DOUBLE, NUMBER, LPAREN, RPAREN }
    ignore = ' \t'

    # Tokens
    SUM = r'sum'
    ZERO = r'zero'
    HEIGHT = r'height'
    DOUBLE = r'double'
    NUMBER = r'[0-9]+'
    
    # Special symbols
    LPAREN = r'\('
    RPAREN = r'\)'

    # Ignored pattern
    ignore_newline = r'\n+'

    def __init__(self) -> None:
        super().__init__()
        self.symbol_table = {"this is a symbol table!": 5,}
        
    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class TreeParser(Parser):
    tokens = TreeLexer.tokens

    @_('tree')
    def s(self, p):
        return S(p.tree.val)

    @_('LPAREN SUM treelist RPAREN')
    def tree(self, p):
        return Tree(p.treelist.sum, p.treelist.height + 1)

    @_('LPAREN ZERO treelist RPAREN')
    def tree(self, p):
        return Tree(0, p.treelist.height + 1)

    @_('LPAREN HEIGHT treelist RPAREN')
    def tree(self, p):
        return Tree(p.treelist.height + 1, p.treelist.height + 1)

    @_('LPAREN DOUBLE tree RPAREN')
    def tree(self, p):
        return Tree(p.tree.val * 2, p.tree.height + 1)

    @_('NUMBER')
    def tree(self, p):
        return Tree(int(p.NUMBER), 0)
    
    @_('treelist tree')
    def treelist(self, p):
        return Treelist(p.treelist.sum + p.tree.val, max(p.treelist.height, p.tree.height))
    
    @_('tree')
    def treelist(self, p):
        return Treelist(p.tree.val, p.tree.height)
    
    def error(self, p):
        print(f"We have a parsing error at line {p.lineno}!")
        if not p:
            print("End of File!")
            return

        # Read ahead looking for a closing ')'
        while True:
            tok = next(self.tokens, None)
            if not tok or tok.type == 'RPAREN':
                break
        self.restart()



if __name__ == '__main__':
    lexer = TreeLexer()
    print(lexer.symbol_table)
    parser = TreeParser()
    filename = sys.argv[1]
    file = open(filename,'r')
    input_text = file.read()
    if input_text:
        try:
            result = parser.parse(lexer.tokenize(input_text))
            print(f"The tree value is: {result.val}")
        except Exception:
            print("we had an error! can't print the value of the tree....")
