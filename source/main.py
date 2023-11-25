from stringcolor import cs
from strings_with_arrows import *
import string
import math
import random
import time

instancenums = []

DIGITS = '0123456789'
LETTERSDIGITS = DIGITS + string.ascii_letters
KEYWORDS = ['def', 'class','and', 'or', 'not', 'if', 'elif', 'else', 'in', 'to', 'step', 'while', 'for', 'loop', 'func', 'return', 'continue', 'break']
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
TT_EE = 'EE'
TT_NE = 'NE'
TT_GT = 'GT'
TT_LT = 'LT'
TT_GTE = 'GTE'
TT_LTE = 'LTE'
TT_EOF = 'EOF'
TT_COLON = "COLON"
TT_COMMA = "COMMA"
TT_STRING = "STRING"
TT_LSQUARE = "LSQUARE"
TT_RSQUARE = "RSQUARE"
TT_PIPE = "PIPE"
TT_NEWLINE = "NEWLINE"
TT_POINT = "POINT"
# TT_MODULO = "MODULO"
# TT_PLUSEQ = "PLUSEQ"
# TT_MINUSEQ = "MINUSEQ"
# TT_MULEQ = "MULEQ"
# TT_DIVEQ = "DIVEQ"
# TT_MODULOEQ = "MODULOEQ"

class Error:
    def __init__(self, pos_start, pos_end, error_code, details, context=None):
        self.error_code = error_code
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
        self.context = context
        if self.error_code == 101:
            self.error_name = "Illegal Character"
        if self.error_code == 102:
            self.error_name = "Invalid number"
        if self.error_code == 103:
            self.error_name = "Expected Character"
        if self.error_code == 104:
            self.error_name = "Unclosed Grouping"
        if self.error_code == 201:
            self.error_name = "Expected Character"
        if self.error_code == 202:
            self.error_name = "Unclosed Grouping"
        if self.error_code == 203:
            self.error_name = "Cannot continue after expression until new line"
        if self.error_code == 301:
            self.error_name = "Division by zero"
        if self.error_code == 302:
            self.error_name = "Symbol not defined"
        if self.error_code == 303:
            self.error_name = "List must be length"
        if self.error_code == 304:
            self.error_name = f"Cannot operate {details[0]} with {details[1]}"
        if self.error_code == 305:
            self.error_name = f"Cannot manipulate preset symbol"
        if self.error_code == 306:
            self.error_name = f"Cannot use node for loop"
        if self.error_code == 307:
            self.error_name = f"Too many arguments passed into"
        if self.error_code == 308:
            self.error_name = f"Too few arguments passed into"
        if self.error_code == 309:
            self.error_name = f"Item out of index range"
        if self.error_code == 310:
            self.error_name = f"Built-in function doesn't support type"
        if self.error_code == 311:
            self.error_name = f"Couldn't find attribute"
        if self.error_code == 312:
            self.error_name = f"Can't edit attribute"
        if self.error_code == 313:
            self.error_name = f"Value type is not callable"
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
            result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
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
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
        
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
    
    def __repr__(self):
        return(f'{self.idx}, {self.ln}, {self.col}, {self.fn}')

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
            
        if pos_end:
            self.pos_end = pos_end.copy()
            
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
            elif self.current_char in '\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == ":":
                tokens.append(Token(TT_COLON,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "|":
                tokens.append(Token(TT_PIPE,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LBRACE,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RBRACE,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQUARE,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQUARE,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POWER,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA,pos_start=self.pos, pos_end=self.pos))
                self.advance()
            elif self.current_char in ('"'):
                tok, error = self.make_string('"')
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char in ("'"):
                tok, error = self.make_string("'")
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == "!":
                tok, error = self.make_not_equals() 
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char in DIGITS + ".":
                numby, pos = self.make_number()
                if numby == "wazup":
                    return [], Error(pos[0], self.pos, 102, f'"{pos[1]}"')
                tokens.append(numby)
                if pos:
                    tokens.append(pos)
            elif self.current_char in string.ascii_letters + "_":
                tokens.append(self.make_words())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], Error(pos_start, self.pos, 101, '"' + char + '"')
        
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_string(self, type_):
        string = ''
        pos_start = self.pos.copy()
        self.advance()
        while self.current_char != type_ and self.current_char != None:
            string += self.current_char
            self.advance()
            if self.pos.idx == len(self.text):
                return None, Error(pos_start, self.pos, 104, 'String')
        self.advance()
        return Token(TT_STRING, string, pos_start, self.pos), None 
    
    def skip_comment(self):
        self.advance()
        
        while self.current_char != '\n':
            self.advance()
            
        self.advance()
                
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
            pos_end = self.pos.copy()
            self.advance()
            
        if num_str == '.':
            return Token(TT_POINT, pos_start=pos_start), None
        else:
            if num_str[len(num_str)- 1] == '.':
                return Token(TT_NUM, float(num_str.replace(".", "")), pos_start, pos_end), Token(TT_POINT, pos_start=self.pos)
            
        if dot_count == 1:
            return Token(TT_NUM, float(num_str), pos_start, self.pos), None
        elif dot_count == 0:
            return Token(TT_NUM, int(num_str), pos_start, self.pos), None
        
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
        
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, Error(pos_start, self.pos, 103, '"="')
    
    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
            
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
            
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
            
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
        
class IfNode:
    def __init__(self, cases, elsecase):
        self.cases = cases
        self.elsecase = elsecase
        
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.elsecase or self.cases[len(self.cases) - 1][0]).pos_end
        
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
    
class StringNode:
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
    
