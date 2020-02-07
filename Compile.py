from Parser import Parser
import sys
import os

if __name__ == '__main__':
    Parser('demofile.txt').parse()
    os.system('clang Out/main.ll')
