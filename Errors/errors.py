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
            "3": f'Variable for assignment at line '
                 f'{self.node.value.lineno} is used before declaration\n',
            "assignment": f'Variable for function "{self.node.value}" at line '
                          f'{self.node.lineno} is used before declaration\n',
            "function_call": f'Variable for function "{self.node.value}" at line '
                             f'{self.node.lineno} is used before declaration\n',
            "for": f'Variable for cycle at line '
                   f'{self.node.lineno} is used before declaration\n',
            "declaration": f'Variable for declaration at line '
                           f'{self.node.lineno} is used before declaration\n',
            "4": f'List index is out of range at line '
                 f'{self.node.value.lineno}\n',
            "5": f'Unknown function call "{self.node.value}" at line '
                 f'{self.node.lineno} \n',
            "6_assignment": f'Wrong type variable "{self.node.value.value}" at line '
                            f'{self.node.value.lineno} \n',
            "7_declaration": f'Bad expression for variable "{node.children[0].value}" at line '
                          f'{self.node.lineno} \n',
            "7_assignment": f'Bad value for variable "{self.node.value.value}" at line '
                          f'{self.node.value.lineno} \n',
            "8": f'Tried to call main function at line'
                      f' {self.node.lineno} \n',
            "9": f'Bad parameters for function "{self.node.value}" at line '
                      f'{self.node.lineno} \n',
            "11": f'Incorrect bool matrix/vector at line '
                      f'{self.node.lineno}\n',
            "10_assignment": f'Bad values at assignment "{self.node.value.value}" at line '
                      f'{self.node.value.lineno}\n',
            "10_function_call": f'Type of variables in function "{self.node.value}" at line '
                      f'{self.node.lineno} do not match\n',
            "10_declaration": f'Bad values for declaration "{self.node.children[0].value}" at line '
                      f'{self.node.lineno}\n',

        }

        if self.type == 0:
            callError(errorList["0"])
            return
        elif self.type == 1:
            callError(errorList["1"])
            return
        elif self.type == 2:
            callError(errorList["2"])
        elif self.type == 3:
            if node.type == 'assignment':
                callError(errorList["assignment"])
            elif node.type == 'function_call':
                callError(errorList["function_call"])
            elif node.type == 'for':
                callError(errorList["for"])
            elif node.type == 'declaration':
                callError(errorList["declaration"])
        elif self.type == 4:
            callError(errorList["4"])
        elif self.type == 5:
            callError(errorList["5"])
        elif self.type == 6:
            if node.type == 'assignment':
                callError(errorList["6_assignment"])
        elif self.type == 7:
            if node.type == 'declaration':
                callError(errorList["7_declaration"])
            elif node.type == 'assignment':
                callError(errorList["7_assignment"])
        elif self.type == 8:
            callError(errorList["8"])
        elif self.type == 9:
            callError(errorList["9"])
        elif self.type == 10:
            if node.type == 'assignment':
                callError(errorList["10_assignment"])
            if node.type == 'function_call':
                callError(errorList["10_function_call"])
            if node.type == 'declaration':
                callError(errorList["10_declaration"])
        elif self.type == 11:
            callError(errorList["11"])


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
