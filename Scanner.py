import re


class SymbolData:
    def __init__(self, name, type=None, value=None, size=None):
        self.name = name
        self.type = type
        self.value = value
        self.array = False
        self.size = size


symbol_table_stack = []


def init_scope():
    symbol_table = dict()
    symbol_table['boolean'] = SymbolData('boolean', type='boolean', size=1)
    symbol_table['integer'] = SymbolData('integer', type='integer', size=4)
    symbol_table['character'] = SymbolData('character', type='character', size=1)
    symbol_table['real'] = SymbolData('real', type='real', size=4)
    symbol_table_stack.append(symbol_table)


arithmetic_operations = ['+', '*', '&', '^', '|', '%']
logical_operations = ['<=', '>', '>=', '==', '<>', '~']
shitty_characters = ['(', ')', ',', ';', ':', ':=', '[', ']']
data_types = ['array', 'boolean', 'integer', 'character', 'real', 'string']
key_words = ['function', 'procedure', 'begin', 'end', 'return', 'if', 'then', 'else', 'while', 'do', 'and', 'or',
             'of', 'break', 'assign', 'continue', 'var']
white_spaces = ['\n', '\t', ' ', '\f', '\r', '\t', '\v']
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class Scanner:
    def __init__(self):
        init_scope()
        f = open("demofile.txt", "r")
        self.inp = f.read()
        self.prev_token = None
        self.const = None
        self.id = None
        self.ignore = False
        self.scope = None

    def next_token(self):
        inp = self.inp
        prev = self.prev_token
        token = self.scan()
        self.inp = inp
        self.prev_token = prev
        return token

    def scan(self):
        while True:
            # print(len(self.inp))
            if len(self.inp) == 0:
                return '$'
            if self.inp[:2] in logical_operations or self.inp[:2] in shitty_characters:
                token = self.inp[0:2]
                self.inp = self.inp[2:]
                self.prev_token = token
                return token
            elif self.inp[0] in arithmetic_operations or self.inp[0] in logical_operations or self.inp[
                0] in shitty_characters:
                token = self.inp[0]
                self.inp = self.inp[1:]
                self.prev_token = token
                self.ignore = False
                return token

            elif self.inp[0] == '/':
                if self.inp[1] == '/':
                    while len(self.inp) != 0 and self.inp[0] != '\n':
                        self.inp = self.inp[1:]
                else:
                    self.inp = self.inp[1:]
                    self.prev_token = '/'
                    return '/'

            elif self.inp[0] == '-':
                if self.inp[1] == '-':
                    while len(self.inp) != 0 and self.inp[0] != '\n':
                        self.inp = self.inp[1:]
                else:
                    self.inp = self.inp[1:]
                    self.prev_token = '-'
                    return '-'

            elif self.inp[0] == '<':
                if self.inp[1] == '-' and self.inp[2] == '-':
                    while not (self.inp[0] == '-' and self.inp[1] == '-' and self.inp[2] == '>'):
                        self.inp = self.inp[1:]
                    self.inp = self.inp[3:]
                else:
                    self.inp = self.inp[1:]
                    self.prev_token = '<'
                    return '<'

            elif self.inp[0] == '\'':
                self.const = self.inp[1]
                if self.inp[2] == '\'':
                    self.inp = self.inp[3:]
                    self.prev_token = 'cc'
                    return 'cc'

                else:
                    raise SyntaxError

            elif self.inp[0] == '"':
                self.inp = self.inp[1:]
                self.const = ''
                while len(self.inp) != 0 and self.inp[0] != '"':
                    self.const += self.inp[0]
                    self.inp = self.inp[1:]
                if len(self.inp) == 0:
                    raise SyntaxError
                self.inp = self.inp[1:]
                self.prev_token = 'sc'
                return 'sc'

            elif self.inp[:4] == 'true':
                self.const = True
                self.inp = self.inp[4:]
                self.prev_token = 'bc'
                return 'bc'

            elif self.inp[:5] == 'false':
                self.const = False
                self.inp = self.inp[5:]
                self.prev_token = 'bc'
                return 'bc'

            elif self.inp[0] in digits:
                if self.inp[:2] == '0x' and self.inp[2] in digits:
                    self.const = 0
                    self.inp = self.inp[2:]
                    while self.inp[0] in digits or self.inp[0] in ['A', 'B', 'C', 'D', 'E', 'F']:
                        if self.inp[0] in digits:
                            self.const = self.const * 16 + (int(self.inp[0]))
                        else:
                            self.const = self.const * 16 + (ord(self.inp[0]) - 55)
                        self.inp = self.inp[1:]

                    self.prev_token = 'ic'
                    return 'ic'

                else:
                    self.const = 0
                    while len(self.inp)>0 and self.inp[0] in digits:
                        self.const = self.const * 10 + int(self.inp[0])
                        self.inp = self.inp[1:]
                    if len(self.inp)>0 and self.inp[0] == '.':
                        self.inp = self.inp[1:]
                        po = -1
                        while self.inp[0] in digits:
                            self.const = self.const + int(self.inp[0]) * pow(10, po)
                            self.inp = self.inp[1:]
                            po -= 1
                        self.prev_token = 'rc'
                        return 'rc'

                    else:
                        self.prev_token = 'ic'
                        return 'ic'

            elif self.inp[0] in white_spaces:
                self.inp = self.inp[1:]

            else:
                for i in range(2, 10):
                    if self.inp[:i] in data_types or self.inp[:i] in key_words:
                        token = self.inp[:i]
                        self.inp = self.inp[i:]
                        self.prev_token = token
                        if token == 'function' or token == 'procedure':
                            init_scope()
                            # symbol_table_stack.append(dict(symbol_table_stack[-1]))
                            self.ignore = True
                        if token == 'begin':
                            if self.prev_token == 'then' or self.prev_token == 'do':
                                init_scope()
                                # symbol_table_stack.append(dict(symbol_table_stack[-1]))
                        elif token == 'end':
                            symbol_table_stack.pop(-1)
                        return token
                m = re.match(r"([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*", self.inp)
                if m:
                    self.id = m.group()
                    self.inp = self.inp[len(self.id):]
                    if not self.ignore:
                        if self.id not in symbol_table_stack[-1].keys():
                            if self.next_token() == ':' or self.prev_token == 'function' or self.prev_token == 'procedure':
                                symbol_table_stack[-1][self.id] = SymbolData(self.id)
                            else:
                                raise NotImplementedError
                    else:
                        if self.id not in symbol_table_stack[-2].keys():
                            if self.next_token() == ':' or self.prev_token == 'function' or self.prev_token == 'procedure':
                                symbol_table_stack[-2][self.id] = SymbolData(self.id)
                            else:
                                raise NotImplementedError

                    self.prev_token = 'id'
                    return 'id'
                else:
                    print('=======')
                    print(self.inp)
                    raise SyntaxError


scanner = Scanner()
# for i in range(100):
#     print(scanner.scan())
# character constant: cc
# string constant: sc
# bool constant: bc
# int constant: ic
# real constant: rc
