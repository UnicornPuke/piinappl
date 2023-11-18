from stringcolor import *
from strings_with_arrows import *

DIGITS = '0123456789'

TT_NUM		= 'NUM'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_NUM = 'NUM'

class Error:
    def __init__(self, pos_start, pos_end, error_code, details):
        self.error_code = error_code
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
        if self.error_code == 101:
            self.error_name = "Illegal Character"
        
    def as_string(self):
        result = cs(f'Error code {self.error_code} - {self.error_name}: {self.details}', "Red4")
        result += cs(f'\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}', "Red3")
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
class Lexer:
    def __init__(self, fn, text):
        self.text = text
        self.fn = fn
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        
    def make_tokens(self):
        tokens = []
        
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LBRACE))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RBRACE))
                self.advance()
            elif self.current_char in DIGITS + ".":
                tokens.append(self.make_number())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], Error(pos_start, self.pos, 101, '"' + char + '"')
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
            
        if dot_count == 1:
            return Token(TT_NUM, float(num_str))
        elif dot_count == 0:
            return Token(TT_NUM, int(num_str)) 
        
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        
    def __repr__(self):
        return f'{self.tok}'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
        
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def factor(self):
        tok = self.current_tok
        
        if tok.type == TT_NUM:
            self.advance()
            return NumberNode(tok)
        
    def parse(self):
        res = self.expr()
        return res
    
    def term(self):
        return self.bin_op(self.factor, [TT_MUL, TT_DIV])
    
    def expr(self):
        return self.bin_op(self.term, [TT_PLUS, TT_MINUS])
    
    def bin_op(self, func, ops):
        left = func()
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)
        return(left)
        
def run(text):
    lexer = Lexer("<stdin>", text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast, None