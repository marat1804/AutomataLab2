import sys
from SyntaxTree.SyntaxTree import SyntaxTreeNode


def callError(string):
    sys.stderr.write(string)


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
                      'TypeError',
                      'BoolError']

    def up(self, err_type, node=None):
        self.type = err_type
        self.node = node
        callError(f'Error {self.types[int(err_type)]}: ')

        errorList = {
            "1": f' incorrect syntax at {self.node.children[0].lineno} line \n',
            "2": f'Variable "{node.children[0].value}" at line '
                 f'{self.node.lineno} is already declared\n',
            "3": f'Variable "{node.children[0].value}" at line '
                f'{self.node.lineno} is already declared\n'

        }

        if self.type == 0:
            callError(errorList[0])
            return
        elif self.type == 1:
            callError(errorList[1])
            return
        elif self.type == 2:
            callError(errorList[2])
        elif self.type == 3:
            if node.type == 'assignment':
                callError(f'Variable for assignment at line '
                          f'{self.node.value.lineno} is used before declaration\n')
            elif node.type == 'function_call':
                callError(f'Variable for function "{self.node.value}" at line '
                          f'{self.node.lineno} is used before declaration\n')
            elif node.type == 'for':
                callError(f'Variable for cycle at line '
                          f'{self.node.lineno} is used before declaration\n')
            elif node.type == 'declaration':
                callError(f'Variable for declaration at line '
                          f'{self.node.lineno} is used before declaration\n')
        elif self.type == 4:
            callError(f'List index is out of range at line '
                      f'{self.node.value.lineno}\n')
        elif self.type == 5:
            callError(f'Unknown function call "{self.node.value}" at line '
                      f'{self.node.lineno} \n')
        elif self.type == 6:
            if node.type == 'assignment':
                callError(f'Wrong type variable "{self.node.value.value}" at line '
                          f'{self.node.value.lineno} \n')
        elif self.type == 7:
            if node.type == 'declaration':
                callError(f'Bad expression for variable "{node.children[0].value}" at line '
                          f'{self.node.lineno} \n')
            elif node.type == 'assignment':
                callError(f'Bad value for variable "{self.node.value.value}" at line '
                          f'{self.node.value.lineno} \n')
        elif self.type == 8:
            callError(f'Tried to call main function at line'
                      f' {self.node.lineno} \n')
        elif self.type == 9:
            callError(f'Bad parameters for function "{self.node.value}" at line '
                      f'{self.node.lineno} \n')
        elif self.type == 10:
            if node.type == 'assignment':
                callError(f'Bad values at assignment "{self.node.value.value}" at line '
                          f'{self.node.value.lineno}\n')
            if node.type == 'function_call':
                callError(f'Type of variables in function "{self.node.value}" at line '
                          f'{self.node.lineno} do not match\n')
            if node.type == 'declaration':
                callError(f'Bad values for declaration "{self.node.children[0].value}" at line '
                          f'{self.node.lineno}\n')
        elif self.type == 11:
            callError(f'Incorrect bool matrix/vector at line '
                      f'{self.node.lineno}\n')


class InterpreterBoolIndexError(Exception):
    pass


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
