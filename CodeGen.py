from Scanner import SymbolData, symbol_table_stack
import re


class CodeGen:
    def __init__(self, scanner):
        self.stack = []
        self.ops = []
        self.is_glob = True
        self.func_mode = False
        self.unnamed_count = '_0'
        self.scanner = scanner
        self.proc = False
        self.var = None
        self.uni = []
        self.bra = True
        self.begin_block_index = 0
        self.str_len = 0
        self.arr_point = 0

    def CG(self, func, token):
        # print('===========')
        # print(func , token)
        if func == '@push':
            if token == 'id':
                self.stack.append(self.scanner.id)
            elif token == 'ic' or token == 'cc' or token == 'sc' or token == 'rc' or token == 'bc' or token == 'lc':
                if len(self.uni) != 0 and self.uni[-1] == '-':
                    if token == 'ic' or token == 'lc':
                        self.stack.append(str(-self.scanner.const))
                        self.uni = self.uni[:-1]
                elif len(self.uni) != 0 and self.uni == '~':
                    if token == 'ic' or token == 'lc':
                        self.stack.append(str(~self.scanner.const))
                        self.uni = self.uni[:-1]
                else:
                    self.stack.append(str(self.scanner.const))
                if token == 'sc':
                    s_var = self.get_unnamed('')
                    self.str_len = len(self.scanner.const) + 1
                    self.ops = ['@' + s_var + ' = internal constant [' + str(self.str_len) + ' x i8] c' + '\"' + self.scanner.const + '\\00\"'] + self.ops
            else:
                self.stack.append(token)

        elif func == '@push_access':
            #TODO get type
            type = 'i32'
            self.ops.append('%' + self.unnamed_count + ' = getelementptr ' + type + ', ' + type + '* %' + self.scanner.id \
            + ', i32 0')
            self.arr_point = len(self.ops)-1
            # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
            self.stack.append(self.unnamed_count)
            self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
            if len(self.uni) != 0 and self.uni[-1] == '-':
                self.ops.append('%' + self.unnamed_count + ' = sub ' + type + ' 0, %' + self.scanner.id)
                self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
                self.stack[-1].append(self.unnamed_count)
                # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
                self.uni = self.uni[:-1]
            elif len(self.uni) != 0 and self.uni[-1] == '~':
                self.ops.append('%' + self.unnamed_count + ' = xor i1 1, %' + self.stack[-1])
                self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
                self.stack[-1].append(self.unnamed_count)
                # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
                self.uni = self.uni[:-1]

        elif func == '@ret_id':
            type = 'i32'
            self.ops.append('ret ' + type + ' %' + self.scanner.id)

        elif func == '@def_var':
            if token == 'TYPE':
                self.def_var()

        elif func == '@def_arr':
            self.def_arr()

        elif func == '@set_type':
            self.set_type()

        elif func == '@init_arr':
            self.stack.append('')
            self.stack.append('')

        elif func == '@def_dim':
            dim = self.stack[-1]
            self.stack = self.stack[:-1]
            self.stack[-1] += ']'
            self.stack[-2] += '[' + str(dim) + ' x '

        elif func == '@enter_def_func_mode':
            self.func_mode = True
            self.stack.append('')

        elif func == '@exit_def_func_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[-1] = self.stack[-1][:len(self.stack[-1]) - 2]

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
            if self.bra:
                self.ops.append('{')
            self.begin_block_index = len(self.stack)

        elif func == '@out_bra':
            if self.proc:
                self.ops.append('ret void')
                self.proc = False
            if self.bra:
                self.ops.append('}')
            else:
                self.bra = True
            self.stack = self.stack[:self.begin_block_index]

        elif func == '@dcl_assign':
            if token == 'ASSIGNMENT':
                print(self.stack)
                # type = symbol_table_stack[-1][self.var].type
                # TODO get type
                type = 'i32'
                self.ops.append('store ' + type + ' %' + self.stack[-1] + ', ' + type + '* %' + self.var)

        elif func == '@assign':
            if token == 'ASSIGNMENT':
                # type = symbol_table_stack[-1][self.stack[-1]].type
                # TODO get type
                type = 'i32'
                acc = ' '
                try:
                    int(self.stack[-1])
                except:
                    acc = ' %'
                self.ops.append('store ' + type + acc + self.stack[-1] + ', ' + type + '* %' + self.stack[-2])

        elif func == '@access':
            self.access()

        elif func == '@assign_access':
            # TODO get type
            type = 'i32'
            cont = ''
            arr = []
            while True:
                num = False
                try:
                    int(self.stack[-1])
                    num = True
                except:
                    try:
                        int(self.stack[-1][1:])
                    except:
                        break
                if num:
                    arr.append((self.stack[-1], True))

                else:
                    arr.append((self.stack[-1], False))
                self.stack = self.stack[:-1]
            for i in range(len(arr) - 1, -1, -1):
                if arr[i][1]:
                    cont += ', i32 ' + arr[i][0]
                else:
                    cont += ', i32 %' + arr[i][0]

            self.ops[self.arr_point] += cont
            self.stack = self.stack[:-1]


        elif func == '@mult_div_mod':
            op = self.stack[-2]  # * / %
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            type_op1 = None
            type_op2 = None

            m1 = re.compile("^([0-9])+")
            m2 = re.compile("^([0-9])+([.])([0-9])+")
            m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")

            print(symbol_table_stack[-1].keys())
            print(symbol_table_stack[-2].keys())

            if m3.match(op1):
                type_op1 = self.find(op1)
            elif m1.match(op1):
                type_op1 = 'integer'
            elif m2.match(op1):
                type_op1 = 'float'
            else:
                raise TypeError

            if m3.match(op2):
                type_op2 = self.find(op2)
            elif m1.match(op2):
                type_op2 = 'integer'
            elif m2.match(op2):
                type_op2 = 'float'
            else:
                raise TypeError

            if type_op1 == type_op2:
                if type_op1 == 'integer':
                    if op == '*':
                        self.instruction('mul i32', op1, op2)
                    elif op == '/':
                        self.instruction('sdiv i32', op1, op2)
                    elif op == '%':
                        self.instruction('srem i32', op1, op2)
                if type_op1 == 'float':
                    if op == '*':
                        self.instruction('fmul float', op1, op2)
                    elif op == '/':
                        self.instruction('fdiv float', op1, op2)
                    elif op == '%':
                        self.instruction('frem float', op1, op2)

            else:
                if type_op1 == 'integer':
                    self.cast(op1,'float')
                    op1=self.stack.pop(-1)
                if type_op2 == 'integer':
                    self.cast(op2,'float')
                    op2=self.stack.pop(-1)
                if op == '*':
                    self.instruction('fmul float', op1, op2)
                elif op == '/':
                    self.instruction('fdiv float', op1, op2)
                elif op == '%':
                    self.instruction('frem float', op1, op2)


        elif func == '@plus_minus':
            op = self.stack[-2]  # + -
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == '+':
                self.instruction('add i32', op1, op2)
            elif op == '-':
                self.instruction('sub i32', op1, op2)

        elif func == '@gleq':
            op = self.stack[-2]  # < > <= >=
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == '>':
                self.instruction('icmp sgt i32', op1, op2)
            elif op == '<':
                self.instruction('icmp slt i32', op1, op2)
            elif op == '>=':
                self.instruction('icmp sge i32', op1, op2)
            elif op == '<=':
                self.instruction('icmp sle i32', op1, op2)

        elif func == '@eq':
            op = self.stack[-2]  # == <>
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == '==':
                self.instruction('icmp eq i32', op1, op2)
            elif op == '<>':
                self.instruction('icmp neq i32', op1, op2)

        elif func == '@band':
            op = self.stack[-2]  # &
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == '&':
                self.instruction('and i32', op1, op2)

        elif func == '@bxor':
            op = self.stack[-2]  # ^
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == '^':
                self.instruction('xor i32', op1, op2)

        elif func == '@bor':
            op = self.stack[-2]  # bor
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == 'bor':
                self.instruction('or i32', op1, op2)

        elif func == '@and':
            op = self.stack[-2]  # and
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == 'and':
                self.instruction('and i1', op1, op2)

        elif func == '@or':
            op = self.stack[-2]  # or
            op1 = self.stack[-1]  # id const
            op2 = self.stack[-3]  # id const
            if op == 'or':
                self.instruction('or i1', op1, op2)

        elif func == '@set_uni_not':
            self.uni.append('~')

        elif func == '@set_uni_neg':
            self.uni.append('-')

        elif func == '@function_call':
            index = -1
            while True:
                try:
                    int(self.stack[index])
                except:
                    try:
                        int(self.stack[index][1:])
                    except:
                        break
                index -= 1
            # TODO fix type
            type = 'i32'
            pop_val = index
            struct = '%' + self.unnamed_count + ' = call ' + type + ' @' + self.stack[index] + '('
            index += 1
            while index != 0:
                type = 'i32'
                var_type = ' '
                try:
                    int(self.stack[index])
                except:
                    var_type = ' %'
                struct += type + var_type + self.stack[index] + ','
                index += 1
            self.ops.append(struct[:-1] + ')')
            self.stack = self.stack[:pop_val]
            self.stack.append(self.unnamed_count)
            # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
            self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
            if len(self.uni) != 0 and self.uni[-1] == '-':
                self.ops.append('%' + self.unnamed_count + ' = sub ' + type + ' 0, %' + self.stack[-1])
                self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
                self.stack[-1] = self.unnamed_count
                # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
                self.uni = self.uni[:-1]
            elif len(self.uni) != 0 and self.uni[-1] == '~':
                self.ops.append('%' + self.unnamed_count + ' = xor i1 1, %' + self.stack[-1])
                self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
                self.stack[-1] = self.unnamed_count
                # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
                self.uni = self.uni[:-1]

        elif func == '@if':
            self.bra = False
            struct = 'br i1 %' + self.get_unnamed('') + ', label %'
            eq1 = self.get_unnamed('label')
            eq2 = self.get_unnamed('label')
            struct += eq1 + ', label %' + eq2
            self.ops.append(struct)
            self.stack.append(eq2)
            self.ops.append(eq1 + ':')

        elif func == '@end_if':
            self.ops.append(self.stack[-1] + ':')

        elif func == '@else':
            self.bra = False
            eq = self.get_unnamed('label')
            top = self.ops[-1]
            self.ops = self.ops[:-1]
            self.ops.append('br label %' + eq)
            self.stack.append(eq)
            self.ops.append(top)

        elif func == '@end_else':
            self.ops.append(self.stack[-1] + ':')

        elif func == '@while':
            self.bra = False
            here = self.get_unnamed('label')
            there = self.get_unnamed('label')
            self.ops.append('br i1 %' + self.stack[-1] + ', label %' + here + ', label %' + there)
            self.ops.append(here + ':')
            self.stack.append(here)
            self.stack.append(there)

        elif func == '@end_while':
            start = self.stack[-4]
            there = self.stack[-1]
            self.stack = self.stack[:-2]
            self.ops.append('br label %' + start)
            self.ops.append(there + ':')

        elif func == '@start_while':
            start = self.get_unnamed('label')
            self.stack.append(start)
            self.ops.append(start + ':')

        elif func == '@bulk_start':
            self.stack.append([])

        elif func == '@add_bulk':
            self.stack[-2].append(self.stack[-1])
            self.stack = self.stack[:-1]

        elif func == '@assign_bulk':
            # type = symbol_table_stack[-1][self.stack[-1]].type
            # TODO get type
            type = 'i32'
            acc = ' '
            try:
                int(self.stack[-1])
            except:
                acc = ' %'
            self.ops.append('store ' + type + acc + self.stack[-1] + ', ' + type + '* %' + self.stack[-2][0])
            self.stack = self.stack[:-1]
            self.stack[-1] = self.stack[-1][1:]

        # print(self.stack)
        # print(self.ops)

    def access(self):
        # TODO get type
        type = 'i32'
        cont = ''
        arr = []
        while True:
            num = False
            try:
                int(self.stack[-1])
                num = True
            except:
                try:
                    int(self.stack[-1][1:])
                except:
                    break
            if num:
                arr.append((self.stack[-1], True))

            else:
                arr.append((self.stack[-1], False))
            self.stack = self.stack[:-1]
        for i in range(len(arr) - 1, -1, -1):
            if arr[i][1]:
                cont += ', i32 ' + arr[i][0]
            else:
                cont += ', i32 %' + arr[i][0]
        struct = '%' + self.unnamed_count + ' = getelementptr ' + type + ', ' + type + '* %' + self.stack[-1] \
                 + ', i32 0' + cont
        self.ops.append(struct)
        self.stack = self.stack[:-1]
        # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
        self.stack.append(self.unnamed_count)
        self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
        if len(self.uni) != 0 and self.uni[-1] == '-':
            self.ops.append('%' + self.unnamed_count + ' = sub ' + type + ' 0, %' + self.stack[-1])
            self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
            self.stack[-1] = self.unnamed_count
            # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
            self.uni = self.uni[:-1]
        elif len(self.uni) != 0 and self.uni[-1] == '~':
            self.ops.append('%' + self.unnamed_count + ' = xor i1 1, %' + self.stack[-1])
            self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
            self.stack[-1] = self.unnamed_count
            # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
            self.uni = self.uni[:-1]

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
        elif type == 'string':
            op_type = '[   x i8]'
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
        self.set_type()
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
        self.var = self.stack[-2]
        self.stack = self.stack[:-2]

    def instruction(self, inst, op1, op2):
        self.stack = self.stack[:-3]
        var_const_1 = ' '
        try:
            int(op1)
        except:
            var_const_1 = ' %'
        var_const_2 = ' '
        try:
            int(op2)
        except:
            var_const_2 = ' %'
        self.ops.append('%' + self.unnamed_count + ' = ' + inst + var_const_1 + op1 + ',' + var_const_2 + op2)
        self.stack.append(self.unnamed_count)
        # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
        self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)

    def find(self, id):
        type = None
        for i in range(len(symbol_table_stack) - 1, -1, -1):
            if id in symbol_table_stack[i]:
                type = symbol_table_stack[i][id].type
                break
        if type is None:
            print('WWWWWTTTTTFFFFF!!!')
            raise KeyError
        return type

    def cast(self, type2, id1):
        if self.find(id1) == 'integer':
            var_const_1 = ' '
            try:
                int(id1)
            except:
                var_const_1 = ' %'
            self.ops.append('%' + self.unnamed_count + ' = ' + 'sitofp' + 'i32' + var_const_1 + id1 + 'to' + type2)
            self.stack.append(self.unnamed_count)

            symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count,
                                                                    type=symbol_table_stack[-1][id1].type)
            self.stack.append(self.unnamed_count)
            self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)

    def get_unnamed(self, op):
        ret = self.unnamed_count
        if op != 'label':
            pass
            # symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=symbol_table_stack[-1][op1].type)
        self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
        return ret

    def write(self):
        indent = ''
        with open('Out/main.ll', 'w+') as out:
            for op in self.ops:
                if op == '}':
                    indent = indent[:-1]
                out.write(indent + op + '\n')
                if op == '{':
                    indent += '\t'
