import sys
from parser import SyntaxTreeNode


class Error_handler:
    def __init__(self):
        self.type = None
        self.node = None
        self.types = ['UnexpectedError',
                      'NoStartPoint',
                      'RedeclarationError',
                      'UndeclaredError',
                      'IndexError',
                      'FuncCallError',
                      'ConverseError',
                      'ValueError',
                      'ApplicationError',
                      'Recursion']

    def up(self, err_type, node=None):
        self.type = err_type
        self.node = node
        sys.stderr.write(f'Error {self.types[int(err_type)]}: ')
        if self.type == 0:
            sys.stderr.write(f' incorrect syntax at '
                             f'{self.node.child[0].lineno} line \n')
            return
        elif self.type == 1:
            sys.stderr.write(f'No "main" function detected\n')
            return


