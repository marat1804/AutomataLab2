import sys
from Parser.parser import MyParser
from SyntaxTree.SyntaxTree import SyntaxTreeNode
from Errors.errors import \
    Error_handler, \
    InterpreterRedeclarationError,\
    InterpreterApplicationCall,\
    InterpreterConverseError,\
    InterpreterIndexError,\
    InterpreterWrongParameters,\
    InterpreterNameError,\
    InterpreterValueError,\
    InterpreterTypeError,\
    InterpreterBoolIndexError
from Robot.robot import \
    Robot, \
    Cell, \
    cells


class Variable:
    def __init__(self, var_type, var_value):
        self.type = var_type
        if var_value == 'true':
            self.value = True
        elif var_value == 'false':
            self.value = False
        else:
            self.value = var_value

    def __repr__(self):
        return f'{self.type} {self.value}'

    def __eq__(self, other):
        if isinstance(other, Variable):
            return (self.type == other.type and
                    self.value == other.value)
        return NotImplemented


class TypeConverser:
    def __init__(self):
        pass

    def converse(self, typeVar, var):
        if typeVar == var.type:
            return var
        elif typeVar == 'int':
            if var.type == 'bool':
                return self.bool_to_int(var)
        elif typeVar == 'bool':
            if var.type == 'int':
                return self.int_to_bool(var)
        elif typeVar.find(var.type) != -1:
            return Variable(typeVar, var.value)

    @staticmethod
    def int_to_bool(var):
        if var.value == 0:
            return Variable('bool', False)
        else:
            return Variable('bool', True)

    @staticmethod
    def bool_to_int(var):
        if var.value:
            return Variable('int', 1)
        else:
            return Variable('int', 0)


def make_copy(var):
    if var.type.find('v') != -1:
        result = []
        for j in var.value:
            result.append(Variable(var.type[1:], j.value))
        return Variable(var.type, result)
    elif var.type.find('m') != -1:
        result = [[] for _ in range(len(var.value))]
        for elem in range(len(var.value)):
            for j in var.value[elem]:
                result[elem].append(
                    Variable(var.type[1:], j.value)
                )
        return Variable(var.type, result)
    return var