class AttributeNode:
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        
        self.pos_start = self.parent.pos_start
        self.pos_end= self.child.pos_end
    
class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        
        self.pos_start = pos_start
        self.pos_end = pos_end
        
class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
    
class ForNode:
	def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
		self.var_name_tok = var_name_tok
		self.start_value_node = start_value_node
		self.end_value_node = end_value_node
		self.step_value_node = step_value_node
		self.body_node = body_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.body_node.pos_end

class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

		self.pos_start = self.condition_node.pos_start
		self.pos_end = self.body_node.pos_end

class LoopNode:
	def __init__(self, amount, body_node):
		self.amount = amount
		self.body_node = body_node

		self.pos_start = self.amount.pos_start
		self.pos_end = self.body_node.pos_end

class ListNode:
    def __init__(self, things, pos_start, pos_end):
        self.things = things
        self.pos_start = pos_start
        self.pos_end = pos_end
        
class DictionaryNode:
    def __init__(self, things, pos_start, pos_end):
        self.things = things
        self.pos_start = pos_start
        self.pos_end = pos_end
        
class MultiLineNode:
    def __init__(self, things, pos_start, pos_end):
        self.things = things
        self.pos_start = pos_start
        self.pos_end = pos_end

class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_return_null = should_return_null

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end
        
class ClassDefNode:
    def __init__(self, var_name_tok, body_node):
        self.var_name_tok = var_name_tok
        self.body_node = body_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

