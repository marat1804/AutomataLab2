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
                      'ApplicationCall',
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
        elif self.type == 2:
            print(node.type)
            sys.stderr.write(f'variable "{node.children[0].value}" at '
                             f'{self.node.lineno} line is used before declaration\n')
        elif self.type == 3:
            if node.type == 'assignment':
                sys.stderr.write(f'Variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno} is used before declaration\n')
            #else:
             #   sys.stderr.write(f'variable "{self.node.value}" at '
              #                   f'{self.node.lineno} line is used before declaration\n')

        elif self.type == 8:
            print(node)
            sys.stderr.write(f'Tried to call main function at line'
                             f' {self.node.lineno} \n')



class InterpreterNameError(Exception):
    pass


class InterpreterIndexError(Exception):
    pass


class InterpreterRedeclarationError(Exception):
    pass


class InterpreterConverseError(Exception):
    pass


class InterpreterValueError(Exception):
    pass


class InterpreterApplicationCall(Exception):
    pass


class InterpreterRecursion(Exception):
    pass
