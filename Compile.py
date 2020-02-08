from Parser import Parser
import sys
import os

if __name__ == '__main__':
    Parser('final-st/27/27-1.ppp')  .parse()
    os.system('clang Out/main.ll')