class CallNode:
	def __init__(self, node_to_call, arg_nodes):
		self.node_to_call = node_to_call
		self.arg_nodes = arg_nodes

		self.pos_start = self.node_to_call.pos_start

		if len(self.arg_nodes) > 0:
			self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
		else:
			self.pos_end = self.node_to_call.pos_end

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0
        
    def register_advancement(self):
        self.advance_count += 1
        
    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)
    
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
        
    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        
    def update_current_tok(self): 
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        elif tok.type in (TT_LSQUARE, TT_IDENTIFIER, TT_STRING, TT_NUM, TT_IDENTIFIER, TT_LBRACE):
            listexpr = res.register(self.listcall())
            if res.error: return res
            return res.success(listexpr)
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            pos_startt = self.current_tok.pos_start.copy()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            return res.failure(Error(pos_startt, self.current_tok.pos_end, 202, "Parenthesis"))
        return res.failure(Error(tok.pos_start, tok.pos_end, 201, "Expression or Number"))
        
    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            if isinstance(res.node, IfNode):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 203, "If"))
            if isinstance(res.node, VarAssignNode):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 203, "Def/Manip"))
            if isinstance(res.node, ForNode):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 203, "For"))
            if isinstance(res.node, WhileNode):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 203, "While"))
            res = self.statements()
        return res
    
    def atom(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'if'):
            ifexpr = res.register(self.ifexpr())
            if res.error: return res
            return res.success(ifexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'def') or self.current_tok.matches(TT_KEYWORD, 'manip'):
            varexpr = res.register(self.varexpr())
            if res.error: return res
            return res.success(varexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'for'):
            forexpr = res.register(self.forexpr())
            if res.error: return res
            return res.success(forexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'while'):
            whileexpr = res.register(self.whileexpr())
            if res.error: return res
            return res.success(whileexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'loop'):
            loopexpr = res.register(self.loopexpr())
            if res.error: return res
            return res.success(loopexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'func'):
            funcexpr = res.register(self.funcexpr())
            if res.error: return res
            return res.success(funcexpr)
        elif self.current_tok.matches(TT_KEYWORD, 'class'):
            funcexpr = res.register(self.classexpr())
            if res.error: return res
            return res.success(funcexpr)
        else:
            expr = res.register(self.call_b())
            if res.error: 
                return res
            return res.success(expr)
        
    def classexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'class'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos1 = self.current_tok.pos_start.copy()
            
            if not self.current_tok.type == TT_IDENTIFIER:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Identifier'))
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
                
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            atom = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos1, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(ClassDefNode(var_name_tok, atom))
        
    def funcexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'func'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos1 = self.current_tok.pos_start.copy()
            
            if self.current_tok.type == TT_IDENTIFIER:
                var_name_tok = self.current_tok
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_LPAREN:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            else:
                var_name_tok = None
                if self.current_tok.type != TT_LPAREN:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"(" or Identifier'))
                    
            res.register_advancement()
            self.advance()
            parenpos2 = self.current_tok.pos_start.copy()
            arg_name_toks = []

            if self.current_tok.type == TT_IDENTIFIER:
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
                
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    if self.current_tok.type != TT_IDENTIFIER:
                        return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Identifier'))

                    arg_name_toks.append(self.current_tok)
                    res.register_advancement()
                    self.advance()
                
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos2, self.current_tok.pos_end, 202, 'Parenthesis'))
            else:
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos2, self.current_tok.pos_end, 202, 'Parenthesis'))
                
            res.register_advancement()
            self.advance()
                
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            atom = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos1, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(FuncDefNode(var_name_tok, arg_name_toks, atom, True))
        
    def listexpr(self):
        res = ParseResult()
        tok = self.current_tok
        if self.current_tok.type == TT_LSQUARE:
            pos_s = self.current_tok.pos_start.copy()
            res.register_advancement()
            self.advance()
            arg_nodes = []
            parenpos = self.current_tok.pos_start.copy()

            if self.current_tok.type == TT_RSQUARE:
                pass
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Expression, Number, or "]"'))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: 
                        return res

                if self.current_tok.type != TT_RSQUARE:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Square Brackets'))
            pos_e = self.current_tok.pos_end.copy()
            res.register_advancement()
            self.advance()
            return res.success(ListNode(arg_nodes, pos_s, pos_e))
        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == TT_NUM:
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if tok.value == "False":
                return res.success(BooleanNode(tok))
            if tok.value == "True":
                return res.success(BooleanNode(tok))
            if tok.value == "None":
                return res.success(NoneTypeNode(tok))
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LBRACE:
            pos_s = self.current_tok.pos_start.copy()
            res.register_advancement()
            self.advance()
            arg_nodes = {}
            bracepos = self.current_tok.pos_start.copy()

            if self.current_tok.type == TT_RBRACE:
                pass
            else:
                if not self.current_tok.type == TT_LPAREN:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
                res.register_advancement()
                self.advance()
                parenpos = self.current_tok.pos_start.copy()

                arg_name = res.register(self.expr())
                if res.error: 
                    return res
                
                if not self.current_tok.type == TT_COMMA:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '","'))
                
                res.register_advancement()
                self.advance()
                
                arg_nodes[arg_name] = res.register(self.expr())
                if res.error: 
                    return res
                
                if not self.current_tok.type == TT_RPAREN:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 201, 'Parenthesis'))
                res.register_advancement()
                self.advance()


                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    
                    if not self.current_tok.type == TT_LPAREN:
                        return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
                    res.register_advancement()
                    self.advance()
                    parenpos = self.current_tok.pos_start.copy()

                    arg_name = res.register(self.expr())
                    if res.error: 
                        return res
                    
                    if not self.current_tok.type == TT_COMMA:
                        return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '","'))
                    
                    res.register_advancement()
                    self.advance()
                    
                    arg_nodes[arg_name] = res.register(self.expr())
                    if res.error: 
                        return res
                    
                    if not self.current_tok.type == TT_RPAREN:
                        return res.failure(Error(parenpos, self.current_tok.pos_end, 201, 'Parenthesis'))
                    res.register_advancement()
                    self.advance()

                if self.current_tok.type != TT_RBRACE:
                    return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            pos_e = self.current_tok.pos_end.copy()
            res.register_advancement()
            self.advance()
            return res.success(DictionaryNode(arg_nodes, pos_s, pos_e))
        
    def listr(self):
        res = ParseResult()
        tok = self.current_tok
        res.register_advancement()
        self.advance()
        if tok.type == TT_IDENTIFIER:
            if self.current_tok.type != TT_LPAREN:
                return res.success(VarAccessNode(tok))
            if not self.current_tok.type == TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            res.register_advancement()
            self.advance()
            arg_nodes = []
            parenpos = self.current_tok.pos_start.copy()

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Expression, Number, or ")"'))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(VarAccessNode(tok), arg_nodes))
            
        return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Identifier'))
        
    def listcall(self):
        res = ParseResult()
        left = res.register(self.listexpr())
        if res.error:
            return res
        while self.current_tok.type == TT_PIPE:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.expr())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
    
    def varcall(self):
        res = ParseResult()
        left = res.register(self.listr())
        if res.error:
            return res
        while self.current_tok.type == TT_PIPE:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.expr())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        while self.current_tok.type == TT_POINT:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.listr())
            if res.error:
                return res
            left = AttributeNode(left, right)
        return res.success(left)
        
    def call(self):
        res = ParseResult()
        factor = res.register(self.factor())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []
            parenpos = self.current_tok.pos_start.copy()

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Expression, Number, or ")"'))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(factor, arg_nodes))
        return res.success(factor)
    
    def call_b(self):
        res = ParseResult()
        factor = self.current_tok
        if self.current_tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if not self.current_tok.type == TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            res.register_advancement()
            self.advance()
            arg_nodes = []
            parenpos = self.current_tok.pos_start.copy()

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Expression, Number, or ")"'))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(VarAccessNode(factor), arg_nodes))
        return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Statement'))
        
    def forexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'for'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start.copy()
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Identifier'))
            
            var_name = self.current_tok
            
            res.register_advancement()
            self.advance()
            
            if not self.current_tok.matches(TT_KEYWORD, 'in'):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'In'))
            
            res.register_advancement()
            self.advance()
            
            start = res.register(self.expr())
            if res.error:
                return res
            if not self.current_tok.matches(TT_KEYWORD, 'to'):
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'To'))
            
            res.register_advancement()
            self.advance()
            end = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.matches(TT_KEYWORD, 'step'):
                res.register_advancement()
                self.advance()

                step_value = res.register(self.expr())
                if res.error: return res
            else:
                step_value = None
            
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            expr = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(ForNode(var_name, start, end, step_value, expr))
        
    def whileexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'while'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start.copy()
            
            condition = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            expr = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(WhileNode(condition, expr))
        
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(MultiLineNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))
        
    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        
        if self.current_tok.matches(TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start

            expr = res.register(self.expr())
            if res.error:
                return res
                
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            res.register_advancement()
            self.advance()
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
            
        if self.current_tok.matches(TT_KEYWORD, 'continue'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
            
        if self.current_tok.matches(TT_KEYWORD, 'break'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
        atom = res.register(self.atom())
        if res.error:
            return res
        return res.success(atom)
        
    def loopexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'loop'):
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start.copy()
            
            amount = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            expr = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(LoopNode(amount, expr))

    def doinky(self):
        res = ParseResult()
        left = res.register(self.call())
        if res.error:
            return res
        while self.current_tok.type == TT_POINT:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.call())
            if res.error:
                return res
            left = AttributeNode(left, right)
        return res.success(left)
    
    def power(self):
        return self.bin_op(self.doinky, [TT_POWER])
    
    def term(self):
        return self.bin_op(self.power, [TT_MUL, TT_DIV])
    
    def ifexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'if'):
            cases = []
            elsecase = None
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start.copy()
            condition = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.type != TT_LBRACE:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
            
            res.register_advancement()
            self.advance()
            
            bracepos = self.current_tok.pos_start.copy()
            expr = res.register(self.statements())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RBRACE:
                return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            cases.append((condition, expr))
            
            while self.current_tok.matches(TT_KEYWORD, 'elif'):
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_COLON:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
                
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_LPAREN:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
                
                res.register_advancement()
                self.advance()
                parenpos = self.current_tok.pos_start.copy()
                condition = res.register(self.expr())
                if res.error:
                    return res
                
                if self.current_tok.type != TT_LBRACE:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
                
                res.register_advancement()
                self.advance()
                
                bracepos = self.current_tok.pos_start.copy()
                expr = res.register(self.statements())
                if res.error:
                    
                    return res
                
                if self.current_tok.type != TT_RBRACE:
                    return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
                
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
                
                res.register_advancement()
                self.advance()
                
                cases.append((condition, expr))
                
            if self.current_tok.matches(TT_KEYWORD, 'else'):
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_COLON:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
                
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_LBRACE:
                    return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"{"'))
                
                res.register_advancement()
                self.advance()
                
                bracepos = self.current_tok.pos_start.copy()
                expr = res.register(self.statements())
                if res.error:
                    return res
                
                if self.current_tok.type != TT_RBRACE:
                    return res.failure(Error(bracepos, self.current_tok.pos_end, 202, 'Braces'))
                
                res.register_advancement()
                self.advance()
                
                elsecase = expr
            return res.success(IfNode(cases, elsecase))
    
    def varexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'def'):
            var_type = self.current_tok.value
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_COLON:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '":"'))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != TT_LPAREN:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"("'))
            
            res.register_advancement()
            self.advance()
            parenpos = self.current_tok.pos_start.copy()
            
            var_name = res.register(self.varcall())
            if res.error:
                return res
            # res.register_advancement()
            # self.advance()
            
            if self.current_tok.type != TT_EQ:
                return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, '"="'))
            
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            
            if self.current_tok.type != TT_RPAREN:
                return res.failure(Error(parenpos, self.current_tok.pos_end, 202, 'Parenthesis'))
            
            res.register_advancement()
            self.advance()
            
            return res.success(VarAssignNode(var_name, expr, var_type))
    
    def expr(self):
        res = ParseResult()
        left = res.register(self.compexpr())
        if res.error:
            return res
        while self.current_tok.matches(TT_KEYWORD, 'and') or self.current_tok.matches(TT_KEYWORD, 'or'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(self.compexpr())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
        
    def compexpr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            compexpr = res.register(self.compexpr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, compexpr))
        node = res.register(self.bin_op(self.arithexpr, [TT_EE, TT_LT, TT_GT, TT_LTE, TT_GTE, TT_NE]))
        
        if res.error:
            return res.failure(Error(self.current_tok.pos_start, self.current_tok.pos_end, 201, 'Expression or Number'))
        
        return res.success(node)

    def arithexpr(self):
        return self.bin_op(self.term, [TT_PLUS, TT_MINUS])
    
    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
        self.error or
        self.func_return_value or
        self.loop_should_continue or
        self.loop_should_break
        )
        
