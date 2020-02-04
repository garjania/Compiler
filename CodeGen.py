from Scanner import SymbolData, symbol_table_stack


class CodeGen:
    def __init__(self, scanner):
        self.stack = []
        self.ops = []
        self.is_glob = True
        self.func_mode = False
        self.unnamed_count = '_0'
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
            dim = self.stack[-1]
            self.stack = self.stack[:-1]
            self.stack[-1] += ']'
            self.stack[-2] += '[' + str(dim) + ' x '

        elif func == '@set_type':
            self.set_type()

        elif func == '@enter_def_func_mode':
            self.func_mode = True
            self.stack.append('')

        elif func == '@exit_def_func_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[-1] = self.stack[-1][:len(self.stack[-1])-2]

        elif func == '@comp_func':
            self.set_type()
            op = 'define ' + self.stack[-1] + ' @' + self.stack[-3] + '(' + \
                 self.stack[-2] + ')'
            self.ops.append(op)
            # TODO add to symbol table and clean stack

        elif func == '@exit_def_proc_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[-1] = self.stack[-1][:len(self.stack[-1])-2]
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

        elif func == '@mult_div_mod':
            op = self.stack[-2] # * / %
            op1 = self.stack[-1] # id const
            op2 = self.stack[-3] # id const
            if op == '*':
                self.instruction('mul i32', op1, op2)
            elif op == '/':
                self.instruction('udiv float', op1, op2)
            elif op == 'mod':
                self.instruction('srem i32', op1, op2)


        print(self.stack)
        print(self.ops)

    def set_type(self):
        type = self.stack[-1]
        self.stack = self.stack[:-1]
        if type == 'integer':
            op_type = 'i32'
        elif type == 'real':
            op_type = 'float'
        elif type == 'boolean':
            op_type = 'i1'
        elif type == 'long':
            op_type = 'i64'
        else:
            op_type = 'i8'
        self.stack.append(op_type)

    def def_arr(self):
        if not self.func_mode:
            if self.is_glob:
                sign = '@'
                allo_type = ' = weak global '
            else:
                sign = '%'
                allo_type = ' = alloca '
            struct = sign + self.stack[-4] + allo_type + self.stack[-3] + self.stack[-1] + self.stack[-2]
            self.ops.append(struct)
        else:
            struct = self.stack[-3] + self.stack[-1] + self.stack[-2] + ' %' + self.stack[-4]
            self.stack[-5] += struct + ', '
        # symbol_table_stack[-1][self.stack[-4]].type = self.stack[-1]
        # symbol_table_stack[-1][self.stack[-4]].array = True
        self.stack = self.stack[:-4]

    def def_var(self):
        if not self.func_mode:
            if self.is_glob:
                struct = '@' + self.stack[-2] + ' = weak global ' + self.stack[-1] + ' 0 '
            else:
                struct = '%' + self.stack[-2] + ' = alloca ' + self.stack[-1]
            self.ops.append(struct)
        else:
            struct = self.stack[-1] + ' %' + self.stack[-2]
            self.stack[-3] += struct + ', '
        # symbol_table_stack[-1][self.stack[-4]].type = self.stack[-1]
        self.stack = self.stack[:-2]

    def instruction(self, inst, op1, op2):
        self.stack = self.stack[:-3]
        self.ops.append('%' + self.unnamed_count + ' = ' + inst + ' %' + op1 + ' %' + op2)
        self.stack.append(self.unnamed_count)
        # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
        self.unnamed_count = '_' + str(int(self.unnamed_count[1:])+1)

    def find(self, id):
        type = None
        for i in range(len(symbol_table_stack)-1, -1, -1):
            if id in symbol_table_stack[i]:
                type = symbol_table_stack[i][id].type
                break
        if type is None:
            print('WWWWWTTTTTFFFFF!!!')
            raise KeyError
        return type
    # TODO cast
    # def cast(self, type1, type2, id1, id2):
    #     if type1 == type2 == 'i64':
    #         return type1
    #     self.stack.append(self.unnamed_count)
    #     symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count,
    #                                                             type=symbol_table_stack[-1][op1].type)
    #     self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
    #     if type1 != 'float':
    #         self.proc.append('')



    def write(self):
        indent = ''
        with open('Out/main.ll', 'w+') as out:
            for op in self.ops:
                if op == '}':
                    indent = indent[:-1]
                out.write(indent + op + '\n')
                if op == '{':
                    indent += '\t'
