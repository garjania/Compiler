class CodeGen:
    def __init__(self, scanner):
        self.stack = []
        self.ops = []
        self.DSTB = {}
        self.is_glob = True
        self.func_mode = False
        self.unnamed_count = 0
        self.scanner = scanner
        self.proc = False

    def CG(self, func, token):
        print('===========')
        print(func)

        if func == '@push':
            if token == 'id':
                self.stack.append(self.scanner.id)
            elif token == 'ic' or token == 'cc' or token == 'sc' or token == 'rc' or token == 'bc':
                self.stack.append(self.scanner.const)
            else:
                self.stack.append(token)

        elif func == '@def_var':
            self.def_var()

        elif func == '@def_arr':
            self.def_arr()

        elif func == '@init_arr':
            self.stack.append('')
            self.stack.append('')

        elif func == '@def_dim':
            dim = self.stack[len(self.stack) - 1]
            self.stack = self.stack[:len(self.stack) - 1]
            self.stack[len(self.stack) - 1] += ']'
            self.stack[len(self.stack) - 2] += '[' + str(dim) + ' x '

        elif func == '@set_type':
            self.set_type()

        elif func == '@enter_def_func_mode':
            self.func_mode = True
            self.stack.append('')

        elif func == '@exit_def_func_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[len(self.stack) - 1] = self.stack[len(self.stack) - 1][:len(self.stack[len(self.stack) - 1]) - 2]

        elif func == '@comp_func':
            self.set_type()
            op = 'define ' + self.stack[-1] + ' @' + self.stack[-3] + '(' + \
                 self.stack[-2] + ')'
            self.ops.append(op)
            # TODO add to symbol table and clean stack

        elif func == '@exit_def_proc_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[-1] = self.stack[-1][:len(self.stack[-1]) - 2]
            op = 'define void @' + self.stack[-2] + '(' + \
                 self.stack[-1] + ')'
            self.ops.append(op)
            self.proc = True
            # TODO add to symbol table and clean stack

        elif func == '@in_bra':
            self.ops.append('{')

        elif func == '@out_bra':
            if self.proc:
                self.ops.append('ret void')
                self.proc = False
            self.ops.append('}')

        elif func == '@mult':
            # TODO cast
            inst = 'mul i32'
            self.instruction(inst)

        elif func == '@div':
            # TODO cast
            inst = 'udiv double'
            self.instruction(inst)

        elif func == '@mod':
            # TODO cast
            inst = 'srem i32'
            self.instruction(inst)

        print(self.stack)
        print(self.ops)

    def set_type(self):
        type = self.stack[len(self.stack) - 1]
        self.stack = self.stack[:len(self.stack) - 1]
        # TODO Correct Type
        if type == 'integer':
            op_type = 'i32'
        elif type == 'real':
            op_type = 'float'
        elif type == 'boolean':
            op_type = 'i1'
        else:
            op_type = 'i8'
        self.stack.append(op_type)

    def def_arr(self):
        if not self.func_mode:
            # TODO if was declared before return err and add to symbol table
            self.DSTB[self.stack[len(self.stack) - 4]] = ['ARR', self.stack[len(self.stack) - 1]]
            if self.is_glob:
                sign = '@'
                allo_type = ' = weak global '
            else:
                sign = '%'
                allo_type = ' = alloca '
            struct = sign + self.stack[len(self.stack) - 4] + allo_type + self.stack[len(self.stack) - 3] + \
                     self.stack[len(self.stack) - 1] + self.stack[len(self.stack) - 2]
            self.ops.append(struct)
        else:
            struct = self.stack[len(self.stack) - 3] + self.stack[len(self.stack) - 1] + \
                     self.stack[len(self.stack) - 2] + ' %' + self.stack[len(self.stack) - 4]
            self.stack[len(self.stack) - 5] += struct + ', '
        self.stack = self.stack[:len(self.stack) - 4]

    def def_var(self):
        if not self.func_mode:
            # TODO if was declared before return err
            self.DSTB[self.stack[len(self.stack) - 2]] = ['VAR', self.stack[len(self.stack) - 1]]
            if self.is_glob:
                struct = '@' + self.stack[len(self.stack) - 2] + ' = weak global ' + self.stack[len(self.stack) - 1] + ' 0 '
            else:
                struct = '%' + self.stack[len(self.stack) - 2] + ' = alloca ' + self.stack[len(self.stack) - 1]
            self.ops.append(struct)
        else:
            struct = self.stack[len(self.stack) - 1] + ' %' + self.stack[len(self.stack) - 2]
            self.stack[len(self.stack) - 3] += struct + ', '
        self.stack = self.stack[:len(self.stack) - 2]

    def instruction(self, inst):
        op1 = self.stack[len(self.stack) - 1]
        op2 = self.stack[len(self.stack) - 2]
        self.stack = self.stack[:len(self.stack) - 2]
        # TODO add unnamed to symbol table and push it to stack
        self.ops.append('%' + str(self.unnamed_count) + ' = ' + inst + ' %' + op1 + ' %' + op2)

    def write(self):
        indent = ''
        with open('Out/main.ll', 'w+') as out:
            for op in self.ops:
                if op == '}':
                    indent = indent[:-1]
                out.write(indent + op + '\n')
                if op == '{':
                    indent += '\t'
