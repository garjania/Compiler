class CodeGen:
    def __init__(self):
        self.stack = []
        self.ops = []
        self.DSTB = {}
        self.is_glob = True

    def CG(self, func, token):
        print('===========')
        print(func)

        if func == '@push':
            self.stack.append(token)

        elif func == '@def_var':
            # TODO if was declared before return err
            self.DSTB[self.stack[len(self.stack) - 2]] = ['VAR', self.stack[len(self.stack) - 1]]
            if self.is_glob:
                allo_type = ' = weak global '
            else:
                allo_type = ' = alloca '
            struct = '%' + self.stack[len(self.stack)-2] + allo_type + self.stack[len(self.stack)-1]
            self.ops.append(struct)
            self.stack = self.stack[:len(self.stack) - 2]

        elif func == '@def_arr':
            # TODO if was declared before return err
            self.DSTB[self.stack[len(self.stack) - 4]] = ['ARR', self.stack[len(self.stack) - 1]]
            if self.is_glob:
                allo_type = ' = weak global '
            else:
                allo_type = ' = alloca '
            struct = '%' + self.stack[len(self.stack) - 4] + allo_type + self.stack[len(self.stack) - 3] + \
                     self.stack[len(self.stack) - 1] + self.stack[len(self.stack) - 2]
            self.ops.append(struct)
            self.stack = self.stack[:len(self.stack) - 4]


        elif func == '@init_arr':
            self.stack.append('')
            self.stack.append('')

        elif func == '@def_dim':
            dim = self.stack[len(self.stack) - 1]
            self.stack = self.stack[:len(self.stack) - 1]
            self.stack[len(self.stack) - 1] += ']'
            self.stack[len(self.stack) - 2] += '[' + dim + ' x '

        elif func == '@set_type':
            type = self.stack[len(self.stack)-1]
            self.stack = self.stack[:len(self.stack) - 1]
            # TODO Correct Type
            if type == 'type':
                op_type = 'i32'
            self.stack.append(op_type)

        print(self.stack)
        print(self.ops)