class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
        self.type = "Number"
        self.built_in = ["type", "length"]
        self.attributes = {}
        
    def attribute(self,child):
        if self.value % self.value == 0:
            length = len(str(int(self.value)))
        else:
            length = len(str(self.value))
        self.attributes = {"type": String("Number"), "length": Number(length)}
        if not isinstance(child, CallNode):
            hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        else:
            hello = self.attributes.get(child.node_to_call.var_name_tok.value)
        if not hello:
            if not isinstance(child, CallNode):
                return None, Error(child.pos_start, child.pos_end,
                        311, child.var_name_tok.value, self.context
                    )
            return None, Error(child.pos_start, child.pos_end,
                        311, child.node_to_call.var_name_tok.value, self.context
                    )
        return hello.set_pos(self.pos_start, self.pos_end).set_context(self.context),None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        if other.type == "Number":
            return Number(self.value + other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def subbed_by(self, other):
        if other.type == "Number":
            return Number(self.value - other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def multed_by(self, other):
        if other.type == "Number":
            return Number(self.value * other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )

    def dived_by(self, other):
        if other.type == "Number":
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
        if other.type == "Number":
            return Number(self.value ** other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )
        
    def equals(self, other):
        if self.value == other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        if self.value != other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        if self.value < other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def greater_than(self, other):
        if self.value > other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def less_than_equals(self, other):
        if self.value <= other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def greater_than_equals(self, other):
        if self.value >= other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None

    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", "Number"], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"None and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"None and {other.type}"], self.context)
    
    def piped(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Number", other.type], self.context
                )
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy    
        
    def __repr__(self):
        return str(self.value)
    
class Boolean:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()
        self.type = "Boolean"
        self.built_in = ["type"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"type": String("Boolean")}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
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
        
    def equals(self, other):
        if self.value == other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        if self.value != other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
    
    def notted(self):
        if self.value == 0:
            self.value = 1
        else:
            self.value = 0
        return Boolean(self.value).set_context(self.context), None
    
    def ored(self, other):
        if self.value == 1 or other.value == 1:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def anded (self, other):
        if self.value == 1 and other.value == 1:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def piped(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Boolean", other.type], self.context
                )
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(bool(self.value))
    