class Interpreter:

    def __init__(self, parser=MyParser(), converser=TypeConverser()):
        self.parser = parser
        self.converser = converser
        self.map = None
        self.program = None
        self.symbol_table = [dict()]
        self.scope = 0
        self.tree = None
        self.functions = None
        self.robot = None
        self.exit_found = False
        self.error = Error_handler()
        self.error_types = {'UnexpectedError': 0,
                            'NoStartPoint': 1,
                            'RedeclarationError': 2,
                            'UndeclaredError': 3,
                            'IndexError': 4,
                            'FuncCallError': 5,
                            'ConverseError': 6,
                            'ValueError': 7,
                            'ApplicationCall': 8,
                            'WrongParameters': 9,
                            'TypeError': 10,
                            'BoolError': 11}

    def interpreter(self, robot=None, program=None):
        self.robot = robot
        self.program = program
        self.symbol_table = [dict()]
        self.tree, self.functions, _correct = self.parser.parse(self.program)
        if _correct:
            if 'main' not in self.functions.keys():
                print(self.error.up(self.error_types['NoStartPoint']))
                return
            self.interpreter_tree(self.tree)
            try:
                self.interpreter_node(self.functions['main'].children['body'])
                return True
            except RecursionError:
                sys.stderr.write(f'RecursionError: function calls itself too many times\n')
                sys.stderr.write("========= Program has finished with fatal error =========\n")
                return False
        else:
            sys.stderr.write(f'Can\'t interpretate incorrect input file\n')

    def interpreter_tree(self, tree):
        print("Program tree:\n")
        tree.print()
        print("\n")

    def interpreter_node(self, node):
        if node is None:
            return ''
        elif node.type == 'program':
            self.interpreter_node(node.children)
        elif node.type == 'stmt_list':
            for ch in node.children:
                self.interpreter_node(ch)

        # statements
        elif node.type == 'declaration':
            declaration_type = node.value.value
            declaration_child = node.children
            try:
                self.declare_variable(declaration_type, declaration_child)
            except InterpreterRedeclarationError:
                self.error.up(self.error_types['RedeclarationError'], node)
            except InterpreterValueError:
                self.error.up(self.error_types['ValueError'], node)
            except InterpreterIndexError:
                self.error.up(self.error_types['IndexError'], node)
            except InterpreterBoolIndexError:
                self.error.up(self.error_types['BoolError'], node)
            except InterpreterTypeError:
                self.error.up(self.error_types['TypeError'], node)
            except InterpreterNameError:
                self.error.up(self.error_types['UndeclaredError'], node)
        elif node.type == 'expr_list':
            L = []
            for ch in node.children:
                L.append(self.interpreter_node(ch))
            if len(L) == 2 and isinstance(L[0], list):
                L[0].append(L[1])
                del L[1]
                L = L[0]
            elif len(L) == 1:
                return L[0]
            return L
        elif node.type == 'expression':
            return self.interpreter_node(node.children)
        elif node.type == 'const':
            return self.const_val(node.value)
        elif node.type == 'comma':
            return node.value
        elif node.type == 'colon':
            return node.value
        elif node.type == 'decl_list':
            return self.transform_list(self.get_list(node))
            # return self.list_of_smth(self.get_list(node))
        elif node.type == 'variable':
            return self.get_value(node)
        elif node.type == 'assignment':
            var = node.value.value
            index = None
            if var not in self.symbol_table[self.scope].keys():
                self.error.up(self.error_types['UndeclaredError'], node)
            else:
                if node.value.type == 'indexing':
                    index = self.interpreter_node(node.value.children)
                try:
                    _type = self.symbol_table[self.scope][var].type
                    expression = self.interpreter_node(node.children)
                    self.assign(_type, var, expression, index)
                except InterpreterTypeError:
                    self.error.up(self.error_types['TypeError'], node)
                except InterpreterConverseError:
                    self.error.up(self.error_types['ConverseError'], node)
                except InterpreterValueError:
                    self.error.up(self.error_types['ValueError'], node)
                except InterpreterNameError:
                    self.error.up(self.error_types['UndeclaredError'], node)
                except InterpreterIndexError:
                    self.error.up(self.error_types['IndexError'], node)
                except InterpreterBoolIndexError:
                    self.error.up(self.error_types['BoolError'], node)

        elif node.type == 'bin_op':
            if node.value == '+':
                return self.bin_plus(node.children[0], node.children[1])
            elif node.value == '-':
                return self.bin_minus(node.children[0], node.children[1])
            elif node.value == '*':
                try:
                    return self.matrix_mul(node.children[0], node.children[1])
                except InterpreterConverseError:
                    raise InterpreterConverseError
                except InterpreterValueError:
                    raise InterpreterValueError
            elif node.value == '.*':
                return self.element_mul(node.children[0], node.children[1])
            elif node.value == 'and' or node.value == '&&':
                return self.bin_and(node.children[0], node.children[1])
            elif node.value == '<':
                return self.logic_less(node.children[0], node.children[1])
            elif node.value == '>':
                return self.logic_more(node.children[0], node.children[1])
        elif node.type == 'un_op':
            if node.value == "'":
                return self.matrix_transpose(node.children)
            elif node.value == 'sum':
                return self.element_sum(node.children)
            elif node.value == '!':
                return self.deny(node.children)
            elif node.value == '<<':
                return self.stl(node.children)
            elif node.value == '>>':
                return self.str(node.children)
        elif node.type == 'indexing':
            try:
                return self.indexing(node.value, node.children)
            except InterpreterNameError:
                raise InterpreterNameError
            except InterpreterIndexError:
                raise InterpreterIndexError
            except InterpreterValueError:
                raise InterpreterValueError
        elif node.type == 'index':
            if isinstance(node.children, list):
                ind = []
                for i in range(len(node.children)):
                    ind.append(self.interpreter_node(node.children[i]))
                return ind
            else:
                return self.interpreter_node(node.children)
        elif node.type == 'if':
            try:
                self.op_if(node)
            except InterpreterConverseError:
                self.error.up(self.error_types['ConverseError'], node)
            except InterpreterTypeError:
                self.error.up(self.error_types['TypeError'], node)
            except InterpreterValueError:
                self.error.up(self.error_types['ValueError'], node)
            except InterpreterIndexError:
                self.error.up(self.error_types['IndexError'], node)
            except InterpreterBoolIndexError:
                self.error.up(self.error_types['BoolError'], node)
        elif node.type == 'for':
            try:
                self.op_for(node)
            except InterpreterConverseError:
                self.error.up(self.error_types['ConverseError'], node)
            except InterpreterTypeError:
                self.error.up(self.error_types['TypeError'], node)
            except InterpreterValueError:
                self.error.up(self.error_types['ValueError'], node)
            except InterpreterIndexError:
                self.error.up(self.error_types['IndexError'], node)
            except InterpreterBoolIndexError:
                self.error.up(self.error_types['BoolError'], node)
            except InterpreterNameError:
                self.error.up(self.error_types['UndeclaredError'], node)
        elif node.type == 'function_description':
            pass
        elif node.type == 'function_call':
            try:
                ret = node.children.get('return')
                if isinstance(ret, list):
                    val = self.function_call(node, 1, node.value)
                    if val is not None:
                        self.symbol_table[self.scope][node.children.get('return')[1]] = self.check_type(
                            node.children.get('return')[0].value, val)
                else:
                    self.function_call(node, 0)
            except InterpreterApplicationCall:
                self.error.up(self.error_types['ApplicationCall'], node)
            except InterpreterWrongParameters:
                self.error.up(self.error_types['WrongParameters'], node)
        elif node.type == 'func_list':
            items = []
            for item in node.children:
                i = self.interpreter_node(item)
                items.append(i)
            if len(items) == 2 and isinstance(items[0], list):
                items[0].append(items[1])
                del items[1]
                items = items[0]
            elif len(items) == 1:
                return items[0]
            return items
        elif node.type == 'func':
            a = ()
            if len(node.children) == 2:
                a = (node.children[1], node.children[0].value)
            elif len(node.children) == 3:
                a = (node.children[1], node.children[0].value, self.interpreter_node(node.children[2]))
            return a
        elif node.type == 'call_list':
            items = []
            for item in node.children:
                i = self.interpreter_node(item)
                items.append(i)
            if len(items) == 2 and isinstance(items[0], list):
                items[0].append(items[1])
                del items[1]
                items = items[0]
            elif len(items) == 1:
                return items[0]
            return items
        elif node.type == 'robot':
            if node.value == 'wall':
                return Variable('int', self.wall())
            elif node.value == 'exit':
                return Variable('bool', self.exit())
            elif node.value == 'right':
                return self.right()
            elif node.value == 'left':
                return self.left()
            elif node.value == 'move':
                exp = self.interpreter_node(node.children)
                return Variable('bool', self.move(exp.value))
        else:
            print('ELSE', node)
        return ''

    def get_value(self, node):
        if node.value in self.symbol_table[self.scope].keys():
            return self.symbol_table[self.scope][node.value]
        elif node.value in self.functions.keys():
            return self.function_call(self.functions[node.value], 1, node.value)
        else:
            raise InterpreterNameError

    def declare_variable(self, type, child):
        if child[1].type == 'decl_list':
            variable = child[0].value
            expression = self.list_of_smth(self.interpreter_node(child[1]))
            self.declare(type, variable, expression)
        elif child[1].type == 'expression':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            self.declare(type, variable, expression)

    def declare(self, type, var, expression):
        expression = self.check_type(type, expression)
        if var in self.symbol_table[self.scope].keys():
            raise InterpreterRedeclarationError
        else:
            self.symbol_table[self.scope][var] = expression

    def get_list(self, node):
        if node.type == 'end_of_list':
            return '#'
        if isinstance(node.children, SyntaxTreeNode):
            expression = self.interpreter_node(node.children)
            if isinstance(expression, list):
                if len(expression) == 1:
                    return expression[0]
            return expression
        elif isinstance(node.children, list):
            expr = []
            for i in node.children:
                a = self.get_list(i)
                expr.append(a)
            if expr[len(expr) - 1] == '#':
                new_expr = []
                a = expr[0]
                while not isinstance(a, Variable) and len(a) == 2:
                    new_expr.append(a[1])
                    a = a[0]
                new_expr.append(a[0])
                new_expr.reverse()
                new_expr.append('#')
                return new_expr
            return expr

    def check_type(self, type, exp):
        var = ['bool', 'int', 'cbool', 'cint']
        if type.find('m') != -1 and exp.type.find('m') != -1:
            return self.check_matrix(type, exp)
        elif type.find('v') != -1 and exp.type.find('v') != -1:
            return self.check_vector(type, exp)
        elif type in var and exp.type in var:
            return self.check_var(type, exp)
        else:
            raise InterpreterTypeError

    def check_matrix(self, type, expr):
        exp = expr.value
        l = len(exp[0])
        t = type[1:]
        for i in range(len(exp)):
            if len(exp[i]) != l:
                raise InterpreterValueError
        for i in range(len(exp)):
            for j in range(l):
                exp[i][j] = self.converser.converse(t, exp[i][j])
        return Variable(type, exp)

    def check_vector(self, type, expr):
        t = type[1:]
        exp = expr.value
        for i in range(len(exp)):
            exp[i] = self.converser.converse(t, exp[i])
        return Variable(type, exp)

    def check_var(self, type, exp):
        exp = self.converser.converse(type, exp)
        return exp

    def const_val(self, value):
        if value == 'true' or value == 'false':
            return Variable('bool', value)
        else:
            return Variable('int', value)

    def list_of_smth(self, value):
        if isinstance(value, Variable):
            return value
        elif isinstance(value[0], list):
            if type(value[0][0].value) is int:
                return Variable('mint', value)
            else:
                return Variable('mbool', value)
        else:
            if type(value[0].value) is int:
                return Variable('vint', value)
            else:
                return Variable('vbool', value)

    def assign(self, type, var, expression, index=None):
        if type[0] == 'c':
            raise InterpreterTypeError
        if type == expression.type:
            self.symbol_table[self.scope][var] = expression
        elif type[0] == expression.type[0]:
            if type[0] == 'v':
                self.symbol_table[self.scope][var] = self.check_vector(type, expression)
            elif type[0] == 'm':
                self.symbol_table[self.scope][var] = self.check_matrix(type, expression)
        elif (type == 'bool' or type == 'int') and (expression.type == 'bool' or expression.type == 'int'):
            self.symbol_table[self.scope][var] = self.check_var(type, expression)
        elif index is not None:
            if type.find('m') != -1:
                self.symbol_table[self.scope][var].value[index[0].value][index[1].value] = self.check_type(type[1:],
                                                                                                           expression)
            elif type.find('v') != -1:
                self.symbol_table[self.scope][var].value[index.value] = self.check_type(type[1:], expression)
        else:
            raise InterpreterConverseError

    def bin_plus(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('int', expr1.value + expr2.value)

    def bin_minus(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('int', expr1.value - expr2.value)

    def matrix_mul(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        if expr1.type.find('m') == -1:
            raise InterpreterConverseError
        else:
            expr1 = self.check_matrix('mint', expr1)
        if expr2.type.find('m') == -1:
            expr2 = self.converse_to_matrix(expr2, len(expr1.value))
        else:
            expr2 = self.check_matrix('mint', self.interpreter_node(var2))
        if len(expr1.value[0]) != len(expr2.value):
            raise InterpreterValueError
        res = []
        l = len(expr1.value)
        for i in range(l):
            res.append([Variable('int', 0) for j in range(l)])
        for i in range(l):
            for j in range(l):
                for k in range(len(expr2.value)):
                    res[i][j].value += expr1.value[i][k].value * expr2.value[k][j].value
        return Variable('mint', res)

    def converse_to_matrix(self, value, size):
        m = []
        for i in range(size):
            m.append([Variable('int', 0) for j in range(size)])
        val = self.converser.converse('int', value)
        for i in range(size):
            m[i][i] = val
        return Variable('mint', m)

    def element_mul(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        if expr1.type.find('v') != -1:
            expr1 = self.check_vector('vint', expr1)
        elif expr1.type.find('m') != -1:
            expr1 = self.check_matrix('mint', expr1)
        else:
            raise InterpreterValueError
        if expr2.type.find('v') != -1:
            expr2 = self.check_vector('vint', expr2)
        elif expr2.type.find('m') != -1:
            expr2 = self.check_matrix('mint', expr2)
        else:
            if expr1.type.find('v') != -1:
                expr2 = self.converse_to_vector(expr2, len(expr1.value))
            elif expr2.type.find('m') != -1:
                expr2 = self.converse_to_matrix(expr2, len(expr1.value))
        if len(expr1.value) != len(expr2.value):
            raise InterpreterValueError
        res = []
        l = len(expr1.value)
        if expr1.type.find('m') != -1:
            for i in range(l):
                res.append([Variable('int', 0) for j in range(l)])
            for i in range(l):
                for j in range(l):
                    res[i][j].value = expr1.value[i][j].value * expr2.value[i][j].value
            return Variable('mint', res)
        elif expr1.type.find('v') != -1:
            for i in range(l):
                res.append(Variable('int', 0))
            for i in range(l):
                res[i].value = expr1.value[i].value * expr2.value[i].value
            return Variable('vint', res)

    def converse_to_vector(self, value, size):
        m = []
        for i in range(size):
            m.append(Variable('int', 0))
        val = self.converser.converse('int', value)
        for i in range(size):
            m[i] = val
        return m

    def matrix_transpose(self, var):
        expr = self.interpreter_node(var)
        if expr.type.find('m') == -1:
            return InterpreterValueError
        else:
            res = []
            l = len(expr.value)
            for i in range(l):
                res.append([Variable('int', 0) for j in range(l)])
            for i in range(l):
                for j in range(l):
                    res[j][i] = expr.value[i][j]
            return Variable(expr.type, res)

    def element_sum(self, var):
        expr = self.interpreter_node(var)
        if expr.type.find('v') == -1 and expr.type.find('m') == -1:
            return InterpreterValueError
        sum = 0
        if expr.type.find('v') != -1:
            for i in range(len(expr.value)):
                sum += expr.value[i].value
        elif expr.type.find('m') != -1:
            for i in range(len(expr.value)):
                for j in range(len(expr.value)):
                    sum += expr.value[i][j].value
        return Variable('int', sum)

    def deny(self, var):
        expr = self.converser.converse('bool', self.interpreter_node(var))
        expr.value = not expr.value
        return expr

    def bin_and(self, var1, var2):
        expr1 = self.converser.converse('bool', self.interpreter_node(var1))
        expr2 = self.converser.converse('bool', self.interpreter_node(var2))
        return Variable('bool', expr1.value and expr2.value)

    def logic_less(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('bool', expr1.value < expr2.value)

    def logic_more(self, var1, var2):
        expr1 = self.converser.converse('int', self.interpreter_node(var1))
        expr2 = self.converser.converse('int', self.interpreter_node(var2))
        return Variable('bool', expr1.value > expr2.value)

    def stl(self, var):
        expr = self.converser.converse('int', self.interpreter_node(var))
        a = []
        value = expr.value
        while value > 0:
            a.append(value % 2)
            value = value // 2
        a.reverse()
        digit = a[0]
        for i in range(len(a) - 1):
            a[i] = a[i + 1]
        a[len(a) - 1] = digit
        b = 0
        a.reverse()
        for i in range(len(a)):
            b += a[i] * 2 ** i
        return Variable('int', b)

    def str(self, var):
        expr = self.converser.converse('int', self.interpreter_node(var))
        a = []
        value = expr.value
        while value > 0:
            a.append(value % 2)
            value = value // 2
        digit = a[0]
        for i in range(len(a) - 1):
            a[i] = a[i + 1]
        a[len(a) - 1] = digit
        b = 0
        for i in range(len(a)):
            b += a[i] * 2 ** i
        return Variable('int', b)

    def indexing(self, var, children):
        if var not in self.symbol_table[self.scope].keys():
            raise InterpreterNameError
        type = self.symbol_table[self.scope][var].type
        index = self.interpreter_node(children)
        # print('indexing', type, index)
        if isinstance(index, list):
            if len(index) == 3:
                index = self.list_of_smth(index)
            elif isinstance(index[0], list):
                index[0] = self.list_of_smth(index[0])
            elif isinstance(index[1], list):
                index[1] = self.list_of_smth(index[1])
        if not isinstance(index, list) and index.type.find('m') == -1 and index.type.find('v') == -1:
            return self.symbol_table[self.scope][var].value[index.value]
        elif isinstance(index, Variable) and index.type.find('m') != -1 and type.find('m') != -1:
            m = len(self.symbol_table[self.scope][var].value)
            n = len(self.symbol_table[self.scope][var].value[0])
            value = index.value
            check, m_, n_ = self.check_bool_matrix(index, m, n)
            if not check:
                raise InterpreterBoolIndexError
            res = [[] for j in range(m_)]
            for i in range(m):
                for j in range(n):
                    if value[i][j].value:
                        res[i].append(self.symbol_table[self.scope][var].value[i][j])
            return Variable(type, res)
        elif isinstance(index, Variable) and index.type.find('v') != -1 and type.find('v') != -1 or isinstance(index,
                                                                                                               list) and type.find(
            'v') != -1 \
                and index[0].type == index[1].type == 'bool':
            m = len(self.symbol_table[self.scope][var].value)
            if not isinstance(index, Variable):
                index = Variable('vbool', index)
            value = index.value
            check = self.check_bool_vector(index, m)
            if not check:
                raise InterpreterBoolIndexError
            res = []
            for i in range(m):
                if value[i].value:
                    res.append(self.symbol_table[self.scope][var].value[i])
            return Variable(type, res)
        else:
            if isinstance(index[0], Variable) and isinstance(index[1], Variable):
                if index[0].type == index[1].type:
                    try:
                        return self.symbol_table[self.scope][var].value[index[0].value][index[1].value]
                    except IndexError:
                        raise InterpreterIndexError
            elif type.find('m') != -1:  # indexing for matrix
                if isinstance(index[0], Variable) and (index[1] == ':' or index[1] == ','):
                    if index[0].type.find('v') == -1 and index[0].type.find('m') == -1:
                        res = []
                        index[0] = self.check_var('int', index[0])
                        m = self.symbol_table[self.scope][var].value
                        for i in range(len(m)):
                            res.append(m[i][index[0].value])
                        type_ = 'v' + type.split('m')[1]
                        return Variable(type_, res)
                    elif index[0].type.find('vint') != -1:
                        index[0] = self.check_vector('vint', index[0])
                        value = index[0].value
                        res = [[] for i in range(len(value))]
                        m = self.symbol_table[self.scope][var].value
                        for j in range(len(value)):
                            for i in range(len(m)):
                                res[j].append(m[i][value[j].value])
                        return Variable(type, res)
                    elif index[0].type.find('vbool') != -1:
                        m = self.symbol_table[self.scope][var].value
                        if len(index[0].value) != len(m):
                            raise InterpreterValueError
                        index[0] = self.check_vector('vbool', index[0])
                        value = index[0].value
                        res = []
                        k = -1
                        for j in range(len(value)):
                            if not value[j].value:
                                continue
                            res.append([])
                            k += 1
                            for i in range(len(m)):
                                res[k].append(m[i][j])
                        return Variable(type, res)
                elif isinstance(index[1], Variable) and (index[0] == ':' or index[0] == ','):
                    if index[1].type.find('v') == -1:
                        res = []
                        index[1] = self.check_var('int', index[1])
                        m = self.symbol_table[self.scope][var].value
                        for i in range(len(m[0])):
                            res.append(m[index[1].value][i])
                        type_ = 'v' + type.split('m')[1]
                        return Variable(type_, res)
                    elif index[1].type.find('vint') != -1:
                        index[1] = self.check_vector('vint', index[1])
                        value = index[1].value
                        res = [[] for i in range(len(value))]
                        m = self.symbol_table[self.scope][var].value
                        for j in range(len(value)):
                            for i in range(len(m)):
                                res[j].append(m[value[j].value][i])
                        return Variable(type, res)
                    elif index[1].type.find('vbool') != -1:
                        m = self.symbol_table[self.scope][var].value
                        if len(index[1].value) != len(m):
                            raise InterpreterValueError
                        index[1] = self.check_vector('vbool', index[1])
                        value = index[1].value
                        res = []
                        k = -1
                        for j in range(len(value)):
                            if not value[j].value:
                                continue
                            res.append([])
                            k += 1
                            for i in range(len(m)):
                                res[k].append(m[j][i])
                        return Variable(type, res)
                else:
                    raise InterpreterIndexError

    def check_bool_matrix(self, var, m, n):
        type = var.type
        value = var.value
        if type.find('m') == -1:
            return False
        if len(value) != m or len(value[0]) != n:
            return False
        counts = []
        etallon = 0
        for i in range(len(value)):
            k = 0
            for j in range(len(value[0])):
                if value[i][j].value:
                    k += 1
            counts.append(k)
            if etallon == 0:
                etallon = k
        if etallon > 1 and len(counts) == (counts.count(etallon) + counts.count(0)):
            return True, counts.count(etallon), etallon
        return False, 0, 0

    def check_bool_vector(self, var, n):
        type = var.type
        value = var.value
        if type.find('v') == -1:
            return False
        if len(value) != n:
            return False
        k = 0
        for i in range(n):
            if value[i].value:
                k += 1
        if k > 1:
            return True
        else:
            return False

    def op_if(self, node):
        condition = self.interpreter_node(node.children['condition'])
        condition = self.converser.converse('bool', condition).value
        if condition:
            self.interpreter_node(node.children['body'])

    def op_for(self, node):
        variable = node.children['var'].value
        flag = False
        if variable not in self.symbol_table[self.scope].keys():
            flag = True
        from_ = self.interpreter_node(node.children['from'])
        to_ = self.interpreter_node(node.children['to'])
        try:
            self.symbol_table[self.scope][variable] = Variable('int', from_.value)
            while self.symbol_table[self.scope][variable].value <= to_.value:
                self.interpreter_node(node.children['body'])
                self.symbol_table[self.scope][variable].value += 1
            if flag:
                del self.symbol_table[self.scope][variable]
            '''
            for i in range(from_.value, to_.value):
                self.symbol_table[self.scope][variable] = Variable('int', i)
                self.interpreter_node(node.children['body'])
            if flag:
                del self.symbol_table[self.scope][variable]
            '''
        except InterpreterConverseError:
            raise InterpreterConverseError
        except InterpreterTypeError:
            raise InterpreterTypeError
        except InterpreterValueError:
            raise InterpreterValueError
        except InterpreterIndexError:
            raise InterpreterIndexError
        except InterpreterBoolIndexError:
            raise InterpreterBoolIndexError
        except InterpreterNameError:
            raise InterpreterNameError

    def function_call(self, node, index, name=None):
        """Looking if we returning to assign or just function call"""
        func_name = ''
        if index == 0:
            func_name = node.value
        elif index == 1:
            func_name = name
        if func_name not in self.functions.keys() and func_name not in self.symbol_table[self.scope].keys():
            self.error.up(self.error_types['FuncCallError'], node)
            return
        if func_name == 'main':
            raise InterpreterApplicationCall
        """Adding for recursion checking"""
        if '#'+func_name not in self.symbol_table[0].keys():
            self.symbol_table[0]['#' + func_name] = 1
        else:
            self.symbol_table[0]['#' + func_name] += 1
        if self.symbol_table[0]['#' + func_name] > 1000:
            self.symbol_table.pop()
            self.scope -= 1
            raise RecursionError from None
        param = node.children.get('call')
        returning = node.children.get('return')
        func_param = None
        func_ret = None
        # print("I'm in " + func_name)
        """Getting values that function got"""
        try:
            if isinstance(param, SyntaxTreeNode):
                if func_param is None:
                    func_param = []
                for item in param.children:
                    p = self.interpreter_node(item)
                    if isinstance(p, list):
                        for key in p:
                            key = make_copy(key)
                            func_param.append(key)
                    else:
                        p = make_copy(p)
                        func_param.append(p)
        except InterpreterNameError:
            self.error.up(self.error_types['UndeclaredError'], node)
            return
        # print('TO FUNC - ', func_param)
        """Forming return list"""
        if index == 0:
            if isinstance(returning, SyntaxTreeNode):
                if func_ret is None:
                    func_ret = []
                a = returning.children
                if a is not None:
                    while isinstance(a, list):
                        func_ret.append(a[1].value)
                        a = a[0].children
                    func_ret.append(a.value)
                    func_ret.reverse()
                else:
                    func_ret.append(returning.value)
        # print('from FUNC - ', func_ret)
        self.scope += 1
        self.symbol_table.append(dict())
        func_subtree = self.functions[func_name] or self.symbol_table[self.scope - 1][func_name]
        get = func_subtree.children.get('param')
        get_list = None
        common_list = {}
        """Forming what function MUST get"""
        if get is not None:
            if get_list is None:
                get_list = {}
            for item in get.children:
                p = self.interpreter_node(item)
                if isinstance(p, tuple):
                    if len(p) == 2:
                        get_list[p[0]] = p[1]
                    elif len(p) == 3:
                        get_list[p[0]] = p[1]
                        if isinstance(p[2], list):
                            common_list[p[0]] = self.list_of_smth(p[2])
                        else:
                            common_list[p[0]] = p[2]
                else:
                    for i in p:
                        if len(i) == 2:
                            get_list[i[0]] = i[1]
                        elif len(i) == 3:
                            get_list[i[0]] = i[1]
                            common_list[i[0]] = i[2]
        # print('GOT - ', get_list, common_list)
        """Checking what we got and what we must get"""
        try:
            if get_list is not None and func_param is not None:
                if len(get_list.keys()) != len(func_param) and len(get_list.keys()) != 0:
                    if len(get_list.keys()) > (len(func_param) + len(common_list.keys())):
                        # print(len(get_list.keys()), len(func_param)+len(common_list.keys()))
                        self.error.up(self.error_types['WrongParameters'], node)
                        return
                    else:
                        for i in common_list.values():
                            func_param.append(i)
                i = 0
                for k, v in get_list.items():
                    a = self.check_type(v, func_param[i])
                    i += 1
                    self.symbol_table[self.scope][k] = a
            elif func_param is None:
                func_param = []
                for i in common_list.values():
                    func_param.append(i)
                i = 0
                if get_list is not None:
                    if len(func_param) == 0:
                        raise InterpreterWrongParameters
                    for k, v in get_list.items():
                        a = self.check_type(v, func_param[i])
                        i += 1
                        self.symbol_table[self.scope][k] = a
        except InterpreterTypeError:
            self.error.up(self.error_types['TypeError'], node)
            return
        ret = func_subtree.children.get('return')
        return_dict = {}
        return_list = []
        """Adding values for symbol table"""
        if isinstance(ret, SyntaxTreeNode):
            r = ret.children
            while len(r) == 3:
                return_dict[r[2]] = r[1].value
                return_list.append(r[2])
                r = r[0].children
            if len(r) == 2:
                return_dict[r[1]] = r[0].value
                return_list.append(r[1])
            return_list.reverse()
            for k, v in return_dict.items():
                var = Variable('int', 0)
                if v.find('m') != -1:
                    var = Variable('mint', [[var, var], [var, var]])
                elif v.find('v') != -1:
                    var = Variable('vint', [var, var])
                a = self.check_type(v, var)
                self.symbol_table[self.scope][k] = a
        if func_ret is not None and len(return_list) != len(func_ret):
            self.error.up(self.error_types['WrongParameters'], node)
            return
        self.interpreter_node(func_subtree.children['body'])
        self.scope -= 1
        """Returning"""
        try:
            if index == 0:
                if func_ret is not None:
                    for i in range(len(return_list)):
                        a = self.check_type(self.symbol_table[self.scope][func_ret[i]].type,
                                            self.symbol_table[self.scope + 1][return_list[i]])
                        self.symbol_table[self.scope][func_ret[i]] = a
                self.symbol_table[0]['#' + func_name] -= 1
                self.symbol_table.pop()
            else:
                ret__ = self.symbol_table[self.scope + 1][return_list[0]]
                self.symbol_table[0]['#' + func_name] -= 1
                self.symbol_table.pop()
                return ret__
        except InterpreterTypeError:
            self.symbol_table[0]['#' + func_name] -= 1
            self.symbol_table.pop()
            self.error.up(self.error_types['TypeError'], node)

    def transform_list(self, L):
        new_L = []
        k = 0
        queue = [L]
        while len(queue) != 0:
            a = queue[0]
            if isinstance(a, list):
                for i in a:
                    queue.append(i)
                del queue[0]
            else:
                new_L.append([])
                while queue[0] != '#':
                    new_L[k].append(queue[0])
                    del queue[0]
                del queue[0]
                k += 1
        if len(new_L) > 2:
            a = len(new_L)
            new_L[a - 1], new_L[a - 2] = new_L[a - 2], new_L[a - 1]
            new_L.reverse()
        elif len(new_L) == 1:
            new_L = new_L[0]
            if isinstance(new_L, list) and len(new_L) == 1:
                new_L = new_L[0]
        return new_L

    def wall(self):
        return self.robot.wall()

    def exit(self):
        result = self.robot.exit()
        if result:
            self.exit_found = True
        return result

    def right(self):
        return self.robot.right()

    def left(self):
        return self.robot.left()

    def move(self, expression):
        return self.robot.move(expression)


def create_robot(descriptor):
    with open(descriptor) as file:
        text = file.read()
    text = text.split('\n')
    robot_info = text.pop(0).split(' ')
    map_size = text.pop(0).split(' ')
    x = int(robot_info[0])
    y = int(robot_info[1])
    turn = int(robot_info[2])
    tmpMap = [0] * int(map_size[0])

    for cell in range(int(map_size[0])):
        tmpMap[cell] = [0] * int(map_size[1])
    for cell in range(int(map_size[0])):
        for j in range(int(map_size[1])):
            tmpMap[cell][j] = Cell("EMPTY")
    pos = 0
    while len(text) > 0:
        line = list(text.pop(0))
        line = [Cell(cells[i]) for i in line]
        tmpMap[pos] = line
        pos += 1
    return Robot(x=x, y=y, turn=turn, map=map)


if __name__ == '__main__':
    prog_names = ['Tests/bubblesort.txt',
                  'Tests/fib.txt',
                  'Tests/cycle_and_conditions.txt',
                  'Tests/funcs.txt',
                  'Tests/index.txt',
                  'Tests/math.txt',
                  'Tests/nomain.txt',
                  'Tests/badrecursion.txt',
                  'Tests/syntax_errors.txt',
                  'Tests/some_errors.txt']
    maps = ['Tests/Map/simple_map',
            'Tests/Map/medium_map',
            'Tests/Map/noexit',
            'Tests/Map/middle',
            'Tests/Map/island',
            'Tests/Map/two_island']
    algo = ['Tests/righthand.txt',
            'Tests/modified.txt']
    print("What do you want to do? \n "
          "0 - Run the algorithm \n "
          "1 - Start the robot \n")
    n = int(input())
    if n == 0:
        i = Interpreter()
        print("What do you want to run ? \n "
              "0 - Bubblesort \n "
              "1 - Fibonacci number \n "
              "2 - Cycles \n "
              "3 - Functions examples \n "
              "4 - Indexing \n "
              "5 - Math and logic \n"
              "6 - No main error \n "
              "7 - Bad recursion \n "
              "8 - Syntax errors \n"
              "9 - Errors")
        number = int(input())
        if number not in range(10):
            print("Bad number!")
        else:
            prog = open(prog_names[number], 'r').read()
            res = i.interpreter(program=prog)
            if res:
                print('Symbol table:')
                for symbol_table in i.symbol_table:
                    for k, v in symbol_table.items():
                        print(k, v)
    elif n == 1:
        print("Please choose the map: \n "
              "0 - Simple map \n "
              "1 - Medium map \n "
              "2 - No exit map \n "
              "3 - Start in the middle \n"
              " 4 - Island \n "
              "5 - Two islands \n")
        number = int(input())
        print("Please choose the algo: \n 0 - Right hand \n 1 - Modified \n")
        number_2 = int(input())
        if number not in range(6) or number_2 not in range(2):
            print("Bad number!")
        else:
            robot = create_robot(maps[number])
            i = Interpreter()
            prog = open(algo[number_2], 'r').read()
            res = i.interpreter(program=prog, robot=robot)
            if res:
                for symbol_table in i.symbol_table:
                    for k, v in symbol_table.items():
                        print(k, v)
            if i.exit_found:
                print("\n\n========== EXIT HAS BEEN FOUND ==========\n\n")
            else:
                print("\n\n========== EXIT HAS NOT BEEN FOUND ==========\n\n")
            print('\nRobot:', i.robot)
            print('\nMap: ')
            i.robot.show()
