import csv

from CodeGen import CodeGen
from Scanner import Scanner


class Parser:
    def __init__(self):
        self.grammar = {'VAR_DCL': [['id', ':', 'SIMPLE_VAR'],
                                    ['id', ':', 'ARRAY_VAR']],
                        'FUNC_DEF': [['function', 'id', '(', ')', ':', 'TYPE', 'BLOCK'],
                                     ['function', 'id', '(', 'VAR_DCL', 'ARG', ')', ':', 'TYPE', 'BLOCK']],
                        'PROC_DEF': [['procedure', 'id', '(', ')', 'BLOCK'],
                                     ['procedure', 'id', '(', 'VAR_DCL', 'ARG', ')', 'BLOCK']],
                        'SIMPLE_VAR': [['TYPE'],
                                       ['TYPE', 'ASSIGNMENT']],
                        'ARRAY_VAR': [['array', 'ARRAY_DIM', 'of', 'TYPE']],
                        'ASSIGNMENT': [[':=', 'EXPR']],
                        'TYPE': [['integer'],
                                 ['real'],
                                 ['character'],
                                 ['string'],
                                 ['boolean']],
                        'BLOCK': [['begin', 'STMT_LOOP', 'end']],
                        'STMT': [['return', 'EXPR'],
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
                                     ['rc'],
                                     ['cc'],
                                     ['sc'],
                                     ['bc'],
                                     ['lc']],
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
                              ['id'],
                              ['CONSTANT'],
                              ['~', 'id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                              ['~', 'id', '(', ')'],
                              ['~', 'id', '(', 'EXPR', 'EXPR_LOOP', ')'],
                              ['~', 'CONSTANT'],
                              ['~', 'id'],
                              ['-', 'id', '[', 'EXPR', 'EXPR_LOOP', ']'],
                              ['-', 'id', '(', ')'],
                              ['-', 'id', '(', 'EXPR', 'EXPR_LOOP', ')'],
                              ['-', 'CONSTANT'],
                              ['-','id']],
                        'STMT_ID': [['[', 'EXPR', 'EXPR_LOOP', ']', 'ASSIGNMENT'],
                                    [':', 'SIMPLE_VAR'],
                                    [':', 'ARRAY_VAR'],
                                    ['(', ')'],
                                    ['(', 'EXPR', 'EXPR_LOOP', ')'],
                                    ['ASSIGNMENT']],
                        'ARG': [[';', 'VAR_DCL', 'ARG']],
                        'STMT_LOOP': [['STMT', ';', 'STMT_LOOP']],
                        'ID_LOOP': [[',', 'ID', 'ID_LOOP']],
                        'EXPR_LOOP': [[',', 'EXPR', 'EXPR_LOOP']],
                        'IC_LOOP': [[',', 'ic', 'IC_LOOP']],
                        'GLOB_VAR_DCL': [['id', ':', 'SIMPLE_VAR'],
                                         ['id', ':', 'ARRAY_VAR']]}
        self.table = []
        self.read_table()
        self.scanner = Scanner()
        self.code_gen = CodeGen(self.scanner)

    def read_table(self):
        with open('Grammar/table.csv', newline='') as file:
            csv_file = list(csv.reader(file, delimiter=',', quotechar='"'))
            for i in range(1, len(csv_file)):
                self.table.append({})
                for j in range(1, len(csv_file[i])):
                    self.table[i - 1][csv_file[0][j]] = csv_file[i][j].split()

    def parse(self):
        stack = [[0, None]]
        token = self.scanner.scan()
        while True:
            top = stack[len(stack) - 1]
            if top[1] is not None:
                temp = top[1]
            else:
                temp = token

            act = self.table[top[0]][temp]
            # print(stack)
            # print(act)
            if act[0] == 'ERROR':
                raise SyntaxError
            elif act[0] == 'SHIFT':
                token = self.scanner.scan()
                self.code_gen.CG(act[2], temp)
                top[1] = temp
                stack.append([int(act[1][1:]), None])
            elif act[0] == 'PUSH_GOTO':
                self.code_gen.CG(act[2], temp)
                top[1] = temp
                stack.append([int(act[1][1:]), None])
            elif act[0] == 'GOTO':
                self.code_gen.CG(act[2], temp)
                stack.append([int(act[1][1:]), None])
            elif act[0] == 'REDUCE':
                stack = stack[:-1]
                rels = list(self.grammar[act[1]])
                found = -1
                for r in rels:
                    set = True
                    l = len(stack)-1
                    for i in range(len(r)-1, -1, -1):
                        if stack[l][1] != r[i]:
                            set = False
                            break
                        l -= 1
                    if set:
                        if len(r) > found:
                            found = len(r)
                while found > 0:
                    stack = stack[:-1]
                    found -= 1
                stack[-1][1] = act[1]
            elif act[0] == 'ACCEPT':
                self.code_gen.write()
                print('yes chaghal')
                break


if __name__ == '__main__':
    parser = Parser()
    parser.parse()
