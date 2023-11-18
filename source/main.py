from stringcolor import *
from strings_with_arrows import *
import string

DIGITS = '0123456789'
LETTERSDIGITS = DIGITS + string.ascii_letters
KEYWORDS = ['def', 'manip']
TT_NUM = 'NUM'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_POWER = 'POWER'
TT_KEYWORD = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_EQ = 'EQ'
TT_EOF = 'EOF'
TT_COLON = "COLON"

class Error:
    def __init__(self, pos_start, pos_end, error_code, details, context=None):
        self.error_code = error_code
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
        self.context = context
        if self.error_code == 101:
            self.error_name = "Illegal Character"
        if self.error_code == 201:
            self.error_name = "Expected Character"
        if self.error_code == 202:
            self.error_name = "Unclosed Grouping"
        if self.error_code == 301:
            self.error_name = "Division by zero"
        if self.error_code == 302:
            self.error_name = "Symbol not defined"
        if self.error_code == 303:
            self.error_name = "Symbol already defined"
        if self.error_code == 304:
            self.error_name = f"Cannot operate {details[0]} with {details[1]}"
    def as_string(self):
        if self.error_code > 300:
            result = self.generate_traceback()
            if self.error_code == 304:
                self.details = ''
            result += cs(f'Error code {self.error_code} - {self.error_name}: {self.details}', "Red2")
            result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        else:
            result = cs(f'Error code {self.error_code} - {self.error_name}: {self.details}', "Red4")
            result += cs(f'\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}', "Red3")
            result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
        
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = cs(f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result, "red3")
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return cs('Traceback (most recent call last):\n' + result, "red4")
    
class Context:
    def __init__(self,display_name,parent=None,parent_entry_pos=None):
        self.display_name = display_name
        self.parent_entry_pos = parent_entry_pos
        self.parent = parent
        self.symbol_table = None

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None
        
    def get(self,name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set_(self,name,value):
        self.symbols[name] = value
        
    def remove(self,name):
        del self.symbols[name]

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
            
        if pos_end:
            self.pos_end = pos_end
            
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
        
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
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS,pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL,pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV,pos_start=self.pos))
                self.advance()
            elif self.current_char == ":":
                tokens.append(Token(TT_COLON,pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN,pos_start=self.pos))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LBRACE,pos_start=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RBRACE,pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POWER,pos_start=self.pos))
                self.advance()
            elif self.current_char == "=":
                tokens.append(Token(TT_EQ,pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS + ".":
                tokens.append(self.make_number())
            elif self.current_char in string.ascii_letters:
                tokens.append(self.make_words())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], Error(pos_start, self.pos, 101, '"' + char + '"')
            
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
            
        if dot_count == 1:
            return Token(TT_NUM, float(num_str), pos_start, self.pos)
        elif dot_count == 0:
            return Token(TT_NUM, int(num_str), pos_start, self.pos)
        
    def make_words(self):
        string = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in LETTERSDIGITS + '_':
            string += self.current_char
            self.advance()
        if string in KEYWORDS:
            return Token(TT_KEYWORD, string, pos_start, self.pos)
        else:
            return Token(TT_IDENTIFIER, string, pos_start, self.pos)

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
        
class VarAssignNode:
    def __init__(self, var_name_tok, value_node, var_type):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.var_type = var_type
        
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end
        
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
        
    def __repr__(self):
        return f'{self.tok}'
    
class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
        
    def __repr__(self):
        return f'{self.tok}'
    
class NoneTypeNode:
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
        
    def __repr__(self):
        return 'None'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
        
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.node = node
        self.op_tok = op_tok
        
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
        
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
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
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            pos_startt = self.current_tok.pos_start.copy()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            return res.failure(Error(pos_startt, self.current_tok.pos_end, 202, "Parenthesis"))        
        elif tok.type == TT_NUM:
            res.register(self.advance())
            return res.success(NumberNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            if tok.value == "False":
                return res.success(BooleanNode(tok))
            if tok.value == "True":
                return res.success(BooleanNode(tok))
            if tok.value == "None":
                return res.success(NoneTypeNode(tok))
            return res.success(VarAccessNode(tok))
        return res.failure(Error(tok.pos_start, tok.pos_end, 201, "Expression or Number"))
        
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, "Operation"))
        return res
    
    def power(self):
        return self.bin_op(self.factor, [TT_POWER])
    
    def term(self):
        return self.bin_op(self.power, [TT_MUL, TT_DIV])
    
    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'def') or self.current_tok.matches(TT_KEYWORD, 'manip'):
            var_type = self.current_tok.value
            res.register(self.advance())
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register(self.advance())
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register(self.advance())
            parenpos = self.current_tok.pos_start.copy()
            
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Identifier'))
            
            var_name = self.current_tok
            res.register(self.advance())
            
            if self.current_tok.type != TT_EQ:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"="'))
            
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register(self.advance())
            
            return res.success(VarAssignNode(var_name, expr, var_type))
            
        return self.bin_op(self.term, [TT_PLUS, TT_MINUS])
    
    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
    
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
        
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self
        
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
        self.type = "Number"
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, Error(
                    other.pos_start, other.pos_end,
                    301, "", self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )
        
    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(self.value)
    
class Boolean:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
        self.type = "Boolean"
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )

    def subbed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )

    def multed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(bool(self.value))

class NoneType:
    def __init__(self):
        self.set_pos()
        self.set_context()
        self.type = "None"
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )

    def subbed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )

    def multed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )
    
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return "None"
        
    
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'[INTERNAL] Error code 401 - No visit method defnied: {type(node).__name__}')
    
    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        
        if not value:
            return res.failure(Error(node.pos_start, node.pos_end, 302, var_name, context))
        
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        var_type = node.var_type
        
        if res.error:
            return res
        
        if var_type == 'def':
            if context.symbol_table.get(var_name):
                return res.failure(Error(node.pos_start, node.pos_end, 303, var_name, context))
            context.symbol_table.set_(var_name, value)
        else:
            if not context.symbol_table.get(var_name):
                return res.failure(Error(node.pos_start, node.pos_end, 302, var_name, context))
            context.symbol_table.set_(var_name, value)
            
        return res.success(value)
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_BooleanNode(self, node, context):
        if node.tok.value == "False":
            node.tok.value = 0
        else:
            node.tok.value = 1
        return RTResult().success(Boolean(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_NoneTypeNode(self, node, context):
        return RTResult().success(NoneType().set_context(context).set_pos(node.pos_start, node.pos_end))
        
    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        if node.op_tok.type == TT_PLUS:
            result,error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result,error = left.subbed_by(right)
        elif node.op_tok.type == TT_DIV:
            result,error = left.dived_by(right)
        elif node.op_tok.type == TT_MUL:
            result,error= left.multed_by(right)
        elif node.op_tok.type == TT_POWER:
            result,error= left.powed_by(right)
        
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))
        
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res
        
        error = None
        
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
            
        if error:
            return res.failure(error)
        else:    
            return res.success(number.set_context(context).set_pos(node.pos_start, node.pos_end))
        
global_symbol_table = SymbolTable()
global_symbol_table.set_("True", Boolean(1))
global_symbol_table.set_("False", Boolean(0))
global_symbol_table.set_("None", NoneType())
        
def run(text):
    lexer = Lexer("<stdin>", text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    
    interpreter = Interpreter()
    context = Context('<shell>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    
    return result.value, result.error