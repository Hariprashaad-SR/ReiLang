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