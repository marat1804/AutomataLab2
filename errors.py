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
                      'WrongParameters',
                      'TypeError']

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
            sys.stderr.write(f'Variable "{node.children[0].value}" at line'
                             f'{self.node.lineno} is used before declaration\n')
        elif self.type == 3:
            if node.type == 'assignment':
                sys.stderr.write(f'Variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno} is used before declaration\n')
            elif node.type == 'function_call':
                sys.stderr.write(f'Variable for function "{self.node.value}" at line '
                                 f'{self.node.lineno} is used before declaration\n')
        elif self.type == 4:
            print('indexingERRORO in error.py')
        elif self.type == 5:
            sys.stderr.write(f'Unknown function call "{self.node.value}" at line '
                             f'{self.node.lineno} \n')
        elif self.type == 6:
            if node.type == 'assignment':
                sys.stderr.write(f'Wrong type variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno} \n')
        elif self.type == 7:
            if node.type == 'declaration':
                sys.stderr.write(f'Bad expression for variable "{node.children[0].value}" at line '
                                 f'{self.node.lineno} \n')
            elif node.type == 'assignment':
                sys.stderr.write(f'Bad value for variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno} \n')
        elif self.type == 8:
            sys.stderr.write(f'Tried to call main function at line'
                             f' {self.node.lineno} \n')
        elif self.type == 9:
            sys.stderr.write(f'Bad parameters for function "{self.node.value}" at line '
                             f'{self.node.lineno} \n')
        elif self.type == 10:
            if node.type == 'assignment':
                sys.stderr.write(f'Assignment to constant variable "{self.node.value.value}" at line '
                                 f'{self.node.value.lineno}\n')
            if node.type == 'function_call':
                sys.stderr.write(f'Type of variables in function "{self.node.value}" at line '
                                 f'{self.node.lineno} do not match\n')





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


class InterpreterWrongParameters(Exception):
    pass


class InterpreterApplicationCall(Exception):
    pass

class InterpreterTypeError(Exception):
    pass
