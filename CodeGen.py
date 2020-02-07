from Scanner import SymbolData, symbol_table_stack
import re


class CodeGen:
    def __init__(self, scanner):
        self.stack = []
        self.ops = ['@.i32 = private unnamed_addr constant [3 x i8] c"%d\\00" ',
                    '@.i8 = private unnamed_addr constant [3 x i8] c"%c\\00" ',
                    '@.i64 = private unnamed_addr constant [3 x i8] c"%f\\00" ',
                    '@.i1 = private unnamed_addr constant [3 x i8] c"%d\\00" ',
                    '@.str = private unnamed_addr constant [3 x i8] c"%s\\00" ',
                    'declare i32 @scanf(i8*, ...)',
                    'declare i32 @printf(i8*, ...)']
        self.is_glob = True
        self.func_mode = False
        self.unnamed_count = '_0'
        self.scanner = scanner
        self.proc = False
        self.var = None
        self.bra = True
        self.begin_block_index = 0
        self.str_len = 0
        self.is_bulk = False
        self.assign = False
        self.token = ''
        self.arg = ''

    def CG(self, func, token):
        # print('===========')
        # print(func, token)
        # print(self.stack)
        if func == '@push':
            self.push(token)

        elif func == '@push_access':
            self.push(token)
            sym = self.search(self.stack[-1])
            self.arg = self.stack[-1]
            if sym.array:
                self.assign = True
            if not sym.array and not sym.function:
                if not sym.arg:
                    name = self.get_unnamed(sym.type)
                    if sym.is_string:
                        type = sym.size + '*'
                        self.search(name).type = sym.size
                        self.search(name).is_string = True
                    else:
                        type = sym.type
                    self.ops.append(sym.glob_loc + name + ' = load ' + type + ', ' + type + '* ' + sym.glob_loc +
                                    self.stack[-1])
                    self.stack[-1] = name
                self.handle_uni()

        elif func == '@ret_id':
            try:
                sym = self.search(self.stack[-1])
                self.ops.append('ret ' + sym.type + ' ' + sym.glob_loc + self.stack[-1])
            except:
                if self.token == 'ic':
                    type = 'i32'
                elif self.token == 'lc':
                    type = 'i64'
                elif self.token == 'cc':
                    type = 'i8'
                elif self.token == 'bc':
                    type = 'i1'
                elif self.token == 'rc':
                    type = 'float'
                self.ops.append('ret ' + type + ' ' + self.stack[-1])

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
            sym = self.search(self.stack[-3])
            sym.type = self.stack[-1]
            sym.function = True
            self.stack = self.stack[:-3]

        elif func == '@exit_def_proc_mode':
            self.func_mode = False
            self.is_glob = False
            self.stack[-1] = self.stack[-1][:len(self.stack[-1]) - 2]
            op = 'define void @' + self.stack[-2] + '(' + \
                 self.stack[-1] + ')'
            self.ops.append(op)
            self.proc = True
            sym = self.search(self.stack[-2])
            sym.type = 'void'
            sym.function = True
            self.stack = self.stack[:-2]

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
                acc = ' '
                type = self.search(self.var).type
                sym = self.search(self.var)
                if sym is None or not sym.is_string:
                    print(self.stack)
                    try:
                        if self.find(self.stack[-1]) != type:
                            if self.find(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':
                                self.cast(type, self.stack[-1])
                        acc = ' %'
                    except KeyError:
                        if self.type_of_const(self.stack[-1]) != type:
                            if self.type_of_const(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':
                                self.cast(type, self.stack[-1])
                            acc = ' %'

                    self.ops.append('store ' + type + acc + self.stack[-1] + ', ' + type + '* %' + self.var)

                else:
                    str_sym = self.search(self.stack[-1])
                    sym.size = str_sym.type
                    self.ops.append(
                        'store ' + sym.size + '* getelementptr inbounds (' + sym.size + ', ' + sym.size + '* @' +
                        self.stack[-1] + ', i32 0), ' + sym.size + '** ' + sym.glob_loc + self.var)
                    self.ops[sym.allocate_point] = '%' + self.var + ' = alloca ' + sym.size + '*'

        elif func == '@assign':
            if token == 'ASSIGNMENT':
                acc = ' '
                type = self.search(self.stack[-2]).type
                sym = self.search(self.stack[-2])
                var = self.stack[-2]
                if sym is None or not sym.is_string:
                    try:
                        if self.find(self.stack[-1]) != type:
                            if self.find(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':

                                self.cast(type, self.stack[-1])
                        acc = ' %'
                    except KeyError:
                        if self.type_of_const(self.stack[-1]) != type:
                            if self.type_of_const(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':
                                self.cast(type, self.stack[-1])
                    # self.ops.append('asdfasdfs')
                    self.ops.append('store ' + type + acc + self.stack[-1] + ', ' + type + '* %' + var)
                else:
                    str_sym = self.search(self.stack[-1])
                    sym.size = str_sym.type
                    self.ops.append(
                        'store ' + sym.size + '* getelementptr inbounds (' + sym.size + ', ' + sym.size + '* @' +
                        self.stack[-1] + ', i32 0), ' + sym.size + '** ' + sym.glob_loc + var)
                    self.ops[sym.allocate_point] = '%' + self.stack[-2] + ' = alloca ' + sym.size + '*'

        elif func == '@assign_bulk':
            if self.is_bulk:
                acc = ' '
                print(self.stack)
                type = self.search(self.stack[-2][0]).type
                sym = self.search(self.stack[-2][0])
                var = self.stack[-2][0]
                if sym is None or not sym.is_string:
                    try:
                        if self.find(self.stack[-1]) != type:
                            if self.find(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':
                                self.cast(type, self.stack[-1])
                        acc = ' %'
                    except KeyError:
                        if self.type_of_const(self.stack[-1]) != type:
                            if self.type_of_const(self.stack[-1]) != 'i64':
                                self.cast('i64', self.stack[-1])
                            if type != 'i64':
                                self.cast(type, self.stack[-1])
                    self.ops.append('store ' + type + acc + self.stack[-1] + ', ' + type + '* %' + var)
                else:
                    str_sym = self.search(self.stack[-1])
                    sym.size = str_sym.type
                    self.ops.append(
                        'store ' + sym.size + '* getelementptr inbounds (' + sym.size + ', ' + sym.size + '* @' +
                        self.stack[-1] + ', i32 0), ' + sym.size + '** ' + sym.glob_loc + self.stack[-2][0])
                    self.ops[sym.allocate_point] = '%' + self.stack[-2][0] + ' = alloca ' + sym.size + '*'
                self.stack = self.stack[:-1]
                self.stack[-1] = self.stack[-1][1:]

        elif func == '@access':
            self.access()

        elif func == '@mult_div_mod':
            if len(self.stack) >= 3 and (self.stack[-2] == '*' or self.stack[-2] == '/' or self.stack[-2] == '%'):
                op = self.stack[-2]  # * / %
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                print(op1, op2)

                m1 = re.compile("^([0-9])+")
                m2 = re.compile("^([0-9])+([.])([0-9])+")
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                # elif m2.match(op1):
                #     type_op1 = 'float'
                # elif m1.match(op1):
                #     if abs(op1) > 128:
                #         type_op1 = 'i64'
                #     else:
                #         type_op1 = 'i32'
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'float':
                    if type_op1 != 'i64':
                        self.cast('i64', op1)
                        op1 = self.stack.pop(-1)
                    self.cast('float', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                # elif m2.match(op2):
                #     type_op2 = 'float'
                # elif m1.match(op2):
                #     if abs(op2) > 128:
                #         type_op2 = 'i64'
                #     else:
                #         type_op2 = 'i32'
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    if type_op2 != 'i64':
                        self.cast('i64', op2)
                        op2 = self.stack.pop(-1)
                    self.cast('float', op2)
                    op2 = self.stack.pop(-1)
                if op == '*':
                    self.instruction('fmul float', op1, op2)
                elif op == '/':
                    self.instruction('fdiv float', op1, op2)
                elif op == '%':
                    self.instruction('frem float', op1, op2)

        elif func == '@plus_minus':
            if len(self.stack) >= 3 and (self.stack[-2] == '+' or self.stack[-2] == '-'):

                op = self.stack[-2]  # * / %
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                print(op1, op2)

                m1 = re.compile("^([0-9])+")
                m2 = re.compile("^([0-9])+([.])([0-9])+")
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                # elif m2.match(op1):
                #     type_op1 = 'float'
                # elif m1.match(op1):
                #     if abs(op1) > 128:
                #         type_op1 = 'i64'
                #     else:
                #         type_op1 = 'i32'
                # else:
                #     raise TypeError
                #
                # if m3.match(op2) or m4.match(op2):
                #     type_op2 = self.find(op2)
                # elif m2.match(op2):
                #     type_op2 = 'float'
                # elif m1.match(op2):
                #     if abs(op2) > 128:
                #         type_op2 = 'i64'
                #     else:
                #         type_op2 = 'i32'
                # else:
                #     raise TypeError
                #
                # if type_op1 == type_op2:
                #     if type_op1 == 'i64':
                #         if op == '+':
                #             self.instruction('add i64', op1, op2)
                #         elif op == '-':
                #             self.instruction('sub i64', op1, op2)
                #     if type_op1 == 'i32':
                #         if op == '+':
                #             self.instruction('add i32', op1, op2)
                #         elif op == '-':
                #             self.instruction('sub i32', op1, op2)
                #     if type_op1 == 'float':
                #         if op == '+':
                #             self.instruction('fadd float', op1, op2)
                #         elif op == '-':
                #             self.instruction('fsub float', op1, op2)

                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'float':
                    if type_op1 != 'i64':
                        self.cast('i64', op1)
                        op1 = self.stack[-1]
                    self.cast('float', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    if type_op2 != 'i64':
                        self.cast('i64', op2)
                        op2 = self.stack[-1]
                    self.cast('float', op2)
                    op2 = self.stack.pop(-1)
                if op == '+':
                    self.instruction('fadd float', op1, op2)
                elif op == '-':
                    self.instruction('fsub float', op1, op2)

        elif func == '@gleq':
            if len(self.stack) >= 3 and (
                    self.stack[-2] == '>' or self.stack[-2] == '<' or self.stack[-2] == '>=' or self.stack[-2] == '<='):
                op = self.stack[-2]  # < > <= >=
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const

                m1 = re.compile("^([0-9])+")
                m2 = re.compile("^([0-9])+([.])([0-9])+")
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i64':
                    self.cast('i64', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    self.cast('i64', op2)
                    op2 = self.stack.pop(-1)
                type = 'i64'
                if op == '>':
                    self.instruction('icmp slt ' + type, op1, op2)
                elif op == '<':
                    self.instruction('icmp sgt ' + type, op1, op2)
                elif op == '>=':
                    self.instruction('icmp sle ' + type, op1, op2)
                elif op == '<=':
                    self.instruction('icmp sge ' + type, op1, op2)

        elif func == '@eq':
            if len(self.stack) >= 3 and (self.stack[-2] == '==' or self.stack[-2] == '<>'):
                op = self.stack[-2]  # == <>
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const

                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i64':
                    self.cast('i64', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    self.cast('i64', op2)
                    op2 = self.stack.pop(-1)
                type = 'i64'

                if op == '==':
                    self.instruction('icmp eq ' + type, op1, op2)
                elif op == '<>':
                    self.instruction('icmp ne ' + type, op1, op2)

        elif func == '@band':
            if len(self.stack) >= 3 and self.stack[-2] == '&':
                op = self.stack[-2]  # &
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i64':
                    self.cast('i64', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    self.cast('i64', op2)
                    op2 = self.stack.pop(-1)
                type = 'i64'

                self.instruction('and ' + type, op1, op2)

        elif func == '@bxor':
            if len(self.stack) >= 3 and self.stack[-2] == '^':
                op = self.stack[-2]  # ^
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i64':
                    self.cast('i64', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    self.cast('i64', op2)
                    op2 = self.stack.pop(-1)
                type = 'i64'

                self.instruction('xor ' + type, op1, op2)

        elif func == '@bor':
            if len(self.stack) >= 3 and self.stack[-2] == 'bor':
                op = self.stack[-2]  # bor
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i64':
                    self.cast('i64', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i64':
                    self.cast('i64', op2)
                    op2 = self.stack.pop(-1)
                type = 'i64'

                self.instruction('or ' + type, op1, op2)

        elif func == '@and':
            if len(self.stack) >= 3 and self.stack[-2] == 'and':
                op = self.stack[-2]  # and
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i1':
                    if type_op1 != 'i64':
                        self.cast('i64', op1)
                        op1 = self.stack.pop(-1)
                    self.cast('i1', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i1':
                    if type_op2 != 'i64':
                        self.cast('i64', op2)
                        op2 = self.stack.pop(-1)
                    self.cast('i1', op2)
                    op2 = self.stack.pop(-1)
                type = 'i1'

                self.instruction('and ' + type, op1, op2)

        elif func == '@or':
            if len(self.stack) >= 3 and self.stack[-2] == 'or':
                op = self.stack[-2]  # or
                op1 = self.stack[-1]  # id const
                op2 = self.stack[-3]  # id const
                m3 = re.compile("^([A-Z]|[a-z])([A-Z]|[0-9]|[_]|[a-z])*")
                m4 = re.compile("^([_])([0-9])+")

                if m3.match(op1) or m4.match(op1):
                    type_op1 = self.find(op1)
                else:
                    type_op1 = self.type_of_const(op1)

                if type_op1 != 'i1':
                    if type_op1 != 'i64':
                        self.cast('i64', op1)
                        op1 = self.stack.pop(-1)
                    self.cast('i1', op1)
                    op1 = self.stack.pop(-1)

                if m3.match(op2) or m4.match(op2):
                    type_op2 = self.find(op2)
                else:
                    type_op2 = self.type_of_const(op2)

                if type_op2 != 'i1':
                    if type_op2 != 'i64':
                        self.cast('i64', op2)
                        op2 = self.stack.pop(-1)
                    self.cast('i1', op2)
                    op2 = self.stack.pop(-1)
                type = 'i1'

                self.instruction('or ' + type, op1, op2)

        elif func == '@function_call':
            index = -1
            while True:
                try:
                    int(self.stack[index])
                except:
                    sym = self.search(self.stack[index])
                    if sym.function:
                        break
                index -= 1
            type = self.find(self.stack[index])
            pop_val = index
            name = self.get_unnamed(type)
            # print(self.stack[index])
            if self.stack[index] == 'strlen' or self.stack[index] == 'read' or self.stack[index] == 'write':
                self.handle_build_in_functions(index)
            else:
                if type != 'void':
                    struct = '%' + name + ' = call ' + type + ' @' + self.stack[index] + '('
                else:
                    struct = 'call ' + type + ' @' + self.stack[index] + '('
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
                if type != 'void':
                    self.stack.append(name)
                self.handle_uni()

        elif func == '@if':
            self.bra = False
            struct = 'br i1 %' + self.stack[-1] + ', label %'
            self.stack = self.stack[:-1]
            eq1 = self.get_unnamed('label')
            eq2 = self.get_unnamed('label')
            struct += eq1 + ', label %' + eq2
            self.ops.append(struct)
            self.stack.append(eq2)
            self.ops.append(eq1 + ':')

        elif func == '@end_if':
            self.ops.append('br label %' + self.stack[-1])
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
            self.ops.append('br label %' + self.stack[-1])
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
            self.ops.append('br label %' + start)
            self.stack.append(start)
            self.ops.append(start + ':')

        elif func == '@set_bulk':
            self.is_bulk = True

        elif func == '@bulk_start':
            self.stack.append([])

        elif func == '@add_bulk':
            self.stack[-2].append(self.stack[-1])
            self.stack = self.stack[:-1]

        elif func == '@end_bulk_assign':
            self.is_bulk = False

        # print(self.stack)
        # print(self.ops)

    def access(self):
        cont = ''
        arr = []
        while True:
            num = False
            try:
                int(self.stack[-1])
                num = True
            except:
                sym = self.search(self.stack[-1])
                if sym.array:
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
        sym = self.search(self.stack[-1])
        name = self.get_unnamed(sym.type)
        struct = '%' + name + ' = getelementptr ' + sym.size + ', ' + sym.size + '* %' + self.stack[-1] \
                 + ', i32 0' + cont
        self.ops.append(struct)
        self.stack = self.stack[:-1]
        self.stack.append(name)
        if self.assign:
            name = self.get_unnamed(sym.type)
            self.ops.append('%' + name + ' = load ' + sym.type + ', ' + sym.type + '* %' + self.stack[-1])
            self.stack = self.stack[:-1]
            self.stack.append(name)
            self.assign = False
        self.handle_uni()

    def push(self, token):
        if token == 'id':
            self.stack.append(self.scanner.id)
        elif token == 'ic' or token == 'cc' or token == 'rc' or token == 'lc':
            self.token = token
            if len(self.stack) != 0 and self.stack[-1] == '-':
                if token == 'ic' or token == 'lc':
                    self.stack = self.stack[:-1]
                    self.stack.append(str(-self.scanner.const))
            elif len(self.stack) != 0 and self.stack[-1] == '~':
                if token == 'ic' or token == 'lc':
                    self.stack = self.stack[:-1]
                    self.stack.append(str(~self.scanner.const))
            else:
                self.stack.append(str(self.scanner.const))

        elif token == 'sc':
            self.str_len = len(self.scanner.const) + 1
            splitted = self.scanner.const.split('\\n')
            self.str_len -= len(splitted) - 1
            out = splitted[0]
            for i in range(len(splitted) - 1):
                out += '\\' + '0A' + splitted[i + 1]
            self.scanner.const = out
            s_var = self.get_unnamed('[' + str(self.str_len) + ' x i8]', True)
            self.ops = ['@' + s_var + ' = internal constant [' + str(
                self.str_len) + ' x i8] c' + '\"' + self.scanner.const + '\\00\"'] + self.ops
            self.stack.append(s_var)
        elif token == 'bc':
            if self.scanner.const == 'True':
                self.stack.append('1')
            else:
                self.stack.append('0')
        else:
            self.stack.append(token)

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
            op_type = 'i8*'
            self.search(self.stack[-1]).is_string = True
        elif type == 'character':
            op_type = 'i8'
        self.stack.append(op_type)

    def def_arr(self):
        sym = self.search(self.stack[-4])
        sym.type = self.stack[-1]
        sym.array = True
        if not self.func_mode:
            if self.is_glob:
                sign = '@'
                allo_type = ' = weak global '
                sym.is_glob = True
            else:
                sign = '%'
                allo_type = ' = alloca '
            struct = sign + self.stack[-4] + allo_type + self.stack[-3] + self.stack[-1] + self.stack[-2]
            self.ops.append(struct)
            sym.allocate_point = len(self.ops)
        else:
            struct = self.stack[-3] + self.stack[-1] + self.stack[-2] + ' %' + self.stack[-4]
            self.stack[-5] += struct + ', '
        sym.size = self.stack[-3] + self.stack[-1] + self.stack[-2]
        self.stack = self.stack[:-4]

    def def_var(self):
        self.set_type()
        sym = self.search(self.stack[-2])
        sym.type = self.stack[-1]
        if not self.func_mode:
            if self.is_glob:
                struct = '@' + self.stack[-2] + ' = weak global ' + self.stack[-1] + ' 0 '
                sym.glob_loc = '@'
            else:
                struct = '%' + self.stack[-2] + ' = alloca ' + self.stack[-1]
            self.ops.append(struct)
            sym.allocate_point = len(self.ops)
        else:
            struct = self.stack[-1] + ' %' + self.stack[-2]
            self.stack[-3] += struct + ', '
            sym.arg = True
        self.var = self.stack[-2]
        self.stack = self.stack[:-2]

    def instruction(self, inst, op1, op2):
        self.stack = self.stack[:-3]
        var_const_1 = ' '
        try:
            type_1 = self.find(op1)
            var_const_1 = ' %'
        except KeyError:
            pass
        var_const_2 = ' '
        try:
            type_2 = self.find(op2)
            var_const_2 = ' %'
        except KeyError:
            pass
        name = self.get_unnamed(inst.split()[-1])
        self.ops.append('%' + name + ' = ' + inst + var_const_1 + op1 + ',' + var_const_2 + op2)

        self.stack.append(name)

    def find(self, id):
        if self.search(id) is None:
            print('WWWWWTTTTTFFFFF!!!')
            raise KeyError
        type = self.search(id).type
        return type

    def search(self, id):
        for i in range(len(symbol_table_stack) - 1, -1, -1):
            if id in symbol_table_stack[i]:
                return symbol_table_stack[i][id]
        return None

    def cast(self, type2, id1):
        var_const_1 = ' '
        try:
            type = self.find(id1)
            var_const_1 = ' %'
        except KeyError:
            type = self.type_of_const(id1)

        if type == 'i32':
            if type2 == 'float':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' sitofp' + ' i32' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
            elif type2 == 'i64':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' zext' + ' i32' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
            else:
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' trunc' + ' i32' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
        elif type == 'float':
            if type2 == 'i64':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' fptosi' + ' float' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
            else:
                raise InterruptedError

        elif type == 'i1' or type == 'i8':
            if type2 == 'i64':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' zext ' + type + ' ' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
            elif type2 == 'float':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' sitofp ' + type + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)
            else:
                raise InterruptedError

        elif type == 'i64':
            if type2 == 'i32' or type2 == 'i8' or type2 == 'i1':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' trunc' + ' i64' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)

            elif type2 == 'float':
                name = self.get_unnamed(type2)
                self.ops.append(
                    '%' + name + ' = ' + ' sitofp' + ' i64' + var_const_1 + id1 + ' to ' + type2)
                self.stack.append(name)

            else:
                print(type, type2)
                raise InterruptedError

        else:
            print(type)
            print(id1)
            raise InterruptedError

    def get_unnamed(self, op, sc=False):
        ret = self.unnamed_count
        if op != 'label':
            symbol_table_stack[-1][self.unnamed_count] = SymbolData(self.unnamed_count, type=op)
            if self.is_glob:
                symbol_table_stack[-1][self.unnamed_count].glob_loc = '@'
            if sc:
                symbol_table_stack[-1][self.unnamed_count].glob_loc = '@'
                symbol_table_stack[-1][self.unnamed_count].is_string = True
                symbol_table_stack[-1][self.unnamed_count].size = op
        self.unnamed_count = '_' + str(int(self.unnamed_count[1:]) + 1)
        return ret

    def handle_uni(self):
        if len(self.stack) > 1 and self.stack[-2] == '-':
            sym = self.search(self.stack[-1])
            name = self.get_unnamed(sym.type)
            self.ops.append('%' + name + ' = sub ' + sym.type + ' 0, %' + self.stack[-1])
            self.stack = self.stack[:-2]
            self.stack.append(name)
        elif len(self.stack) > 1 and self.stack[-2] == '~':
            sym = self.search(self.stack[-1])
            name = self.get_unnamed(sym.type)
            self.ops.append('%' + name + ' = xor i1 1, %' + self.stack[-1])
            self.stack = self.stack[:-2]
            self.stack.append(name)

    def handle_build_in_functions(self, index):
        if self.stack[index] == 'read':
            sym = self.search(self.arg)
            self.ops.append('call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.' + sym.type +
                            ', i32 0, i32 0), ' + sym.type + '* ' + sym.glob_loc + self.arg + ')')
        elif self.stack[index] == 'write':
            inp = self.stack[index + 1]
            sym = self.search(inp)
            if not sym.is_string:
                self.ops.append(
                    'call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.' + sym.type +
                    ', i32 0, i32 0), ' + sym.type + ' ' + sym.glob_loc + inp + ')')
            else:
                if self.search(inp).glob_loc == '@':
                    self.ops.append('call i32 (i8*, ...) @printf(i8* getelementptr inbounds (' + sym.type + ', ' +
                                    sym.type + '* @' + inp + ', i32 0, i32 0))')
                else:
                    self.ops.append('call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]*'
                                    ' @.str, i32 0, i32 0), ' + sym.type + '* %' + inp + ')')

        elif self.stack[index] == 'strlen':
            self.handle_strlen(self.stack[index + 1])

    def handle_strlen(self, input):
        name = self.get_unnamed('i32')
        self.ops.append('%' + name + ' = alloca i32')
        self.ops.append('store i32 0, i32* %' + name)
        lb1 = self.get_unnamed('label')
        self.ops.append('br label %' + lb1)
        self.ops.append(lb1 + ':')
        self.stack.append(name)
        name = self.get_unnamed('i32')
        self.ops.append('%' + name + ' = load i32, i32* %' + self.stack[-1])
        self.stack.append(name)
        name = self.get_unnamed('i8')
        sym = self.search(input)
        self.ops.append(
            '%' + name + ' = getelementptr ' + sym.type + ', ' + sym.type + '* ' + sym.glob_loc + input + ', i32 0, i32 %' +
            self.stack[-1])
        self.stack[-1] = name
        name = self.get_unnamed('i8')
        self.ops.append('%' + name + ' = load i8, i8* %' + self.stack[-1])
        self.stack[-1] = name
        name = self.get_unnamed('i8')
        self.ops.append('%' + name + ' = icmp ne i8 %' + self.stack[-1] + ', 0')
        lb2 = self.get_unnamed('label')
        lb3 = self.get_unnamed('label')
        self.ops.append('br i1 %' + name + ', label %' + lb2 + ', label %' + lb3)
        self.ops.append(lb2 + ':')
        name = self.get_unnamed('i32')
        self.ops.append('%' + name + ' = load i32, i32* %' + self.stack[-2])
        self.stack[-1] = name
        name = self.get_unnamed('i32')
        self.ops.append('%' + name + ' = add nsw i32 %' + self.stack[-1] + ', 1')
        self.ops.append('store i32 %' + name + ', i32* %' + self.stack[-2])
        self.ops.append('br label %' + lb1)
        self.ops.append(lb3 + ':')
        self.stack = self.stack[:-4]
        self.stack.append(name)

    def write(self):
        indent = ''
        with open('Out/main.ll', 'w+') as out:
            for op in self.ops:
                if op == '}':
                    indent = indent[:-1]
                out.write(indent + op + '\n')
                if op == '{':
                    indent += '\t'

    def type_of_const(self, const):
        try:
            int(const)
            if abs(int(const)) > 128:
                type = 'i64'
            else:
                type = 'i32'
        except ValueError:
            try:
                float(const)
                type = 'float'
            except ValueError:
                try:
                    bool(const)
                    type = 'i1'
                except ValueError:
                    if len(const) == 1:
                        type = 'i8'
                    else:
                        type = 'string'
        return type