class BaseFunction:
    def __init__(self, name):
        self.set_pos()
        self.set_context()
        self.name = name or '<anonymous>'
        self.built_in = ["type", "name"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"name": String(self.name), "type": String("Function")}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
        
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) > len(arg_names):
            return res.failure(Error(
                self.pos_start, self.pos_end, 307,
                f"{len(args) - len(arg_names)} into '{self.name}'",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(Error(
                self.pos_start, self.pos_end, 308,
                f"{len(arg_names) - len(args)} into '{self.name}'",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self,arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set_(arg_name, arg_value)
            
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)
    
    def added_to(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def subbed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def multed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def not_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def piped(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", self.type], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"Function and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"Function and {other.type}"], self.context)
    
    def set_context(self, context=None):
        self.context = context
        return self

class Class:
    def __init__(self, name, body_node):
        self.set_pos()
        self.set_context()
        self.name = name or '<anonymous>'
        self.body_node = body_node
        self.arg_names = []
        self.built_in = ["type", "name"]
        self.attributes = {}
        self.extras = {}
        self.type = "Class Object"
        
    def attribute(self,child):
        self.attributes = {"name": String(self.name), "type": String("Class Object")}
        if isinstance(child, VarAccessNode):
            hello = self.attributes.get(child.var_name_tok.value)
        else:
            hello = self.attributes.get(child.node_to_call.var_name_tok.value)
        if not hello:
            if isinstance(child, VarAccessNode):
                return None, Error(child.pos_start, child.pos_end,
                        311, child.var_name_tok.value, self.context
                    )
            return None, Error(child.pos_start, child.pos_end,
                        311, child.node_to_call.var_name_tok.value, self.context
                    )
        hello.set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = Class(self.name, self.body_node)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.attributes = self.attributes
        while True:
            copy.instance_number = random.randint(0, 100000)
            if copy.instance_number not in instancenums:
                break
        instancenums.append(copy.instance_number)
        return copy

    def instance(self):
        copy = ClassInstance(self.name, self.body_node)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.extras = self.extras
        copy.attributes = self.attributes
        while True:
            copy.instance_number = random.randint(0, 100000)
            if copy.instance_number not in instancenums:
                break
        instancenums.append(copy.instance_number)
        return copy
        
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args) > len(arg_names):
            return res.failure(Error(
                self.pos_start, self.pos_end, 307,
                f"{len(args) - len(arg_names)} into '{self.name}'",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(Error(
                self.pos_start, self.pos_end, 308,
                f"{len(arg_names) - len(args)} into '{self.name}'",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self,arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set_(arg_name, arg_value)
            
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)
    
    def added_to(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def subbed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def multed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def not_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def piped(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, [self.type, other.type], self.context
                )
        
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", self.type], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"Class and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"Class and {other.type}"], self.context)
    
    def set_context(self, context=None):
        self.context = context
        return self
    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        body_node = MultiLineNode([], self.pos_start, self.pos_end)

        for i in self.body_node.value:
            if isinstance(i, Function):
                if i.name == "_init":
                    self.arg_names = i.arg_names
                    body_node = i.body_node
        if "self" in self.arg_names:
            args.append(self.instance())
        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res
        return res.success(self.instance())
    def __repr__(self):
        return f"<class-object {self.name}>"

class ClassInstance(Class):
    def __init__(self, name, body_node):
        self.set_pos()
        self.set_context()
        self.name = name or '<anonymous>'
        self.body_node = body_node
        self.arg_names = []
        self.built_in = ["type", "name"]
        self.attributes = {}
        self.type = "Class Instance"

    def copy(self):
        copy = ClassInstance(self.name, self.body_node)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        copy.extras = self.extras
        copy.attributes = self.attributes
        copy.instance_number = self.instance_number
        return copy

    def attribute(self,child):
        self.attributes = {"name": String(self.name), "type": String("Class Instance")}
        for i in self.body_node.value:
            if isinstance(i, Function):
                self.extras[i.name] = i
        self.attributes.update(self.extras)
        if isinstance(child, CallNode):
            hello = self.attributes.get(child.node_to_call.var_name_tok.value)
            if not hello or hello == None:
                return None, Error(child.pos_start, child.pos_end,
                        311, child.node_to_call.var_name_tok.value, self.context
                    )
        else:
            hello = self.attributes.get(child.var_name_tok.value)
            if not hello or hello == None:
                return None, Error(child.pos_start, child.pos_end,
                        311, child.var_name_tok.value, self.context
                    )
        hello = hello.set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return hello,None
    
    def __repr__(self):
        return f"<class-instance {self.name} at 0x{self.instance_number}>"

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_return_null):
        super().__init__(name)
        self.type = "Function"
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None: return res

        ret_value = (value if not self.should_return_null else None) or res.func_return_value or NoneType()
        return res.success(ret_value)
    def __repr__(self):
        return f"<function {self.name}>"
    
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type = "Function"
        
    def no_visit_method(self, node, context):
        raise Exception(f'[INTERNAL] Error code 402 - No execute method defnied: {type(node).__name__}')
        
    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()
        
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)
        
        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return():
            return res
        
        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)
        
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f"<built-in function {self.name}>"
    
    def execute_print(self, exec_ctx):
        if isinstance(exec_ctx.symbol_table.get('value'), String):
            print(str(exec_ctx.symbol_table.get('value').value))
        else:
            print(str(exec_ctx.symbol_table.get('value')))
        x = RTResult().success(NoneType().set_pos(self.pos_start, self.pos_end).set_context(self.context))
        return x
    execute_print.arg_names = ['value']
    
    def execute_factorial(self, exec_ctx):
        if isinstance(exec_ctx.symbol_table.get('value'), Number) and isinstance(exec_ctx.symbol_table.get('value').value, int) and exec_ctx.symbol_table.get('value').value > 0:
            x = RTResult().success(Number(math.factorial(exec_ctx.symbol_table.get('value').value)).set_pos(self.pos_start, self.pos_end).set_context(self.context))
        else:
            x = RTResult().failure(Error(self.pos_start, self.pos_end, 310, f'{exec_ctx.symbol_table.get("value").type}:{exec_ctx.symbol_table.get("value").value}'))
        return x
    execute_factorial.arg_names = ['value']
    
            
class List:
    def __init__(self, value):
        self.set_pos()
        self.set_context()
        self.type = "List"
        self.value = value
        self.built_in = ["type", "length"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"length": Number(len(self.value)), "type": String("List")}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = List(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def added_to(self, other):
        if other.type == "List":
            return List(self.value + other.value).set_context(self.context), None
        new_list = self.copy()
        new_list.value.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.value.pop(other.value)
                return new_list, None
            except:
                return None, Error(
                    other.pos_start, other.pos_end,
                    309, other.value,
                    self.context
                )
        return None, Error(other.pos_start, other.pos_end,
                    304, ["List", other.type], self.context
                )

    def multed_by(self, other):
        if other.type == "Number":
            if isinstance(other.value, float):
                return None, Error(
                    other.pos_start, other.pos_end,
                    309, other.value,
                    self.context
                )
            new_list = self.copy() 
            new_list.value *= other.value
            return new_list, None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["List", other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["List", other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["List", other.type], self.context
                )
        
    def equals(self, other):
        number = 1
        if self.type == other.type:
            if len(self.value) == len(other.value):
                for i in self.value:
                    if i.value != other.value[self.value.index(i)].value:
                        number = 0
            else:
                number = 0
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        number = 0
        if self.type == other.type:
            if len(self.value) == len(other.value):
                for i in self.value:
                    if i.value != other.value[self.value.index(i)].value:
                        number = 1
            else:
                number = 1
        else:
            number = 1
            
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["List", other.type], self.context
                    )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["List", other.type], self.context
                    )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["List", other.type], self.context
                    )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["List", other.type], self.context
                    )
    
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", "List"], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"List and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"List and {other.type}"], self.context)
    
    def piped(self, other):
        if other.type == "Number":
            try:
                return self.value[other.value], None
            except:
                return None, Error(
                    other.pos_start, other.pos_end,
                    309, other.value,
                    self.context
                )
        return None, Error(other.pos_start, other.pos_end,
                    304, ["List", other.type], self.context
                )
    
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(self.value)

