import csv


class Parser:
    def __init__(self):
        self.grammar = {'VAR_DCL': [['id', ':', 'SIMPLE_VAR'],
                                    ['id', ':', 'ARRAY_VAR']],
                        'FUNC_DEF': [['function', 'id', '(', ')', ':', 'TYPE', 'BLOCK'],
                                     ['function', 'id', '(', 'VAR_DCL', 'ARG', ')', ':', 'TYPE', 'BLOCK']],
                        'PROC_DEF': [['procedure', 'id', '(', ')', 'BLOCK'],
                                     ['procedure', 'id', '(', 'VAR_DCL', ',VAR_DCL?', ')', 'BLOCK']],
                        'SIMPLE_VAR': [['id', ':', 'TYPE'],
                                       ['id', ':', 'TYPE', 'ASSIGNMENT']],
                        'ARRAY_VAR': [['id', ':', 'array', 'ARRAY_DIM', 'of', 'TYPE']],
                        'ASSIGNMENT': [[':=', 'EXPR']],
                        'TYPE': [['type']],
                        'BLOCK': [['begin', 'STMT_LOOP', 'end']],
                        'STMT': [['return', 'id'],
                                 ['CONDITIONAL'],
                                 ['(', 'ID', ',', 'ID', 'ID_LOOP', ')', 'BULK_ASSIGNMENT'],
                                 ['id', 'STMT_ID'],
                                 ['LOOP']],
                        'FUNCTION_CALL': [['id', '(', ')'],
                                          ['id', '(', 'EXPR', 'EXPR_LOOP', ')']],
                        'ID': [['id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                               ['id']],
                        'LOOP': [['while', '(', 'EXPR', ')', 'do', 'BLOCK']],
                        'CONDITIONAL': [['if', '(', 'EXPR', ')', 'then', 'BLOCK'],
                                        ['if', '(', 'EXPR', ')', 'then', 'BLOCK', 'else', 'BLOCK']],
                        'ARRAY_DIM': [['[', 'ic', 'IC_LOOP', ']']],
                        'BULK_ASSIGNMENT': [[':=', '(', 'EXPR', 'EXPR_LOOP', ')']],
                        'CONSTANT': [['ic'],
                                     ['float'],
                                     ['ch'],
                                     ['str']],
                        'EXPR': [['T', 'EP']],
                        'EP': [['or', 'T', 'EP']],
                        'T': [['F', 'TP']],
                        'TP': [['and', 'F', 'TP']],
                        'F': [['V', 'FP']],
                        'FP': [['bor', 'V', 'FP']],
                        'V': [['S', 'VP']],
                        'VP': [['^', 'S', 'VP']],
                        'S': [['R', 'SP']],
                        'SP': [['&', 'R', 'SP']],
                        'R': [['O', 'RP']],
                        'RP': [['==', 'O', 'RP'],
                               ['<>', 'O', 'RP']],
                        'O': [['P', 'OP']],
                        'OP': [['>', 'P', 'OP'],
                               ['<', 'P', 'OP'],
                               ['>=', 'P', 'OP'],
                               ['<=', 'P', 'OP']],
                        'P': [['W', 'PP']],
                        'PP': [['+', 'W', 'PP'],
                               ['-', 'W', 'PP']],
                        'W': [['Q', 'WP']],
                        'WP': [['*', 'Q', 'WP'],
                               ['/', 'Q', 'WP'],
                               ['%', 'Q', 'WP']],
                        'Q': [['id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                              ['id', '(', ')'],
                              ['id', '(', 'EXPR', 'EXPR_LOOP', ')'],
                              ['CONSTANT'],
                              ['~', 'id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                              ['~', 'id', '(', ')'],
                              ['~', 'id', '(', 'EXPR', 'EXPR_LOOP', ')'],
                              ['~', 'CONSTANT'],
                              ['-', 'id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                              ['-', 'id', '(', ')'],
                              ['-', 'id', '(', 'EXPR', 'EXPR_LOOP', ')'],
                              ['-', 'CONSTANT']],
                        'STMT_ID': [['[', 'EXPR', 'EXPR_LOOP', ']', 'ASSIGNMENT'],
                                    [':', 'SIMPLE_VAR'],
                                    [':', 'ARRAY_VAR'],
                                    ['(', ')'],
                                    ['(', 'EXPR', 'EXPR_LOOP', ')']],
                        'ARG': [[';', 'VAR_DCL', 'ARG']],
                        'STMT_LOOP': [['STMT', ';', 'STMT_LOOP']],
                        'ID_LOOP': [[',', 'ID', 'ID_LOOP']],
                        'EXPR_LOOP': [[',', 'EXPR', 'EXPR_LOOP']],
                        'IC_LOOP': [[',', 'ic', 'ic_LOOP']]}
        self.table = []
        self.read_table()

    def read_table(self):
        with open('Grammar/table.csv', newline='') as file:
            csv_file = list(csv.reader(file, delimiter=',', quotechar='"'))
            for i in range(1, len(csv_file)):
                self.table.append({})
                for j in range(1, len(csv_file[i])):
                    self.table[i - 1][csv_file[0][j]] = csv_file[i][j].split()

    def parse(self):
        token = ''
        stack = [[0, None]]
        while True:
            # TODO get token
            top = stack[len(stack) - 1]
            if top[1] is not None:
                temp = top[1]
            else:
                temp = token
            act = self.table[top[0]][temp]
            if act[0] == 'ERROR':
                # TODO handle error
                print('error')
            elif act[0] == 'SHIFT':
                top[1] = temp
                stack.append([int(act[1][1:]), None])
                # TODO get token
            elif act[0] == 'PUSH_GOTO':
                top[1] = temp
                stack.append([int(act[1][1:]), None])


if __name__ == '__main__':
    parser = Parser()
    parser.parse()
