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
        return f'{self.error_name} : {self.details}\nFile {self.pos_start.file}, line {self.pos_start.ln_no + 1}\n{self.pos_start.txt}\n{(self.pos_start.idx * " ")}^\n'
    

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'IllegalCharError', details)

#### POSITION

class Position:
    def __init__(self, idx, ln_no, col, fl, txt):
        self.idx = idx
        self.ln_no = ln_no
        self.col = col
        self.file = fl
        self.txt = txt
    
    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln_no += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln_no, self.col, self.file, self.txt)

##### TOKENS #####

RL_INT = 'RL_INT'
RL_FLOAT = 'RL_FLOAT'
RL_PLUS = 'RL_PLUS'
RL_MINUS = 'RL_MINUS'
RL_MUL = 'RL_MUL'
RL_DIV = 'RL_DIV'
RL_LPAREN = 'RL_LPAREN'
RL_RPAREN = 'RL_RPAREN'

class Token:
    def __init__(self, type_, value = None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type} : {self.value}'
        return f'{self.type}'


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
        isError = 0

        while self.current_char != None:
            if self.current_char in IGNORE_CHARS:
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(RL_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(RL_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(RL_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(RL_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(RL_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RL_RPAREN))
                self.advance()
            else:
                isError = 1
                char = self.current_char
                if pos_start == None:
                    pos_start = self.pos.copy()
                self.advance()
        
        if isError == 1:
            return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        return tokens, None

    def make_number(self):
        numb_str = ''
        dot_count = 0

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
            return Token(RL_INT, int(numb_str))
        elif dot_count == 1:
            return Token(RL_FLOAT, float(numb_str))
        

#### RUN ####

def run(text, fl):
    reilang = ReiLang(text, fl)
    tokens, error = reilang.make_tokens()


    return tokens, error