class Dictionary:
    def __init__(self, value):
        self.set_pos()
        self.set_context()
        self.type = "Dictionary"
        self.value = value
        self.built_in = ["type", "keys", "values"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"keys": List(list(self.value.keys())),"values": List(list(self.value.values())), "type": String("Dictionary")}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = Dictionary(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def added_to(self, other):
        if other.type == "Dictionary":
            copy = self.copy()
            copy.value.update(other.value)
            return copy, None
        if other.type == "List":
            copy = self.copy()
            if len(other.value)!= 2:
                return None, Error(other.pos_start, other.pos_end,
                    303, 2, self.context)
            copy.value[other.value[0]] = other.value[1]
            return copy, None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Dictionary", other.type], self.context
                )

    def subbed_by(self, other):
        new_list = self.copy()
        for i in list(new_list.value):
            if isinstance(i, type(other)) and i.value == other.value:
                del new_list.value[i]
                return new_list, None
        return None, Error(other.pos_start, other.pos_end, 309, other, self.context)

    def multed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Dictionary", other.type], self.context
                )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Dictionary", other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["Dictionary", other.type], self.context
                )
        
    def equals(self, other):
        number = 1
        if self.type == other.type:
            if len(self.value) == len(other.value):
                for i in self.value:
                    if isinstance(i, type(list(other.value)[list(self.value).index(i)])):
                        if not i.value == list(other.value)[list(self.value).index(i)].value:
                            number = 0
                    else:
                        number = 0
                for i in self.value.values():
                    if isinstance(i, type(list(other.value.values())[list(self.value.values()).index(i)])):
                        if not i.value == list(other.value.values())[list(self.value.values()).index(i)].value:
                            number = 0
                    else:
                        number = 0
            else:
                number = 0
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        number = 0
        if self.type == other.type:
            if len(self.value) == len(other.value):
                for i in self.value:
                    if isinstance(i, type(list(other.value)[list(self.value).index(i)])):
                        if not i.value == list(other.value)[list(self.value).index(i)].value:
                            number = 1
                    else:
                        number = 1
                for i in self.value.values():
                    if isinstance(i, type(list(other.value.values())[list(self.value.values()).index(i)])):
                        if not i.value == list(other.value.values())[list(self.value.values()).index(i)].value:
                            number = 1
                    else:
                        number = 1
            else:
                number = 1
        else:
            number = 1
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["Dictionary", other.type], self.context
                    )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["Dictionary", other.type], self.context
                    )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["Dictionary", other.type], self.context
                    )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["Dictionary", other.type], self.context
                    )
    
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", "Dictionary"], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"Dictionary and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"Dictionary and {other.type}"], self.context)
    
    def piped(self, other):
        for i in list(self.value):
            if isinstance(i, type(other)) and i.value == other.value:
                return self.value.get(i), None
    
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        strings= "{"
        leng = 0
        for i in self.value:
            leng += 1
            strings += f"({i}, {self.value[i]})"
            if not leng == len(self.value):
                strings += ", "
        strings += "}"
        return strings
    
