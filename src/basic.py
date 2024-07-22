#### CONSTANTS ####

DIGITS = '0123456789'
IGNORE_CHARS = ['\t', '\n', ' ']


#### ERROR ####

class Error:
    def __init__(self,pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def tostring(self):
        res =  f'{self.error_name} : {self.details}\nFile {self.pos_start.file}, line {self.pos_start.ln_no + 1}\n{self.pos_start.txt}'
        res += f'\n{(self.pos_start.idx * " ")}{"^" * (self.pos_end.idx - self.pos_start.idx)}\n'
        return res

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'IllegalCharError', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'InvalidSyntaxError', details)

#### POSITION

class Position:
    def __init__(self, idx, ln_no, col, fl, txt):
        self.idx = idx
        self.ln_no = ln_no
        self.col = col
        self.file = fl
        self.txt = txt
    
    def advance(self, current_char = None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln_no += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln_no, self.col, self.file, self.txt)

##### TOKENS #####

RL_INT = 'INT'
RL_FLOAT = 'FLOAT'
RL_PLUS = 'PLUS'
RL_MINUS = 'MINUS'
RL_MUL = 'MUL'
RL_DIV = 'DIV'
RL_LPAREN = 'LPAREN'
RL_RPAREN = 'RPAREN'
RL_EOF = 'EOF'

class Token:
    def __init__(self, type_, value = None, pos_start = None, pos_end = None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type} : {self.value}'
        return f'{self.type}'

#### NODES ####

class NumberNode:
    def __init__(self, token):
        self.tok = token
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'
    

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
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end
    
    def __repr__(self):
        return f'({self.op_tok}{self.node})'


#### PARSER #####
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
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
            self.cur_tok = self.tokens[self.tok_idx]
        
        return self.cur_tok
    
    def parse(self):
        res = self.expr()
        if not res.error and self.cur_tok.type != RL_EOF:
            return res.failure(InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected '+' , '-', '*', '/' "))
        return res
    
    def factor(self):
        tok = self.cur_tok
        res = ParseResult()

        if tok.type in (RL_PLUS, RL_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type == RL_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.cur_tok.type == RL_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(self.cur_tok.pos_start, self.cur_tok.pos_end, "Expected ')'"))
        elif tok.type in (RL_INT, RL_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, 'Expected INT or FLOAT'))

    def term(self):
        return self.bin_op(self.factor, (RL_MUL, RL_DIV))

    def expr(self):
        return self.bin_op(self.term, (RL_PLUS, RL_MINUS))
        
    
    def bin_op(self, fn, type):
        res = ParseResult()
        left = res.register(fn())

        if res.error:
            return res

        while self.cur_tok.type in type:
            op_tok = self.cur_tok
            res.register(self.advance())
            right = res.register(fn())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)





#### REILANG ###

class ReiLang:
    def __init__(self, text, fl):
        self.text = text
        self.file = fl
        self.pos = Position(-1, 0, -1, self.file, self.text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        pos_start = None

        while self.current_char != None:
            if self.current_char in IGNORE_CHARS:
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(RL_PLUS, pos_start = pos_start))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(RL_MINUS, pos_start = pos_start))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(RL_MUL, pos_start = pos_start))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(RL_DIV, pos_start = pos_start))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(RL_LPAREN, pos_start = pos_start))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RL_RPAREN, pos_start = pos_start))
                self.advance()
            else:
                char = self.current_char
                pos_start = self.pos.copy()
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        
        tokens.append(Token(RL_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        numb_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                numb_str += self.current_char
                dot_count += 1
            else:
                numb_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(RL_INT, int(numb_str), pos_start=pos_start, pos_end=self.pos)
        elif dot_count == 1:
            return Token(RL_FLOAT, float(numb_str))

#### NUMBER NODE  ####
class Number:
    def __init__(self, value):
        self.value = value
    
    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end

        return self
    
    def add_by(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
    
    def sub_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        
    def mul_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        
    def div_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value)
        
    # def added_to(self, other):
    #     if isinstance(other, Number):
    #         return Number(self.value + other.value)
        
    # def added_to(self, other):
    #     if isinstance(other, Number):
    #         return Number(self.value + other.value)

    def __repr__(self):
        return str(self.value)

#### INTERPRETER ####
class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self, node):
        return Number(node.tok.value).set_pos(node.pos_start, node.pos_end)
    
    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)
        result = Number(0)

        if node.op_tok.type == RL_PLUS:
            result = left.add_by(right)
        
        elif node.op_tok.type == RL_MINUS:
            result = left.sub_by(right)
        
        elif node.op_tok.type == RL_MUL:
            result = left.mul_by(right)

        elif node.op_tok.type == RL_DIV:
            result = left.div_by(right)

        return result.set_pos(node.pos_start, node.pos_end)
    
    def visit_UnaryOpNode(self, node):
        number = self.visit(node.node)

        if node.op_tok.type == RL_MINUS:
            number = number.mul_by(Number(-1))

        return number.set_pos(node.pos_start, node.pos_end)

#### RUN ####

def run(text, fl):
    reilang = ReiLang(text, fl)
    tokens, error = reilang.make_tokens()

    if error:
        return None, error

    expr = Parser(tokens).parse()

    if expr.error:
        return None, expr.error
    
    interpreter = Interpreter()
    val = interpreter.visit(expr.node)

    return val, None