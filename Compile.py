from Parser import Parser
import sys
import os

if __name__ == '__main__':
    Parser('final-st/4/4.ppp')  .parse()
    os.system('clang Out/main.ll')