class String:
    def __init__(self, value):
        self.set_pos()
        self.set_context()
        self.type = "String"
        self.value = str(value)
        self.built_in = ["type", "length"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"type": String("String"), "length": Number(len(self.value))}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def piped(self, other):
        if other.type == "Number":
            try:
                newval = self.value[other.value]
                copy = self.copy()
                copy.value = newval
                return copy, None
            except:
                return None, Error(
                    other.pos_start, other.pos_end,
                    309, other.value,
                    self.context
                )
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
                )
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def added_to(self, other):
        if other.type == "String":
            return String(self.value + other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
                )

    def subbed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
                )

    def multed_by(self, other):
        if other.type == "Number":
            return String(self.value * other.value).set_context(self.context), None
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
        )

    def dived_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
                )
        
    def powed_by(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["String", other.type], self.context
                )
        
    def equals(self, other):
        if self.value == other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        if self.value != other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["String", other.type], self.context
                    )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["String", other.type], self.context
                    )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["String", other.type], self.context
                    )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["String", other.type], self.context
                    )
    
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", "String"], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"String and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"String and {other.type}"], self.context)
    
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return f'"{str(self.value)}"'

class NoneType:
    def __init__(self):
        self.set_pos()
        self.set_context()
        self.type = "None"
        self.value = 0
        self.built_in = ["type"]
        self.attributes = {}
        
    def attribute(self,child):
        self.attributes = {"type": String("None")}
        hello = self.attributes.get(child.var_name_tok.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        if not hello:
            return None, Error(child.pos_start, child.pos_end,
                    311, child.var_name_tok.value, self.context
                )
        return hello,None
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def copy(self):
        copy = NoneType()
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
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
        
    def equals(self, other):
        if self.value == other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def not_equals(self, other):
        if self.value != other.value:
            number = 1
        else:
            number = 0
        return Boolean(number).set_context(self.context), None
    
    def less_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["None", other.type], self.context
                    )
    
    def greater_than(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["None", other.type], self.context
                    )
    
    def less_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["None", other.type], self.context
                    )
    
    def greater_than_equals(self, other):
        return None, Error(other.pos_start, other.pos_end,
                        304, ["None", other.type], self.context
                    )
    
    def notted(self):
        return None, Error(self.pos_start, self.pos_end, 304, ["not", "None"], self.context)
    
    def anded(self, other):
        return None, Error(self.pos_start, self.pos_end, 304, ["and", f"None and {other.type}"], self.context)
    
    def ored(self,other):
        return None, Error(self.pos_start, self.pos_end, 304, ["or", f"None and {other.type}"], self.context)
    
    def piped(self, other):
        return None, Error(other.pos_start, other.pos_end,
                    304, ["None", other.type], self.context
                )
    
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return "None"
    
