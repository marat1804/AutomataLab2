import sys
from typing import List
from parser import MyParser, SyntaxTreeNode


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


class TypeConverser:
    def __init__(self):
        pass

    def converse(self, type, var):
        if type == var.type:
            return var
        elif type == 'bool':
            if var.type == 'int':
                return self.int_to_bool(var)
        elif type == 'int':
            if var.type == 'bool':
                return self.bool_to_int(var)

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


class Interpreter:

    def __init__(self, parser, converser):
        self.parser = parser
        self.converser = converser
        self.map = None
        self.program = None
        self.symbol_table = dict()
        self.tree = None
        self.functions = None
        # TODO add errors
        self.errors = {}

    def interpreter(self, map, program):
        self.map = map
        self.program = program
        self.symbol_table = dict()
        try:
            self.tree, self.functions = self.parser.parse(program)
        # TODO Exception
        except Exception:
            pass
        self.interpreter_tree(self.tree)
        self.interpreter_node(self.functions['application'])

    def interpreter_tree(self, tree):
        pass

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
            self.declare_variable(declaration_type, declaration_child)
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
            return self.list_of_smth(self.get_list(node))
        elif node.type == 'variable':
            return self.get_value(node)
        elif node.type == 'assigment':
            var = node.value.value
            index = None
            if node.value.type == 'indexing':
                index = self.interpreter_node(node.value.children)
            if var not in self.symbol_table.keys():
                print('ERROR_assign')  # TODO Error
            else:
                _type = self.symbol_table[var].type
                expression = self.interpreter_node(node.children)
                # TODO add Try
                self.assign(_type, var, expression, index)
        elif node.type == 'bin_op':
            if node.value == '+':
                return self.bin_plus(node.children[0], node.children[1])
            elif node.value == '-':
                return self.bin_minus(node.children[0], node.children[1])
            elif node.value == '*':
                return self.matrix_mul(node.children[0], node.children[1])
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
            return self.indexing(node.value, node.children)
        elif node.type == 'index':
            if isinstance(node.children, list):
                ind = []
                for i in range(len(node.children)):
                    ind.append(self.interpreter_node(node.children[i]))
                return ind
            else:

                return self.interpreter_node(node.children)
        else:
            print('ELSE', node)
        return ''

    def get_value(self, node):
        if node.value in self.symbol_table.keys():
            return self.symbol_table[node.value]
        else:
            print("ERRROR")

    def declare_variable(self, type, child):
        if child[1].type == 'decl_list':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            self.declare(type, variable, expression)
        elif child[1].type == 'expression':
            variable = child[0].value
            expression = self.interpreter_node(child[1])
            # TODO try
            self.declare(type, variable, expression)

    def declare(self, type, var, expression):
        expression = self.check_type(type, expression)
        if var in self.symbol_table.keys():
            pass  # TODO ERROR
        else:

            self.symbol_table[var] = expression

    def get_list(self, node):
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
            if len(expr) == 2:
                if len(expr[0]) != len(expr[1]):
                    expr[0].append(expr[1])
                    del expr[1]
                    expr = expr[0]
            return expr

    def check_type(self, type, exp):
        if type.find('m') != -1:
            e = self.check_matrix(type, exp)
        elif type.find('v') != -1:
            e = self.check_vector(type, exp)
        else:
            e = self.check_var(type, exp)
        return e

    def check_matrix(self, type, expr):
        exp = expr.value
        l = len(exp[0])
        t = type[1:]
        for i in range(len(exp)):
            if len(exp[i]) != l:
                print('ERROR')
                # TODO Error
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
            print("ERRROR")  # TODO ERROR
        if type == expression.type:
            self.symbol_table[var] = expression
        elif type[0] == expression.type[0]:
            if type[0] == 'v':
                self.symbol_table[var] = self.check_vector(type, expression)
            elif type[0] == 'm':
                self.symbol_table[var] = self.check_matrix(type, expression)
        elif (type == 'bool' or type == 'int') and (expression.type == 'bool' or expression.type == 'int'):
            self.symbol_table[var] = self.check_var(type, expression)
        elif index is not None:
            if type.find('m') != -1:
                self.symbol_table[var].value[index[0].value][index[1].value] = expression
            elif type.find('v') != -1:
                self.symbol_table[var].value[index.value] = expression
        else:
            print('ERRORR_asss')  # TODO EROOR

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
            print('not_matrix')  # TODO add EROOOR
        else:
            expr1 = self.check_matrix('mint', expr1)
        if expr2.type.find('m') == -1:
            expr2 = self.converse_to_matrix(expr2, len(expr1.value))
        else:
            expr2 = self.check_matrix('mint', self.interpreter_node(var2))
        if len(expr1.value) != len(expr2.value):
            print('error')  # TODO add Erroor
        res = []
        l = len(expr1.value)
        for i in range(l):
            res.append([Variable('int', 0) for j in range(l)])
        for i in range(l):
            for j in range(l):
                for k in range(l):
                    res[i][j].value += expr1.value[i][k].value * expr2.value[k][j].value
        return Variable('mint', res)

    def converse_to_matrix(self, value, size):
        m = []
        for i in range(size):
            m.append([Variable('int', 0) for j in range(size)])
        val = self.converser.converse('int', value)
        for i in range(size):
            m[i][i] = val
        return m

    def element_mul(self, var1, var2):
        expr1 = self.interpreter_node(var1)
        expr2 = self.interpreter_node(var2)
        if expr1.type.find('v') != -1:
            expr1 = self.check_vector('vint', expr1)
        elif expr1.type.find('m') != -1:
            expr1 = self.check_matrix('mint', expr1)
        else:
            print('error')
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
            print('Eroor')
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
            print('Error')
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
            print('Errror')
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
        if var not in self.symbol_table.keys():
            print("erroor")  # TODO Error
        type = self.symbol_table[var].type
        index = self.interpreter_node(children)
        print('indexing', type, index)
        if not isinstance(index, list) and index.type.find('m') == -1 and index.type.find('v') == -1:
            return self.symbol_table[var].value[index.value]
        elif isinstance(index, Variable) and index.type.find('m') != -1 and type.find('m') != -1:
            m = len(self.symbol_table[var].value)
            n = len(self.symbol_table[var].value[0])
            value = index.value
            check, m_, n_ = self.check_bool_matrix(index, m, n)
            if not check:
                print('BAD BOOL MATRIX')
            res = [[] for j in range(m_)]
            for i in range(m):
                for j in range(n):
                    if value[i][j].value:
                        res[i].append(self.symbol_table[var].value[i][j])
            return Variable(type, res)
        elif isinstance(index, Variable) and index.type.find('v') != -1 and type.find('v') != -1:
            m = len(self.symbol_table[var].value)
            value = index.value
            check = self.check_bool_vector(index, m)
            if not check:
                print('BAD BOOL VECTOR')
            res = []
            for i in range(m):
                if value[i].value:
                    res.append(self.symbol_table[var].value[i])
            return Variable(type, res)
        else:
            if isinstance(index[0], Variable) and isinstance(index[1], Variable):
                if index[0].type == index[1].type:
                    return self.symbol_table[var].value[index[0].value][index[1].value]
            elif type.find('m') != -1:  # indexing for matrix
                if isinstance(index[0], Variable) and (index[1] == ':' or index[1] == ','):
                    if index[0].type.find('v') == -1 and index[0].type.find('m') == -1:
                        res = []
                        index[0] = self.check_var('int', index[0])
                        m = self.symbol_table[var].value
                        for i in range(len(m)):
                            res.append(m[i][index[0].value])
                        type_ = 'v' + type.split('m')[1]
                        return Variable(type_, res)
                    elif index[0].type.find('vint') != -1:
                        index[0] = self.check_vector('vint', index[0])
                        value = index[0].value
                        res = [[] for i in range(len(value))]
                        m = self.symbol_table[var].value
                        for j in range(len(value)):
                            for i in range(len(m)):
                                res[j].append(m[i][value[j].value])
                        return Variable(type, res)
                    elif index[0].type.find('vbool') != -1:
                        m = self.symbol_table[var].value
                        if len(index[0].value) != len(m):
                            print("ERRROR")  # TODO ERROR
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
                        m = self.symbol_table[var].value
                        for i in range(len(m)):
                            res.append(m[index[1].value][i])
                        type_ = 'v' + type.split('m')[1]
                        return Variable(type_, res)
                    elif index[1].type.find('vint') != -1:
                        index[1] = self.check_vector('vint', index[1])
                        value = index[1].value
                        res = [[] for i in range(len(value))]
                        m = self.symbol_table[var].value
                        for j in range(len(value)):
                            for i in range(len(m)):
                                res[j].append(m[value[j].value][i])
                        return Variable(type, res)
                    elif index[1].type.find('vbool') != -1:
                        m = self.symbol_table[var].value
                        if len(index[1].value) != len(m):
                            print("ERRROR")  # TODO ERROR
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
                    print('ERRORRR index')

    def check_bool_matrix(self, var, m, n):
        type = var.type
        value = var.value
        if type.find('m') == -1:
            print('ERROR_matrix')
            return
        if len(value) != m or len(value[0]) != n:
            print('Erroorr in size')
            return
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
        return False

    def check_bool_vector(self, var, n):
        type = var.type
        value = var.value
        if type.find('v') == -1:
            print('ERROR_vector')
            return
        if len(value) != n:
            print('Erroorr in size')
            return
        k = 0
        for i in range(n):
            if value[i].value:
                k += 1
        if k > 1:
            return True
        else:
            return False


if __name__ == '__main__':
    i = Interpreter(MyParser, TypeConverser())
    prog = open('test1.txt', 'r').read()
    m = MyParser()
    tree, f = m.parse(prog)
    i.interpreter_node(tree)
    for k, v in i.symbol_table.items():
        print(k, v)