Boolean.true = Boolean(1)
Boolean.false = Boolean(0)
NoneType.none = NoneType()
PRESETSV = ["True", "False", "None"]
BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.factorial = BuiltInFunction("factorial")
PRESETSD = ["print", "factorial", 'range'] + PRESETSV
    
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
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)
    
    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if isinstance(value_to_call, ClassInstance):
            return res.failure(Error(value_to_call.pos_start, value_to_call.pos_end, 313, "Class Instance", context))
        if res.should_return(): return res
        value_to_call.value = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        
        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return(): return res
            
        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        if isinstance(node.var_name_tok, VarAccessNode):
            var_name = node.var_name_tok.var_name_tok.value
            
            value = res.register(self.visit(node.value_node, context))
            var_type = node.var_type
            
            if res.should_return():
                return res
            
            if var_type == 'def':
                context.symbol_table.set_(var_name, value)
        elif isinstance(node.var_name_tok, BinOpNode):
            var_name = res.register(self.visit(node.var_name_tok,context))
            if res.should_return():
                return res
            lists = res.register(self.visit(node.var_name_tok.left_node,context))
            rists = res.register(self.visit(node.var_name_tok.right_node,context))
            value = res.register(self.visit(node.value_node, context))
            if res.should_return():
                return res
            copy = lists.copy()
            if isinstance(lists.copy(), List):
                try:
                    copy.value[rists.value] = value
                except:
                    return res.failure(Error(rists.pos_start, rists.pos_end, 309, rists.value, context))
            if isinstance(lists.copy(), Dictionary):
                try:
                    for i in list(lists.value):
                        if isinstance(i, type(rists)) and i.value == rists.value:
                            copy.value[i] = value
                except Exception as e:
                    return res.failure(Error(rists.pos_start, rists.pos_end, 309, rists.value, context))
        else:
            var_name = res.register(self.visit(node.var_name_tok.parent,context))
            if res.should_return():
                return res
            value_node = res.register(self.visit(node.value_node,context))
            child = node.var_name_tok.child.var_name_tok.value
            if res.should_return():
                return res
            copy = var_name.copy()
            if isinstance(copy, ClassInstance):
                copy.extras[child] = value_node
                value = None
            else:
                if isinstance(node.var_name_tok.parent, VarAccessNode):
                    call = res.register(self.visit(node.var_name_tok.parent,context))
                    return res.failure(Error(node.var_name_tok.pos_start, node.var_name_tok.pos_end, 312, f'{call.type}.{node.var_name_tok.child.var_name_tok.value}', context))
                else:
                    call = res.register(self.visit(node.var_name_tok.parent,context))
                    return res.failure(Error(node.var_name_tok.pos_start, node.var_name_tok.pos_end, 312, f'{call.type}.{node.var_name_tok.child.var_name_tok.value}', context))
        return res.success(value)
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    def visit_StringNode(self, node, context):
        return RTResult().success(String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.things:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_DictionaryNode(self, node, context):
        res = RTResult()
        elements = {}

        for element_node in node.things:
            elements[(res.register(self.visit(element_node, context)))] = (res.register(self.visit(node.things[element_node], context)))
            if res.should_return(): return res

        return res.success(
            Dictionary(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_MultiLineNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.things:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BooleanNode(self, node, context):
        if node.tok.value == "False":
            node.tok.value = 0
        else:
            node.tok.value = 1
        return RTResult().success(Boolean(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_NoneTypeNode(self, node, context):
        return RTResult().success(NoneType().set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_LoopNode(self, node, context):
        res = RTResult()
        elements = []
        loop_value = res.register(self.visit(node.amount, context))
        if not isinstance(loop_value, Number) or loop_value.value < 1 or isinstance(loop_value.value, float):
            return res.failure(Error(node.amount.pos_start, node.amount.pos_end, 306, node.amount, context))
        for i in range(0, loop_value.value):
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = NoneType()
        
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()
    
    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if not isinstance(start_value, Number) or isinstance(start_value.value, float):
            return res.failure(Error(node.start_value_node.pos_start, node.start_value_node.pos_end, 306, node.start_value_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if not isinstance(end_value, Number) or isinstance(end_value.value, float):
            return res.failure(Error(node.end_value_node.pos_start, node.end_value_node.pos_end, 306, node.end_value_node, context))
        if res.should_return(): return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if not isinstance(step_value, Number) or isinstance(step_value.value, float):
                return res.failure(Error(node.step_value_node.pos_start, node.step_value_node.pos_end, 306, node.start_value_node, context))
            if res.should_return(): return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
            
        while condition():
            context.symbol_table.set_(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
            
            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break
            
            elements.append(value)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res

            if condition.value == 0: break

            res.register(self.visit(node.body_node, context))
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_FuncDefNode(self, node, context):
        res = RTResult()
        
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_return_null).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if func_name in PRESETSD:
            return res.failure(Error(node.pos_start, node.pos_end, 305, func_name, context))
        
        if node.var_name_tok:
            context.symbol_table.set_(func_name, func_value)
            
        return res.success(func_value)
    
    def visit_ClassDefNode(self, node, context):
        res = RTResult()
        burn = Context(node.var_name_tok.value)
        burn.symbol_table = SymbolTable(context.symbol_table)
        func_name = node.var_name_tok.value
        body_node = res.register(self.visit(node.body_node, burn))
        func_value = Class(func_name, body_node).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if func_name in PRESETSD:
            return res.failure(Error(node.pos_start, node.pos_end, 305, func_name, context))
        context.symbol_table.set_(func_name, func_value)
            
        return res.success(func_value)
    
    def visit_AttributeNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.parent, context))
        if res.should_return(): return res
        
        result, error = left.attribute(node.child)
        if result:
            result.set_pos(node.child.pos_start, node.child.pos_end).set_context(context)
        
        if error:
            return res.failure(error)
        else:
            if isinstance(node.child, CallNode):
                args = []
                for arg_node in node.child.arg_nodes:
                    args.append(res.register(self.visit(arg_node, context)))
                    if res.should_return(): return res

                for i in result.arg_names:
                    if i == "self":
                        args.insert(0, left.copy())

                result = res.register(result.execute(args))
                if res.should_return(): return res
                result = result.copy().set_pos(node.child.pos_start, node.child.pos_end).set_context(context)
            return res.success(result.set_context(context).set_pos(node.child.pos_start, node.child.pos_end))
        
    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        
        if res.should_return(): return res
        
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
        elif node.op_tok.type == TT_EE:
            result,error = left.equals(right)
        elif node.op_tok.type == TT_NE:
            result,error = left.not_equals(right)
        elif node.op_tok.type == TT_GT:
            result,error = left.greater_than(right)
        elif node.op_tok.type == TT_LT:
            result,error= left.less_than(right)
        elif node.op_tok.type == TT_GTE:
            result,error= left.greater_than_equals(right)
        elif node.op_tok.type == TT_LTE:
            result,error= left.less_than_equals(right)
        elif node.op_tok.type == TT_PIPE:
            result,error= left.piped(right)
        elif node.op_tok.matches(TT_KEYWORD, 'or'):
            result, error= left.ored(right)
        elif node.op_tok.matches(TT_KEYWORD, 'and'):
            result, error= left.anded(right)
        
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))
        
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        
        error = None
        
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        if node.op_tok.matches(TT_KEYWORD, 'not'):
            number, error = number.notted()
            
        if error:
            return res.failure(error)
        else:    
            return res.success(number.set_context(context).set_pos(node.pos_start, node.pos_end))
        
    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value.value != 0:
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(expr_value)

        if node.elsecase:
            else_value = res.register(self.visit(node.elsecase, context))
            if res.should_return(): return res
            return res.success(else_value)

        return res.success(None)
        
global_symbol_table = SymbolTable()
global_symbol_table.set_("True", Boolean.true)
global_symbol_table.set_("False", Boolean.false)
global_symbol_table.set_("None", NoneType())
global_symbol_table.set_("print", BuiltInFunction.print)
global_symbol_table.set_("factorial", BuiltInFunction.factorial)
        
def run(text, fn):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    
    return result.value, result.error